# reference/ — Ground Truth

This directory holds raw, immutable source data: CRM exports, the P&L report, Relay bank statements, and sourced overhead contract figures. **Never edited.** If a figure here looks wrong, that's a finding to raise with the owner, not something to correct in place — corrections flow from here into derived docs (`CONTEXT.md`, the strategy files, the model), never the other way.

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

## Canonical record & change protocol

This table is the **canonical** repo record of the Relay account map. It is also restated, as context, in `CONTEXT.md`'s Relay line. If the account structure ever changes: update this table and `CONTEXT.md`'s Relay line — the two live copies — and add a **new** `HISTORY.md` entry. Never edit H-026 or any past entry; H-026 is a frozen 2026-07-05 snapshot, not a live copy.
