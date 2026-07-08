# Revenue Ledger — Standing Update Procedure

## Why a full re-export and re-parse, never an incremental delta

Homeworks invoice records are mutable — invoices get edited and back-dated after the fact. An incremental ("just append the new invoices") update would silently miss edits to *prior* invoices and drift from source over time. A full re-export and full re-parse is self-healing: every run reconstructs the ledger from scratch against current Homeworks state, so there is nothing to drift. The parse is cheap (a few seconds), so there is no cost to always doing it the expensive-but-correct way.

## Steps

1. Export all invoices from Homeworks as one PDF.
2. Save it as `reference/invoices_<YYYY-MM>_<YYYY-MM>.pdf`, dated by the coverage period. **Never overwrite a prior snapshot** — each export is its own immutable raw source (see `reference/README.md`).
3. Run:
   ```
   python model/parse_invoices.py --expect-window <start> <end> <homeworks_billed_total>
   ```
   (Omit the path argument to use the newest `reference/invoices_*.pdf` automatically, or pass a specific PDF path as the first argument.)
4. If any reconciliation check fails, **stop — do not commit.** The script prints expected vs. actual for the failing check(s).
5. Review `git diff` on `model/data/revenue-invoices.csv` and `model/data/revenue-line-items.csv`. This diff *is* the period's revenue report — new invoices, and any edits Homeworks silently made to prior ones.
6. Commit.

## Cadence

Run at each biweekly check-in. No separate ritual — it's part of the regular cadence, not an extra task.

## KPI to watch: bundled-line share of gross

As of 2026-07-06 (H-036), **56.6%** of gross ($15,795.85 of $27,891.65) sits in bundled service lines ("General Maintenance," "Lawn Care," "Lawn Maintenance") rather than a specific catalog service. This should trend **toward zero** as Follow-Up #13 (line-item billing going forward) takes effect — it's the direct measure of whether that billing-practice fix is actually happening in practice, invoice by invoice.
