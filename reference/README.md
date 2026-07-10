# reference/ — Ground Truth

This directory holds only **immutable raw sources**: CRM exports, the P&L report, Relay bank statements, invoice PDFs, and sourced overhead contract figures. Everything here is appended, never altered, and never regenerated — nothing in `reference/` is script output. If a figure here looks wrong, that's a finding to raise with the owner, not something to correct in place — corrections flow from here into derived docs (`CONTEXT.md`, the strategy files, `model/data/`), never the other way.

Script-regenerated derivatives (data extracted and reconciled from these raw sources) live in `model/data/` instead — see that directory's contents, `reference/REVENUE-UPDATE.md` for the revenue ledger's update procedure, and `reference/CATALOG-UPDATE.md` for the service catalog's.

## Relay account map

Confirmed by the owner, 2026-07-05 (see `HISTORY.md` H-026):

| Account # | Role | Status |
| --- | --- | --- |
| 8735 | Income | Active |
| 3549 | OpEx | Active |
| 3550 | Reserve | $0 across all 17 months of statements |
| 8737 | Taxes | $0 across all 17 months of statements |
| 8736 | Owner's Comp | Deleted in Relay, 2026-07-05. $0 across all 17 months of statements. |

The `Relay YYYY-MM-DD #NNNN.csv` (or `Relay (Partial) YYYY-MM-DD #NNNN.csv`) files are named by account number. Statements for 3550, 8737, and 8736 are retained even though they're empty — they are the audit substantiation for H-026's $0-balance claim, not dead weight to prune.

## Revenue ledger source

- `invoices_2025-06_2026-06.pdf` — source. 68 invoices, Jun 2025–Jun 2026, as issued. Immutable; never edited or regenerated.

The extracted, reconciled revenue ledgers (`revenue-invoices.csv`, `revenue-line-items.csv`) are **script-regenerated derivatives**, not raw sources, so they live in `model/data/` — not here — and are overwritten only by `model/parse_invoices.py`, never by hand (see `HISTORY.md` H-035 and `reference/REVENUE-UPDATE.md`).

## Payroll journal exports

- `tupelo-landscaping-llc-payroll-summary-2025-04-11-to-2026-04-11.csv` — Gusto "Payroll Journal Report" export, per-employee/per-pay-period detail (hours, rate, gross earnings, employee/employer taxes, net pay), covering pay days 2025-04-11 through 2026-04-11.
- `tupelo-landscaping-llc-payroll-summary-2026-04-11-to-2026-07-09.csv` — the same report type, covering pay days 2026-04-11 through 2026-07-09. Confirmed directly (not assumed): the two files cleanly abut with zero overlapping pay days — the shared "2026-04-11" boundary in both filenames is the report-generation cutoff, not a duplicated period.

Both are owner-supplied, immutable raw sources — filed here verbatim, byte-identical to the originals. **Gusto only exports a rolling window (roughly one year) at a time**, so future pulls will periodically be needed to keep coverage current, the same structural situation the Relay statements and the service catalog are already in.

**Not given the dated-snapshot + refresh-procedure treatment (`CATALOG-UPDATE.md`/`REVENUE-UPDATE.md`-style) in this pass, and that's a deliberate choice, not an oversight.** Those procedures exist because their data actively feeds a script-regenerated derivative in `model/data/` on a standing cadence (`parse_invoices.py`, the catalog snapshot pointer). Payroll data doesn't yet feed anything — whether and how it becomes a ledger source is an explicit, separate, deferred decision (see `CONTEXT.md`). Writing a refresh procedure now would be designing an update cadence for a pipeline that doesn't exist yet. Revisit this the same session that decision is made, not before.

## Service catalog

**Active snapshot: `service-catalog-2026-07-09.csv`** (22 rows: `Name, Rate Charged to Client, Tax1 %, Tax2 %, Category, Description`; saved verbatim from the Homeworks "Items and Services" export, including its trailing `null` row — not cleaned). This pointer line is the one piece of catalog-tracking data that is allowed to change in place; see `reference/CATALOG-UPDATE.md` for the refresh procedure and the reasoning for using an explicit pointer rather than glob-latest.

`model/parse_invoices.py`'s fail-closed gate reads valid catalog names from the active snapshot named above — never a hardcoded list.

**Packages (unbilled):** `service-packages-2026-07-09.csv` transcribes the two Package definitions (`General Maintenance`, `Lawn Care`) from Homeworks' "Packages" tab, owner-confirmed 2026-07-09 by screenshot. As of this snapshot, the Packages feature has **never been used to bill an invoice** — it is a distinct mechanism from the informal `General Maintenance` / `Lawn Care` / `Lawn Maintenance` bundle labels already present as literal invoice text in `model/data/revenue-line-items.csv`. Same names, different mechanism — see `reference/CATALOG-UPDATE.md`'s "Packages feature vs. bundle labels" section before conflating the two in any file.

Item-vs-service classification (which of the 22 catalog rows are billable materials vs. labor) lives in `model/data/catalog-type-map.csv` — a script-input derivative, not a raw source, so it's in `model/data/` rather than here.

## Canonical record & change protocol

This table is the **canonical** repo record of the Relay account map. It is also restated, as context, in `CONTEXT.md`'s Relay line. If the account structure ever changes: update this table and `CONTEXT.md`'s Relay line — the two live copies — and add a **new** `HISTORY.md` entry. Never edit H-026 or any past entry; H-026 is a frozen 2026-07-05 snapshot, not a live copy.
