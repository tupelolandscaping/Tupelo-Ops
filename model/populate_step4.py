#!/usr/bin/env python3
"""Populate overhead, materials, and capital ledger events (Sequencing Step 4).

Usage:
    python model/populate_step4.py

Labor is no longer owned by this script -- see model/populate_labor_from_payroll.py,
which rebuilds model/data/ledger-labor.csv from real Gusto payroll data
(Sequencing Step 5, Part 2). The synthetic ESTIMATE labor generator that used
to live here (2-person, 50/50 split, $25/$20 rates, per D2) has been removed;
D2's original framing is preserved in CONTEXT.md as a forward-looking
projection-layer assumption only, not a source of historical actuals.

Overhead: appends real, dated ACTUAL rows to model/data/ledger-overhead.csv on
top of the 32 Stripe fee rows already there (untouched) -- Gusto's FEE line and
General Liability ("Simply Business") at their real, varying historical Relay
amounts; Workers' Comp as one lump-sum row; the merged Copilot->Homeworks CRM
line; Squarespace's one confirmed month. Commercial Auto and equipment
maintenance stay BLOCKED with no row, per Section 6 item I / fixed-overhead.md.
Settled Spend-side rows that were later reversed by a RETURNED Receive (a
bounced transaction that still shows SETTLED on the Spend side) are excluded
before any of the above is built -- see match_payments.exclude_reversed_spend
and H-048, which found two Gusto FEE charges wrongly booked as ACTUAL this way.

Materials: writes model/data/ledger-materials.csv with a single BLOCKED $0
placeholder row, per D1.

Capital: writes model/data/ledger-capital.csv with the chainsaw purchase and
the owner's truck/insurance-advance reimbursement, both ACTUAL. Xavier, the
owner's remaining truck-debt, and the H-025 truck bookkeeping entry are
deliberately absent -- they stay projection-layer-only / excluded entirely,
per existing decisions (model/PHASE7-PLAN.md Section 3(c)).

Re-running this script is safe: it regenerates ledger-materials.csv and
ledger-capital.csv from scratch (nothing else writes to them yet), and
replaces only the categories it's responsible for in ledger-overhead.csv,
leaving the Stripe fee rows (from match_payments.py) and the employer-
payroll-tax-burden rows (from populate_labor_from_payroll.py) alone.
"""
import csv
import sys
from datetime import date

sys.path.insert(0, "model")
import match_payments as mp  # noqa: E402

LEDGER_FIELDS = [
    "date", "type", "event", "category", "subcategory", "customer",
    "quantity", "unit_rate", "amount", "status", "source",
]
LEDGER_OVERHEAD_PATH = "model/data/ledger-overhead.csv"
LEDGER_MATERIALS_PATH = "model/data/ledger-materials.csv"
LEDGER_CAPITAL_PATH = "model/data/ledger-capital.csv"

MATERIALS_START = date(2025, 4, 8)

# Overhead (category, subcategory) pairs this script owns in ledger-overhead.csv
# -- anything else already present (the Stripe fee rows, and the
# employer-payroll-tax-burden rows from populate_labor_from_payroll.py, which
# also use category="Gusto" but a different subcategory) is preserved
# untouched. Matching on category alone would wrongly delete those rows.
OWNED_OVERHEAD_PAIRS = {
    ("Gusto", "payroll-provider-fee"),
    ("General Liability Insurance", "monthly-premium"),
    ("Workers Comp Insurance", "annual-premium"),
    ("Homeworks (CRM)", "crm-subscription"),
    ("Squarespace", "website-hosting"),
}


def write_ledger(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def read_ledger(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def build_overhead_rows(spend):
    rows = []

    # Gusto FEE -- the $127/mo (currently) contract-fee line, distinct from
    # NET/TAX payroll disbursements. Real, varying historical amounts.
    fee_rows = sorted([r for r in spend if r["payee"] == "GUSTO" and r["reference"].startswith("FEE")],
                       key=lambda x: x["date"])
    for r in fee_rows:
        amt = -r["amount"]
        rows.append({
            "date": r["date"], "type": "overhead", "event": "", "category": "Gusto",
            "subcategory": "payroll-provider-fee", "customer": "",
            "quantity": "1", "unit_rate": f"{amt:.2f}", "amount": f"{amt:.2f}",
            "status": "ACTUAL", "source": f"{r['source_file']}; {r['reference']}",
        })

    # General Liability -- billed through "Simply Business". Real, varying
    # historical amounts; current rate ($33.75) only holds from Nov 2025 on.
    gl_rows = sorted([r for r in spend if r["payee"] == "Simply Business"], key=lambda x: x["date"])
    for r in gl_rows:
        amt = -r["amount"]
        rows.append({
            "date": r["date"], "type": "overhead", "event": "", "category": "General Liability Insurance",
            "subcategory": "monthly-premium", "customer": "",
            "quantity": "1", "unit_rate": f"{amt:.2f}", "amount": f"{amt:.2f}",
            "status": "ACTUAL", "source": f"{r['source_file']}; payee 'Simply Business'",
        })

    # Workers' Comp -- one confirmed lump-sum payment.
    wc_rows = [r for r in spend if r["payee"] == "Employers Insura" and abs(-r["amount"] - 544.00) < 0.01]
    for r in wc_rows:
        amt = -r["amount"]
        rows.append({
            "date": r["date"], "type": "overhead", "event": "", "category": "Workers Comp Insurance",
            "subcategory": "annual-premium", "customer": "",
            "quantity": "1", "unit_rate": f"{amt:.2f}", "amount": f"{amt:.2f}",
            "status": "ACTUAL", "source": f"{r['source_file']}; {r['reference']}",
        })

    # Copilot -> Homeworks: owner-confirmed same vendor, renamed. Copilot at
    # $139/mo (Jun 2025-May 2026), then the Homeworks Growth-plan $299/mo rate.
    # NOTE: only the $299.00 charge (2026-06-25) is the base-rate debit; the
    # two other Homeworks charges ($25.47 on 2026-06-20, $77.16 on 2026-07-02)
    # are separate, still-unexplained ancillary charges and are NOT included
    # here -- see the flagged discrepancy in HISTORY.md/chat: the "first
    # Homeworks-rate debit lands 2026-07-02" framing does not match what the
    # data shows (it's 2026-06-25, still on Copilot's ~25th-of-month anchor).
    copilot_rows = sorted([r for r in spend if r["payee"] == "Copilot"], key=lambda x: x["date"])
    for r in copilot_rows:
        amt = -r["amount"]
        rows.append({
            "date": r["date"], "type": "overhead", "event": "", "category": "Homeworks (CRM)",
            "subcategory": "crm-subscription", "customer": "",
            "quantity": "1", "unit_rate": f"{amt:.2f}", "amount": f"{amt:.2f}",
            "status": "ACTUAL",
            "source": f"{r['source_file']}; payee 'Copilot' -- prior name for Homeworks, per owner",
        })
    homeworks_299 = [r for r in spend if r["payee"] == "HOMEWORKS SOFTWARE" and abs(-r["amount"] - 299.00) < 0.01]
    for r in homeworks_299:
        amt = -r["amount"]
        rows.append({
            "date": r["date"], "type": "overhead", "event": "", "category": "Homeworks (CRM)",
            "subcategory": "crm-subscription", "customer": "",
            "quantity": "1", "unit_rate": f"{amt:.2f}", "amount": f"{amt:.2f}",
            "status": "ACTUAL",
            "source": (f"{r['source_file']}; payee 'HOMEWORKS SOFTWARE' -- first debit at the new "
                       "Growth-plan rate, still on the pre-existing ~25th-of-month billing anchor, "
                       "not shifted to the 1st"),
        })

    # Squarespace -- one confirmed month; earlier months are an acknowledged
    # gap, not backfilled.
    sqsp_rows = [r for r in spend if r["payee"] == "Squarespace"]
    for r in sqsp_rows:
        amt = -r["amount"]
        rows.append({
            "date": r["date"], "type": "overhead", "event": "", "category": "Squarespace",
            "subcategory": "website-hosting", "customer": "",
            "quantity": "1", "unit_rate": f"{amt:.2f}", "amount": f"{amt:.2f}",
            "status": "ACTUAL", "source": f"{r['source_file']}; payee 'Squarespace'",
        })

    rows.sort(key=lambda r: r["date"])
    return rows


def build_materials_rows():
    return [{
        "date": MATERIALS_START.isoformat(), "type": "materials", "event": "",
        "category": "materials", "subcategory": "unattributed", "customer": "",
        "quantity": "1", "unit_rate": "0.00", "amount": "0.00", "status": "BLOCKED",
        "source": ("CONTEXT.md D1 -- no per-job attributable materials/fuel data until Job "
                   "Costing activates; excludes the $422.26 Home Depot order and other Home "
                   "Depot spend, held out pending Follow-Up #7 (whole-order vs. line-item "
                   "expense convention)"),
    }]


def build_capital_rows(spend):
    rows = []
    chainsaw = [r for r in spend if r["payee"] == "USAA CLASSIC CHECKING"
                and abs(-r["amount"] - 408.00) < 0.01]
    for r in chainsaw:
        amt = -r["amount"]
        rows.append({
            "date": r["date"], "type": "capital", "event": "", "category": "equipment",
            "subcategory": "chainsaw", "customer": "",
            "quantity": "1", "unit_rate": f"{amt:.2f}", "amount": f"{amt:.2f}",
            "status": "ACTUAL", "source": f"{r['source_file']}; {r['reference']}",
        })

    reimbursement = [r for r in spend if r["payee"] == "USAA CLASSIC CHECKING"
                     and abs(-r["amount"] - 2200.00) < 0.01]
    for r in reimbursement:
        amt = -r["amount"]
        rows.append({
            "date": r["date"], "type": "capital", "event": "", "category": "owner-reimbursement",
            "subcategory": "truck-and-insurance-advance", "customer": "",
            "quantity": "1", "unit_rate": f"{amt:.2f}", "amount": f"{amt:.2f}",
            "status": "ACTUAL",
            "source": (f"{r['source_file']}; {r['reference']} -- ONE combined transaction "
                       "matching the full $2,200 ($1,000 insurance + $1,200 truck) repayment "
                       "total exactly; no separate ~$1,000/~$1,200 transactions were found in "
                       "Relay despite searching the full history"),
        })
    return rows


def main():
    raw_rows, deduped_rows, dup_groups = mp.load_relay_rows()
    spend_all = [r for r in deduped_rows if r["txn_type"] in ("Spend", "Spend-transfer") and r["status"] == "SETTLED"]
    spend, excluded_reversed = mp.exclude_reversed_spend(spend_all, deduped_rows)
    print(f"[filter] {len(spend_all)} settled Spend rows -> {len(excluded_reversed)} excluded as "
          f"bounced-then-returned (never actually cleared) -> {len(spend)} kept")
    for r in excluded_reversed:
        print(f"    excluded: {r['date']}  {r['payee']}  ${r['amount']:.2f}  ref={r['reference'][:60]}")

    new_overhead_rows = build_overhead_rows(spend)
    existing_overhead = read_ledger(LEDGER_OVERHEAD_PATH)
    kept_overhead = [r for r in existing_overhead
                     if (r["category"], r["subcategory"]) not in OWNED_OVERHEAD_PAIRS]
    write_ledger(LEDGER_OVERHEAD_PATH, kept_overhead + new_overhead_rows)
    print(f"[overhead] {len(kept_overhead)} pre-existing rows kept (Stripe fees + "
          f"employer-payroll-tax-burden) + {len(new_overhead_rows)} new rows written")

    materials_rows = build_materials_rows()
    write_ledger(LEDGER_MATERIALS_PATH, materials_rows)
    print(f"[materials] {len(materials_rows)} row written (BLOCKED placeholder)")

    capital_rows = build_capital_rows(spend)
    write_ledger(LEDGER_CAPITAL_PATH, capital_rows)
    print(f"[capital] {len(capital_rows)} row(s) written")
    if len(capital_rows) < 2:
        print("  WARNING: expected chainsaw + reimbursement rows; got fewer -- check matches above")

    # Reconciliation gates
    print()
    latest_month_rows = [r for r in new_overhead_rows if r["date"] >= "2026-06-01"]
    print(f"[gate] overhead rows dated 2026-06 or later ({len(latest_month_rows)} rows):")
    for r in latest_month_rows:
        print(f"    {r['date']}  {r['category']:28s} ${float(r['amount']):8.2f}  {r['status']}")


if __name__ == "__main__":
    main()
