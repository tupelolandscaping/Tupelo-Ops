# reference/ — Ground Truth

This directory holds only **immutable raw sources**: CRM exports, the P&L report, Relay bank statements, invoice PDFs, and sourced overhead contract figures. Everything here is appended, never altered, and never regenerated — nothing in `reference/` is script output. If a figure here looks wrong, that's a finding to raise with the owner, not something to correct in place — corrections flow from here into derived docs (`CONTEXT.md`, the strategy files, `model/data/`), never the other way.

Script-regenerated derivatives (data extracted and reconciled from these raw sources) live in `model/data/` instead — see that directory's contents and `reference/REVENUE-UPDATE.md` for the revenue ledger's update procedure.

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

## Canonical record & change protocol

This table is the **canonical** repo record of the Relay account map. It is also restated, as context, in `CONTEXT.md`'s Relay line. If the account structure ever changes: update this table and `CONTEXT.md`'s Relay line — the two live copies — and add a **new** `HISTORY.md` entry. Never edit H-026 or any past entry; H-026 is a frozen 2026-07-05 snapshot, not a live copy.
