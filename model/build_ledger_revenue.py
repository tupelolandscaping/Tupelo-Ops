#!/usr/bin/env python3
"""Regenerate model/data/ledger-revenue.csv's invoice-side rows (Process/tooling
reliability pass, H-051).

Usage:
    python model/build_ledger_revenue.py

Closes a real pipeline gap found in the "what's left" review: model/parse_invoices.py
regenerates model/data/revenue-invoices.csv and model/data/revenue-line-items.csv from
a fresh Homeworks PDF export, but nothing regenerated ledger-revenue.csv's `event=invoice`
rows (category `service` / `BLOCKED — unmapped` / `surcharge` / `tip` -- 319 of its 377
rows) from that fresh parse. model/match_payments.py only ever appends/refreshes
`event=payment` rows on top, explicitly leaving invoice-side rows untouched by design --
so a routine revenue refresh silently left the actual ledger stale.

Run order: model/parse_invoices.py -> this script -> model/match_payments.py -> ...
(see model/refresh_all.py for the full pipeline). This script is a natural continuation
of parse_invoices.py's job (turn the CRM export into ledger form), distinct from
match_payments.py's job (match bank deposits against invoices) -- keeping them separate
scripts matches this repo's established one-script-one-job pattern (e.g.
model/populate_step4.py vs. model/populate_labor_from_payroll.py owning disjoint ledger
categories) and keeps the responsibility for "who builds invoice-side rows" unambiguous
and discoverable, rather than buried inside a differently-scoped script -- which is
exactly how the original gap went unnoticed.

Transformation (reverse-engineered from the existing ledger and verified byte-for-byte
identical against the current 319 invoice-side rows before this script was written,
0 mismatches across all rows):
  - One row per model/data/revenue-line-items.csv line item: category = "BLOCKED --
    unmapped" if is_bundle else "service"; subcategory = the mapped `service` name
    (populated even for bundle rows, e.g. "General Maintenance"); amount = line_net
    (net of surcharge -- the surcharge itself is a separate row, below); date =
    invoice_date (not service_date -- confirmed against the existing ledger).
  - One additional row per line item where line_surcharge != 0 (148 of 152 line items;
    the other 4 are the zero-surcharge lines documented in Follow-Up #16): category =
    "surcharge", subcategory = the same mapped `service` name, amount = line_surcharge.
  - One row per model/data/revenue-invoices.csv invoice where tip != 0 (19 of 68
    invoices): category = "tip", subcategory blank, amount = tip.

Fail-closed gate: the built rows' total must equal REVENUE_INVOICE_ANCHOR (the same
$28,316.57 anchor model/build_model.py's Reconciliation tab checks against, H-043) to
the penny. This is not a redundant re-check of build_model.py's Check 1 -- that check
verifies whatever is currently sitting in the ledger; this one verifies the fresh
transformation from source before it's written, so a bug in this script's own logic
cannot silently corrupt the ledger and still pass Check 1 by coincidence.

Re-running this script is safe and idempotent: identical input CSVs produce identical
output, sorted in a fixed, deterministic order (by date, category, subcategory,
customer, amount) so re-runs are byte-for-byte stable even though dict/CSV row order
from the source files is not guaranteed to be. It preserves whatever `event=payment`
rows currently exist in ledger-revenue.csv untouched (mirroring match_payments.py's own
`kept_revenue = [r for r in existing_revenue if r["event"] != "payment"]` pattern in
reverse), so running it out of order relative to match_payments.py cannot destroy the
other script's rows either way.
"""
import csv

REVENUE_LINE_ITEMS_PATH = "model/data/revenue-line-items.csv"
REVENUE_INVOICES_PATH = "model/data/revenue-invoices.csv"
LEDGER_REVENUE_PATH = "model/data/ledger-revenue.csv"

LEDGER_FIELDS = [
    "date", "type", "event", "category", "subcategory", "customer",
    "quantity", "unit_rate", "amount", "status", "source",
]

# Same anchor model/build_model.py's Reconciliation tab Check 1 verifies against
# (H-043: $27,891.65 gross service/materials revenue + $424.92 tips). Duplicated
# here, not imported, matching this repo's existing pattern of small shared
# constants living per-script rather than in a shared module (e.g. LEDGER_FIELDS).
REVENUE_INVOICE_ANCHOR = 28316.57


def read_ledger(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def write_ledger(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def mkrow(date, category, subcategory, customer, amount, status, source):
    amt = f"{float(amount):.2f}"
    return {
        "date": date, "type": "revenue", "event": "invoice",
        "category": category, "subcategory": subcategory, "customer": customer,
        "quantity": "1", "unit_rate": amt, "amount": amt,
        "status": status, "source": source,
    }


def build_invoice_rows():
    line_items = read_ledger(REVENUE_LINE_ITEMS_PATH)
    invoices = read_ledger(REVENUE_INVOICES_PATH)

    rows = []
    for r in line_items:
        category = "BLOCKED — unmapped" if r["is_bundle"].upper() == "TRUE" else "service"
        rows.append(mkrow(r["invoice_date"], category, r["service"], r["customer"],
                           r["line_net"], r["status"], r["source"]))
        if float(r["line_surcharge"]) != 0:
            rows.append(mkrow(r["invoice_date"], "surcharge", r["service"], r["customer"],
                               r["line_surcharge"], r["status"], r["source"]))

    for r in invoices:
        if float(r["tip"]) != 0:
            rows.append(mkrow(r["invoice_date"], "tip", "", r["customer"],
                               r["tip"], r["status"], r["source"]))

    rows.sort(key=lambda r: (r["date"], r["category"], r["subcategory"], r["customer"], r["amount"]))
    return rows, len(line_items), len(invoices)


def main():
    invoice_rows, n_line_items, n_invoices = build_invoice_rows()
    print(f"[parse] {n_line_items} line items, {n_invoices} invoices")

    total = sum(float(r["amount"]) for r in invoice_rows)
    if abs(total - REVENUE_INVOICE_ANCHOR) >= 0.01:
        print(f"GATE FAILED: built invoice-side rows sum to ${total:,.2f}, "
              f"expected ${REVENUE_INVOICE_ANCHOR:,.2f} (H-043 anchor) -- "
              f"off by ${total - REVENUE_INVOICE_ANCHOR:,.2f}. Not writing the ledger.")
        raise SystemExit(1)

    try:
        existing = read_ledger(LEDGER_REVENUE_PATH)
    except FileNotFoundError:
        existing = []
    kept_payments = [r for r in existing if r["event"] == "payment"]

    write_ledger(LEDGER_REVENUE_PATH, invoice_rows + kept_payments)

    by_cat = {}
    for r in invoice_rows:
        by_cat.setdefault(r["category"], [0, 0.0])
        by_cat[r["category"]][0] += 1
        by_cat[r["category"]][1] += float(r["amount"])
    print(f"[build] {len(invoice_rows)} invoice-side rows written, sum ${total:,.2f} "
          f"(gate passed, matches ${REVENUE_INVOICE_ANCHOR:,.2f} anchor exactly):")
    for cat, (n, amt) in sorted(by_cat.items()):
        print(f"    {cat}: {n} rows, ${amt:,.2f}")
    print(f"[preserve] {len(kept_payments)} existing event=payment row(s) kept untouched")


if __name__ == "__main__":
    main()
