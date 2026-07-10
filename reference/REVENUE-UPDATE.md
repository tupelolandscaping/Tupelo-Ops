# Revenue Ledger — Standing Update Procedure

## Why a full re-export and re-parse, never an incremental delta

Homeworks invoice records are mutable — invoices get edited and back-dated after the fact. An incremental ("just append the new invoices") update would silently miss edits to *prior* invoices and drift from source over time. A full re-export and full re-parse is self-healing: every run reconstructs the ledger from scratch against current Homeworks state, so there is nothing to drift. The parse is cheap (a few seconds), so there is no cost to always doing it the expensive-but-correct way.

## Steps

1. Export all invoices from Homeworks as one PDF.
2. Save it as `reference/invoices_<YYYY-MM>_<YYYY-MM>.pdf`, dated by the coverage period. **Never overwrite a prior snapshot** — each export is its own immutable raw source (see `reference/README.md`).
3. **Confirm the service catalog is current** (per H-038, the parser's fail-closed gates now validate against the catalog, not a hardcoded list — see `reference/CATALOG-UPDATE.md`): check whether Homeworks' Items/Services or Packages have changed since the active snapshot named in `reference/README.md`. If so, refresh the catalog snapshot **first**, following `reference/CATALOG-UPDATE.md`. This is a prerequisite check-in step now, not just the invoice re-export — an unrefreshed catalog means new or renamed services will correctly fail the recognized-header gate rather than silently misclassify.
4. Run:
   ```
   python model/parse_invoices.py --expect-window <start> <end> <homeworks_billed_total>
   ```
   (Omit the path argument to use the newest `reference/invoices_*.pdf` automatically, or pass a specific PDF path as the first argument.)
5. If any reconciliation check fails, **stop — do not commit.** The script prints expected vs. actual for the failing check(s) — including, per H-038, an unrecognized-header failure (a `service_raw` absent from the active catalog snapshot, `model/data/service-name-map.csv`, and the bundle set) or an unclassified-kind failure (a mapped `service` absent from `model/data/catalog-type-map.csv`).
6. Run:
   ```
   python model/build_ledger_revenue.py
   ```
   **This step is required and easy to forget** (a real gap found and closed in H-051): `parse_invoices.py` only regenerates `model/data/revenue-invoices.csv` and `model/data/revenue-line-items.csv` — it does not touch `model/data/ledger-revenue.csv`. Without this step, the actual ledger the model builds from stays stale even though the freshly-parsed CSVs look current. This script rebuilds `ledger-revenue.csv`'s invoice/surcharge/tip rows from those CSVs and fails closed (`GATE FAILED`, nonzero exit, ledger not written) if the built total doesn't match the known revenue anchor to the penny. It preserves any existing `event=payment` rows untouched — running `model/match_payments.py` before or after this step doesn't matter.
7. Review `git diff` on `model/data/revenue-invoices.csv`, `model/data/revenue-line-items.csv`, and `model/data/ledger-revenue.csv`. This diff *is* the period's revenue report — new invoices, and any edits Homeworks silently made to prior ones.
8. Commit.

**Or, simpler:** run `python model/refresh_all.py`, which runs this step (and the rest of the data-refresh pipeline) in the correct order automatically and halts on any failure — see `README.md`'s "Model data-refresh pipeline" section. Steps 4–6 above are what that orchestrator runs for the revenue portion specifically; do them by hand only if you want to refresh revenue alone without touching labor/overhead/materials/capital.

## Cadence

Run at each biweekly check-in. No separate ritual — it's part of the regular cadence, not an extra task.

## What a re-parse produces and gates on

**Bundled-line share of gross (KPI to watch).** As of 2026-07-06 (H-036), **56.6%** of gross ($15,795.85 of $27,891.65) sits in bundled service lines ("General Maintenance," "Lawn Care," "Lawn Maintenance") rather than a specific catalog service. This should trend **toward zero** as Follow-Up #13 (line-item billing going forward) takes effect — it's the direct measure of whether that billing-practice fix is actually happening in practice, invoice by invoice.

**Item vs. service classification (per H-038).** Every non-bundle line item in `model/data/revenue-line-items.csv` now carries a `kind` column (`item` for billable materials/goods, `service` for labor), looked up from `model/data/catalog-type-map.csv` against the line's mapped `service` name. Bundle rows (`is_bundle=TRUE`) carry no `kind` — a bundled visit can mix labor and materials and can't be classified as one until Follow-Up #13 decomposes it.

**Two fail-closed gates now depend on the catalog snapshot, not a hardcoded list.** `model/parse_invoices.py` reads valid catalog names from the snapshot pointed to in `reference/README.md` (H-038 replaced the prior hardcoded `ALREADY_CANONICAL_SERVICES` set with this). A `service_raw` header not found there, in `model/data/service-name-map.csv`, or in the bundle set fails the recognized-header gate. Separately, any mapped `service` with no entry in `model/data/catalog-type-map.csv` fails the kind-classification gate — this is what catches a genuinely new catalog item (or a catalog refresh you forgot to also update `catalog-type-map.csv` for) before it silently ships with a blank `kind`.

See `HISTORY.md` H-038 for the full record of this change.
