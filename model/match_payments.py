#!/usr/bin/env python3
"""Match Relay bank deposits to invoices and populate revenue payment events.

Usage:
    python model/match_payments.py

Reads every reference/Relay*.csv statement, deduplicates rows that appear in
more than one file because of overlapping export windows, and classifies each
settled Receive/Receive-transfer row into one of:
  - tier 1  "exact"       -- Reference field cites an invoice number that
                             matches model/data/revenue-invoices.csv exactly
  - tier 2  "amount-lag"  -- amount + payee match exactly one open invoice
            "batch"       -- amount matches the sum of 2-3 open invoices
            "unmatched-*" -- no invoice or invoice-combination match found
  - tier 3  "aggregated"  -- Stripe settlements, no per-customer attribution
                             possible from bank data alone (Finding 3). Per-
                             charge attribution IS possible via a separate
                             source (reference/stripe-balance-history-*.csv's
                             Description/Transfer fields, H-061) but is not
                             implemented here -- deliberately deferred, see
                             CONTEXT.md Follow-Up #25 for the quantified scope
                             (32/32 rows re-attributable, 25 single-invoice +
                             7 multi-invoice batches).
  - excluded              -- internal transfers, owner cash injections,
                              payroll-tax refunds, bank verification
                              micro-deposits, vendor/corporate-card refunds

Writes `type=revenue, event=payment` rows into model/data/ledger-revenue.csv
(existing `event=invoice` rows are left untouched) and, for every Stripe
"aggregated" row, a paired `type=overhead, subcategory=payment-processing-fee`
row into model/data/ledger-overhead.csv. The payment event's own `amount` is
always the actual net deposit, never a back-computed gross (see
model/PHASE7-PLAN.md Section 3(b)).

The fee is computed two ways depending on data availability (HISTORY.md
H-062): if the payout's date+net-amount matches a payout in
reference/stripe-balance-history-*.csv, the fee is the TRUE sum of that
payout's underlying per-charge Stripe fees (each charge carries its own
$0.30 flat component, so a payout batching 2-3 charges owes more than one
flat fee) -- this is ground truth, not an estimate. Otherwise (a payout not
covered by that export) it falls back to the owner-confirmed 3.9% + $0.30
formula (Finding 7), back-solved from the net deposit assuming a single
charge -- this fallback is known to UNDERcount whenever the uncovered
payout batches more than one charge; see H-061/H-062 for the $2.56
historical undercount this caused before the balance-history export existed.

Re-running this script is safe: it replaces only `event=payment` rows in
ledger-revenue.csv and only Stripe-fee rows in ledger-overhead.csv, leaving
invoice/tip/surcharge rows and any other overhead rows untouched.

Exits nonzero if the classification gate fails (every settled Receive/
Receive-transfer row must resolve to a payment event or a named exclusion --
zero unclassified residual). Does not attempt the fuller per-account
balance-delta reconciliation gate; that requires Sequencing Step 4 (labor/
overhead/materials/capital population) to exist first.
"""
import csv
import glob
import re
import sys
from datetime import datetime
from itertools import combinations

RELAY_GLOB = "reference/Relay*.csv"
STRIPE_BALANCE_HISTORY_GLOB = "reference/stripe-balance-history-*.csv"
INVOICES_PATH = "model/data/revenue-invoices.csv"
LEDGER_REVENUE_PATH = "model/data/ledger-revenue.csv"
LEDGER_OVERHEAD_PATH = "model/data/ledger-overhead.csv"
LEDGER_FIELDS = [
    "date", "type", "event", "category", "subcategory", "customer",
    "quantity", "unit_rate", "amount", "status", "source",
]

STRIPE_FEE_PCT = 0.039
STRIPE_FEE_FLAT = 0.30

# Payee -> customer name, for the tier-2 amount/batch/lag matcher. Only
# payees actually observed paying by direct bank transfer with no invoice
# number cited (Findings 1, 2, and this pass's full-history extension).
PAYEE_TO_CUSTOMER = {
    "WOMEN LIFE FRE": "Women Life Freedom LLC",
    "ANACOSTIA COMMUN": "Association",
    "Martha Picarello": "Martha Picarello",
    "Joel Beauvais": "Joel Beauvais",
    "JaLane Daschke": "JaLane Daschke",
    "Katie Wheelbarger": "Katie Wheelbarger",
    "Barbara Jyachosky": "Barbara Jyachosky",
}
# Decision 5: near-miss deposits do not get fuzzy-matched to the closest
# invoice -- they get their own explicit "gap unexplained" tag instead.
NEAR_MISS_PAYEES = {"Martha Picarello", "Joel Beauvais"}

INVOICE_REF_RE = re.compile(r"invoice\s*#?\s*(\d+)", re.IGNORECASE)


def parse_date(s):
    m, d, y = s.split("/")
    return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"


def account_from_filename(fn):
    m = re.search(r"#(\d{4})\.csv$", fn)
    return m.group(1) if m else None


def is_fuller_file(fn):
    # "Relay (Partial) 2026-07-01 to 2026-07-06 #NNNN.csv" supersedes the
    # narrower "Relay (Partial) 2026-07-01 #NNNN.csv" for their shared
    # overlapping window (H-039). Generalizes to any future overlapping pull
    # named with the same " to " range convention.
    return " to " in fn


def days_between(d1, d2):
    return (datetime.strptime(d1, "%Y-%m-%d") - datetime.strptime(d2, "%Y-%m-%d")).days


def load_relay_rows():
    """Parse every Relay statement, deduplicating overlapping export windows.

    The statement's own account is always read from the filename, never from
    the in-file "Account #" column -- that column (present in 64 of 89 files,
    absent in the other 25) records a transfer's *counterparty* account, not
    the statement's own account.
    """
    raw_rows = []
    for fn in sorted(glob.glob(RELAY_GLOB)):
        acct = account_from_filename(fn)
        with open(fn, newline="", encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                if not r.get("Date", "").strip():
                    continue
                raw_rows.append({
                    "account": acct,
                    "date": parse_date(r["Date"].strip()),
                    "payee": r.get("Payee", "").strip(),
                    "txn_type": r.get("Transaction Type", "").strip(),
                    "description": r.get("Description", "").strip(),
                    "reference": r.get("Reference", "").strip(),
                    "status": r.get("Status", "").strip(),
                    "amount": float(r["Amount"].replace("+", "").replace(",", "")),
                    "balance": r.get("Balance", "").strip(),
                    "source_file": fn,
                })

    groups = {}
    for r in raw_rows:
        key = (r["account"], r["date"], r["payee"], r["txn_type"],
               r["reference"], r["amount"], r["balance"])
        groups.setdefault(key, []).append(r)

    dup_groups = sum(1 for g in groups.values() if len(g) > 1)
    deduped = [
        next((g for g in grp if is_fuller_file(g["source_file"])), grp[0])
        for grp in groups.values()
    ]
    return raw_rows, deduped, dup_groups


def exclude_reversed_spend(spend_rows, deduped_rows, window_days=3):
    """Drop any settled Spend-side row that was later reversed by a matching
    RETURNED Receive (same payee, the exact same amount, within `window_days`).

    A bounced-then-returned debit is still marked SETTLED by Relay on the
    Spend side -- only a separate, later Receive row (status=RETURNED)
    reveals that it never actually cleared. Any script booking ACTUAL rows
    from Spend-side data must exclude these, or it will book real cost for
    cash that was never actually paid out. Confirmed by H-048: two Gusto FEE
    charges (2025-05-05, 2025-05-07) were booked as ACTUAL in
    ledger-overhead.csv despite bouncing, because nothing cross-checked
    SETTLED Spend rows against RETURNED Receive rows before this fix.

    "Reversed the same transaction" is a binary fact, not an approximate
    one, so amounts are compared as exact integer cents (round(amount*100)),
    never a floating-point epsilon window -- an earlier version of this
    function used `abs(a - b) < 0.01`, which is not the same thing: it
    falsely matched a $0.08 charge against an unrelated $0.09 return (their
    difference, 0.009999999999999995 in floating point, happens to be
    just under 0.01). A real reversal always cancels the original amount
    exactly, so exact equality is both correct and sufficient.

    Returns (kept_rows, excluded_rows) -- both lists of the original dicts,
    so callers can report exactly what was dropped and why.
    """
    def cents(amount):
        return round(amount * 100)

    returned = [r for r in deduped_rows if r["status"] == "RETURNED"]
    kept, excluded = [], []
    for r in spend_rows:
        reversed_match = any(
            ret["payee"] == r["payee"]
            and cents(abs(ret["amount"])) == cents(abs(r["amount"]))
            and abs(days_between(ret["date"], r["date"])) <= window_days
            for ret in returned
        )
        (excluded if reversed_match else kept).append(r)
    return kept, excluded


def exclusion_reason(r):
    """Named, justified reasons a settled Receive row is not revenue.

    This list is broader than the original Finding 4 (internal transfers,
    USAA FSB TRNSFER, Gusto payroll) -- extending tier-4 checking to the full
    Relay history (not just the partial-July sample) surfaced four more
    categories that don't fit any of Approach A's three revenue tiers.
    """
    if r["payee"] == "Income":
        return "internal account transfer (Income->OpEx sweep)"
    if r["payee"] == "USAA FSB TRNSFER":
        return "unrelated personal/internal transfer"
    if r["payee"] == "USAA CLASSIC CHECKING" and r["reference"] == "ACH Pull":
        return "owner cash injection (personal-to-business ACH pull)"
    if r["payee"] == "GUSTO PAYROLL" and r["reference"].startswith("TAX"):
        return "payroll-tax-related refund/credit from payroll provider"
    if r["payee"] == "GUSTO" and r["reference"].startswith("INV"):
        return ('payroll-vendor credit (Gusto), not a customer invoice '
                'despite "INV" reference text')
    if r["reference"] == "ACCTVERIFY":
        return "bank account-verification micro-deposit"
    if "Corporate Card" in r["reference"] and r["description"] == "Unknown":
        return "vendor/corporate-card refund or credit"
    if r["payee"] == "United States Treasury":
        return "government tax-related refund (Form 941)"
    return None


def classify(receive_rows, invoices):
    inv_by_num = {inv["invoice"]: inv for inv in invoices}
    global_window_start = min(inv["invoice_date"] for inv in invoices)

    classified, excluded = [], []
    for r in receive_rows:
        reason = exclusion_reason(r)
        if reason:
            excluded.append({**r, "exclusion_reason": reason})
            continue
        if r["payee"] == "STRIPE":
            classified.append({**r, "tier": "aggregated", "invoice_refs": [], "customer": None})
            continue

        m = INVOICE_REF_RE.search(r["reference"])
        if m and m.group(1) in inv_by_num:
            inv = inv_by_num[m.group(1)]
            if abs(float(inv["gross"]) - r["amount"]) < 0.005:
                classified.append({**r, "tier": "exact", "invoice_refs": [m.group(1)],
                                    "customer": inv["customer"]})
                continue

        customer = PAYEE_TO_CUSTOMER.get(r["payee"])
        cust_invoices = [inv for inv in invoices if inv["customer"] == customer]
        singles = [inv for inv in cust_invoices if abs(float(inv["gross"]) - r["amount"]) < 0.005]

        if len(singles) == 1:
            inv = singles[0]
            classified.append({**r, "tier": "amount-lag", "invoice_refs": [inv["invoice"]],
                                "customer": customer,
                                "lag_days": days_between(r["date"], inv["invoice_date"])})
            continue
        if len(singles) > 1:
            classified.append({**r, "tier": "AMBIGUOUS",
                                "invoice_refs": [s["invoice"] for s in singles], "customer": customer})
            continue

        grosses = [(inv["invoice"], float(inv["gross"])) for inv in cust_invoices]
        batch = None
        for size in (2, 3):
            for combo in combinations(grosses, size):
                if abs(sum(c[1] for c in combo) - r["amount"]) < 0.01:
                    batch = combo
                    break
            if batch:
                break
        if batch:
            classified.append({**r, "tier": "batch", "invoice_refs": [c[0] for c in batch],
                                "customer": customer})
            continue

        if r["payee"] in NEAR_MISS_PAYEES:
            closest = min(cust_invoices, key=lambda inv: abs(float(inv["gross"]) - r["amount"]))
            classified.append({**r, "tier": "unmatched-nearmiss", "invoice_refs": [closest["invoice"]],
                                "customer": customer, "gap": r["amount"] - float(closest["gross"])})
        else:
            predates = r["date"] < global_window_start
            classified.append({**r, "tier": "unmatched-predates" if predates else "unmatched-investigate",
                                "customer": customer, "invoice_refs": []})

    return classified, excluded


def load_stripe_fee_lookup():
    """Sum true per-charge Stripe fees by payout, keyed on (date, net) so it
    can be matched against a Relay-side 'aggregated' row's own (date, amount).
    Returns {} if no reference/stripe-balance-history-*.csv file is present
    (the H-061/H-062 export is optional; callers must fall back cleanly).

    Deduplicates by Stripe's own `id` column (a true unique transaction ID,
    unlike Relay's rows) before summing -- required once more than one
    stripe-balance-history-*.csv file exists (H-064): a future refresh will
    routinely produce overlapping date windows against the current export,
    exactly like reference/Relay*.csv already does, and without this a
    charge or payout appearing in two files would be double-counted."""
    files = glob.glob(STRIPE_BALANCE_HISTORY_GLOB)
    if not files:
        return {}

    seen_ids = set()
    charges_by_transfer = {}
    payouts = []
    for fn in files:
        with open(fn, newline="") as f:
            for row in csv.DictReader(f):
                if row["id"] in seen_ids:
                    continue
                seen_ids.add(row["id"])
                if row["Type"] == "charge":
                    charges_by_transfer.setdefault(row["Transfer"], []).append(row)
                elif row["Type"] == "payout" and float(row["Amount"]) < 0:
                    payouts.append((row, fn))

    lookup = {}
    for p, source_fn in payouts:
        date = p["Available On (UTC)"][:10]
        net = round(abs(float(p["Net"])), 2)
        batch = charges_by_transfer.get(p["Source"], [])
        true_fee = round(sum(float(c["Fee"]) for c in batch), 2)
        lookup[(date, net)] = (true_fee, len(batch), source_fn)
    return lookup


def subcategory_for(m):
    tier = m["tier"]
    if tier == "exact":
        return f"Invoice {m['invoice_refs'][0]} [exact]"
    if tier == "amount-lag":
        return f"Invoice {m['invoice_refs'][0]} [amount-lag]"
    if tier == "batch":
        return f"Invoices {', '.join(m['invoice_refs'])} [batch]"
    if tier == "aggregated":
        return "unattributed [aggregated]"
    if tier == "unmatched-predates":
        return "unmatched — predates invoice PDF coverage window [unmatched]"
    if tier == "unmatched-investigate":
        return "unmatched — needs investigation [unmatched]"
    if tier == "unmatched-nearmiss":
        return (f"unmatched — ${abs(m['gap']):.2f} short of invoice "
                f"#{m['invoice_refs'][0]}, gap unexplained [unmatched]")
    raise ValueError(f"Unresolved tier requiring a decision before this can run: {m}")


def build_ledger_rows(classified, stripe_fee_lookup):
    payment_rows, fee_rows = [], []
    true_count = 0
    for m in classified:
        customer = m["customer"] if m["tier"] != "aggregated" else ""
        payment_rows.append({
            "date": m["date"], "type": "revenue", "event": "payment",
            "category": "payment", "subcategory": subcategory_for(m),
            "customer": customer or "", "quantity": "1",
            "unit_rate": f"{m['amount']:.2f}", "amount": f"{m['amount']:.2f}",
            "status": "ACTUAL", "source": m["source_file"],
        })
        if m["tier"] == "aggregated":
            net = m["amount"]
            key = (m["date"], round(net, 2))
            true = stripe_fee_lookup.get(key)
            if true is not None:
                fee, n_charges, source_fn = true
                true_count += 1
                source = (f"{source_fn}; true sum of {n_charges} underlying charge fee(s) "
                           "for this payout (H-062) -- supersedes the 3.9%+$0.30 "
                           "back-solved-per-day estimate this row previously carried")
            else:
                gross = (net + STRIPE_FEE_FLAT) / (1 - STRIPE_FEE_PCT)
                fee = gross - net
                source = (f"{m['source_file']}; fee computed via 3.9% + $0.30 formula, "
                           "back-solved from net deposit (no matching payout found in "
                           "reference/stripe-balance-history-*.csv) -- never used as the "
                           "payment event's own amount")
            fee_rows.append({
                "date": m["date"], "type": "overhead", "event": "",
                "category": "Stripe", "subcategory": "payment-processing-fee",
                "customer": "", "quantity": "1",
                "unit_rate": f"{fee:.2f}", "amount": f"{fee:.2f}", "status": "ACTUAL",
                "source": source,
            })
    payment_rows.sort(key=lambda r: r["date"])
    fee_rows.sort(key=lambda r: r["date"])
    print(f"[stripe-fee] {true_count}/{len(fee_rows)} fee rows use true per-charge sums "
          f"from reference/stripe-balance-history-*.csv; "
          f"{len(fee_rows)-true_count} fall back to the back-solved formula")
    return payment_rows, fee_rows


def read_ledger(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def write_ledger(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main():
    invoices = read_ledger(INVOICES_PATH)

    raw_rows, deduped_rows, dup_groups = load_relay_rows()
    print(f"[parse] {len(glob.glob(RELAY_GLOB))} Relay files, {len(raw_rows)} raw rows, "
          f"{dup_groups} duplicate groups removed -> {len(deduped_rows)} rows")

    receive = [r for r in deduped_rows
               if r["txn_type"] in ("Receive", "Receive-transfer") and r["status"] == "SETTLED"]
    returned = [r for r in deduped_rows if r["status"] == "RETURNED"]
    stripe_reversals = [r for r in deduped_rows
                        if r["payee"] == "STRIPE" and r["txn_type"] == "Spend" and r["status"] == "SETTLED"]

    classified, excluded = classify(receive, invoices)

    ambiguous = [m for m in classified if m["tier"] == "AMBIGUOUS"]
    if ambiguous:
        print(f"GATE FAILED: {len(ambiguous)} row(s) matched more than one invoice "
              "by amount -- resolve before proceeding:")
        for m in ambiguous:
            print(f"  {m['payee']} {m['date']} ${m['amount']} -> invoices {m['invoice_refs']}")
        sys.exit(1)

    # Classification gate: every settled Receive/Receive-transfer row must be
    # either a classified payment event or a named exclusion. Zero residual.
    accounted = len(classified) + len(excluded)
    if accounted != len(receive):
        print(f"GATE FAILED: {len(receive)} settled Receive/Receive-transfer rows, "
              f"but only {accounted} were classified or excluded -- "
              f"{len(receive) - accounted} unaccounted row(s).")
        sys.exit(1)

    stripe_fee_lookup = load_stripe_fee_lookup()
    payment_rows, fee_rows = build_ledger_rows(classified, stripe_fee_lookup)

    existing_revenue = read_ledger(LEDGER_REVENUE_PATH)
    kept_revenue = [r for r in existing_revenue if r["event"] != "payment"]
    write_ledger(LEDGER_REVENUE_PATH, kept_revenue + payment_rows)

    existing_overhead = read_ledger(LEDGER_OVERHEAD_PATH)
    kept_overhead = [r for r in existing_overhead
                     if not (r["category"] == "Stripe" and r["subcategory"] == "payment-processing-fee")]
    write_ledger(LEDGER_OVERHEAD_PATH, kept_overhead + fee_rows)

    print()
    print("[gate] PASSED -- every settled Receive/Receive-transfer row is either a "
          f"payment event or a named exclusion. {len(receive)} rows = "
          f"{len(classified)} classified + {len(excluded)} excluded.")
    print(f"[output] {len(payment_rows)} payment-event rows written to {LEDGER_REVENUE_PATH} "
          f"(sum(amount) = ${sum(float(r['amount']) for r in payment_rows):,.2f})")
    print(f"[output] {len(fee_rows)} Stripe fee rows written to {LEDGER_OVERHEAD_PATH} "
          f"(sum(amount) = ${sum(float(r['amount']) for r in fee_rows):,.2f})")
    print(f"[note] {len(returned)} RETURNED-status rows excluded outright (not settled cash)")
    print(f"[note] {len(stripe_reversals)} Stripe Spend-type debit(s) found, "
          "excluded from revenue events, not netted into any tier -- see CONTEXT.md Follow-Up")


if __name__ == "__main__":
    main()
