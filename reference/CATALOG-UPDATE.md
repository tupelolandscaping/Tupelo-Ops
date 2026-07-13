# Service Catalog — Standing Update Procedure

## Why a dated snapshot + explicit pointer, not "always use the newest file"

`reference/invoices_*.pdf` uses glob-latest-by-filename because revenue only accumulates — a newer export is always a superset in scope, so "newest wins" is safe. The catalog doesn't have that guarantee: an item can be renamed, discontinued, or re-priced between exports, so a newer snapshot is not necessarily a superset of an older one. Using an explicit pointer instead of glob-latest makes "this snapshot is now active" a deliberate, reviewed, diffed action rather than an automatic side effect of dropping a new file into `reference/`.

Known limitation, not yet a problem: if a catalog item is ever discontinued in a future snapshot, `parse_invoices.py`'s recognized-header gate (which reads only the *active* snapshot) would reject that name when re-parsing older invoices that used it. With a single snapshot in play this doesn't arise. If/when it does, resolve it explicitly (e.g., union of all snapshots for gate purposes) rather than guessing now.

**First real occurrence, 2026-07-13 (H-066):** "Weeding Maintenance" was discontinued in that day's export, merged into the existing "Weeding" item. Resolved via the *simpler* of the two mechanisms already available, not the "union of all snapshots" approach floated above: since the discontinued name maps cleanly onto one surviving catalog name, it was added to `model/data/service-name-map.csv` as an ordinary legacy-name alias (`Weeding Maintenance,Weeding`) — the exact mechanism already used for every other historical rename (`Mulching`→`Mulching/Soil Placement`, etc.). `check_recognized_headers()` treats `service_map.keys()` as recognized regardless of whether the name still appears in the active snapshot, so this needed no code change. The "union of all snapshots" approach remains the fallback for a future case that *isn't* a clean one-to-one merge (e.g. a discontinued item with no successor).

## Steps

1. Export **Items and Services** from Homeworks as a CSV.
2. Save it as `reference/service-catalog-<YYYY-MM-DD>.csv`, dated by export date. **Never edit or overwrite a prior snapshot** — each export is its own immutable raw source (see `reference/README.md`).
3. If the Homeworks **Packages** tab has changed, capture it the same way: transcribe into `reference/service-packages-<YYYY-MM-DD>.csv` (columns `package_name,item_name,item_order`), tagged ACTUAL/owner-confirmed with the capture date as source.
4. Diff the new snapshot against the previous one (`diff` on the two dated CSVs). Log any additions, removals, or rate changes to `HISTORY.md` as a new entry.
5. Update the pointer in `reference/README.md`'s "Active catalog snapshot" line to the new filename and date. This is the one piece of catalog-tracking data that is allowed to change in place — same pattern as the Relay account-map table.
6. If any catalog item was added, confirm it has an entry in `model/data/service-name-map.csv` (if renamed from a legacy name) and `model/data/catalog-type-map.csv` (item vs. service classification). `parse_invoices.py`'s fail-closed gates will reject an unrecognized or unclassified name — that's the intended catch, not a bug to work around.
7. Re-run `python model/parse_invoices.py` and confirm all gates still pass.
8. Run:
   ```
   python model/build_ledger_revenue.py
   ```
   **This step is required and easy to forget** (found stale by the Follow-Up #22 cross-reference audit, H-055 — the same gap H-051 already fixed in `reference/REVENUE-UPDATE.md`'s own step 6): `parse_invoices.py` only regenerates `model/data/revenue-invoices.csv` and `model/data/revenue-line-items.csv` — it does not touch `model/data/ledger-revenue.csv`. A catalog change can alter how *existing* invoice lines classify (service vs. `BLOCKED — unmapped`, or `item`/`service` kind) once re-parsed against the new catalog, even with no new invoices — so skipping this step can leave the actual ledger stale on a catalog-only refresh, not just a revenue refresh. This script rebuilds `ledger-revenue.csv`'s invoice/surcharge/tip rows and fails closed if the built total doesn't match the known revenue anchor to the penny.

## Refresh trigger

At minimum each Revision Point (RP1/RP2/RP3 per the Execution Timeline), or immediately whenever the owner notices a catalog change (new item, rate change, removed item) — whichever comes first.

## Packages feature vs. bundle labels — do not conflate

Homeworks' **Packages** feature ("Items / Services Packages" tab) defines named bundles (`General Maintenance`, `Lawn Care`) as a first-class object with an explicit item list. As of the 2026-07-09 snapshot, **this feature has never been used to generate a bill** — no invoice line item traces to it. This is distinct from the informal "General Maintenance" / "Lawn Care" / "Lawn Maintenance" **bundle labels** that already appear as literal invoice headers in `model/data/revenue-line-items.csv` (`is_bundle=TRUE`), which are free-text service names typed at billing time, not output of the Packages feature. The two share names by coincidence of the owner's own naming habits, not by mechanism. See `reference/service-packages-2026-07-09.csv` for the current (unbilled) package definitions.
