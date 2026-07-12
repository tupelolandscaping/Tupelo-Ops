# Stripe Balance-History — Standing Update Procedure

## Why this exists

`model/match_payments.py`'s `load_stripe_fee_lookup()` (H-062) uses `reference/stripe-balance-history-*.csv` as the ground-truth source for Stripe fee amounts on any payout it covers — true per-charge sums, replacing the 3.9%+$0.30 back-solved-per-day estimate for those rows. The export currently on file covers 2025-07-07 through 2026-07-03. **Every Stripe payout after that date silently falls back to the less-accurate formula** — the pipeline never fails, it just quietly loses precision (H-061 found this fallback undercounts by ~$0.30 per extra charge whenever a payout batches more than one charge; H-062 corrected the $2.56 this had already caused historically). Refreshing this export is how that precision is kept current going forward.

## Why a full re-export and full re-run, never an incremental delta

Same reasoning as `REVENUE-UPDATE.md` and `PAYROLL-UPDATE.md`. Unlike those two, this export's window is **not known to have Gusto's ~1-year rolling-export limitation** — if Stripe's dashboard allows exporting the full history to date in one pull, prefer that; it's simplest and avoids gap-tracking entirely. If a full pull isn't practical, an incremental pull from the prior file's end date forward is safe too: **overlapping windows are explicitly handled** — `load_stripe_fee_lookup()` deduplicates every row by Stripe's own `id` column (H-064), a true unique transaction identifier, before summing. This is more robust than `reference/Relay*.csv`'s own dedup, which has to fall back to heuristic tuple-matching because Relay rows carry no such ID. Do not delete or overwrite a prior export — each dated file is its own immutable raw source, filed here verbatim (see `reference/README.md`).

## Steps

1. Export a fresh **balance transaction history** report directly from Stripe's own dashboard (not via Homeworks) — Balance → Transaction history, or Reports → Balance report, CSV export — covering the window needed (ideally the full history to date; otherwise from the prior file's end date forward).
2. Save it as `reference/stripe-balance-history-<start>-to-<end>.csv`, dated by the coverage window, matching the existing file's naming convention.
3. Update `reference/README.md`'s "Stripe balance-history export" section to list the new file alongside the existing one(s), including its row-type breakdown (`charge`/`payout`/`refund` counts) the same way the first file was documented (H-061).
4. Run:
   ```
   python model/refresh_all.py
   ```
   Check `match_payments.py`'s printed `[stripe-fee] N/32 fee rows use true per-charge sums ... M fall back` line (the totals will grow past 32 as more Stripe activity accrues) — a nonzero fallback count is expected and fine for payouts genuinely outside every export's combined coverage; it is not a gate failure, just the known degrade-gracefully behavior this design intentionally has (H-062).
5. Review `git diff` on `model/data/ledger-overhead.csv`'s Stripe `payment-processing-fee` rows — this diff *is* the period's fee-accuracy update: new payout rows, and any existing row whose fee changed because it's now covered by true per-charge data instead of the formula fallback.
6. Log the refresh in `HISTORY.md` (new export filed, new fallback/true-sum coverage counts, any dollar change to the Stripe fee total).
7. Commit.

## Cadence

Unlike Relay/payroll, there is **no hard correctness gate** riding on this refresh — the pipeline always produces a valid result either way. Refresh whenever precise fee accuracy for a specific recent period actually matters: ahead of a Cash Buffer Policy check-in, before relying on a recent month's overhead figure for a decision, or simply whenever it's convenient and Stripe activity has accrued since the last pull. There is no urgency comparable to Relay's cash-balance staleness or payroll's reconciliation gate — treat this as a precision refresh, not a data-integrity one.

## What a re-run produces and gates on

**No fail-closed gate (deliberate).** `load_stripe_fee_lookup()` returns `{}` if no export file is present at all, and any payout without a matching (date, net) entry silently uses the fallback formula — the script never halts on missing or stale Stripe-export coverage. This is a genuine, intentional difference from every other pipeline stage's fail-closed design (H-062); do not add a hard gate here without also reconsidering whether that's the right tradeoff, since the fallback's whole purpose is to let the pipeline keep working before this export ever existed and after any future payout it hasn't yet covered.

**Deduplication.** By Stripe's own `id` column (H-064) — a true unique identifier, not a heuristic match. Safe against overlapping export windows by design.

**Known, standing limitation (do not treat a refresh as resolving this).** This export only improves *fee* accuracy on the existing `unattributed [aggregated]` Stripe payment-event rows in `model/data/ledger-revenue.csv` — it does **not** re-attribute those rows to specific invoices, even though the same export's `Description`/`Transfer` fields make that fully possible (H-061 finding 8; 32/32 of the aggregated rows as of H-061). That is a separate, larger, deliberately deferred rebuild of `match_payments.py`'s tier-3 classification logic — see `CONTEXT.md` Follow-Up #25. A routine fee-accuracy refresh under this procedure does not touch that.
