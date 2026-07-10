---
title: Phase 7 Scoping — Atomic Ledger & Model Build
type: planning
status: draft — awaiting owner sign-off on Section 4 open decisions
date: 2026-07-09
tags: [phase7, ledger, schema, planning, model-build]
---

# Phase 7 Scoping — Atomic Ledger & Model Build

**Purpose.** Both pre-build gates are closed (Gate B — H-033/H-036/H-037/H-038; Gate A — H-039). This document scopes the ledger schema and build sequencing *before* any ledger CSV or `build_model.py` code is written, per the owner's instruction that a wrong schema decision here is expensive to unwind. **No data files are created and no code is written in this pass.** Section 4 collects every decision that needs the owner's sign-off before Part 7 proper begins.

---

## 1. Spec re-read (Step 1)

Re-read fresh from `CONTEXT.md`: Section 4 (D1, D2, D5, D5a, D6, D7, D8), Section 7 Follow-Up #15, Section 9 (Model Architecture Specification). No paraphrase from memory — the schema proposal below (Section 2) quotes the existing draft schema in Section 9 verbatim as its starting point, and every "what's real vs. estimated" claim below is checked against Section 9's own "What is real vs. estimated at build time" list, not re-derived independently.

---

## 2. Inventory — what already exists as ledger input (Step 2)

| File | Provides | Ledger-ready? |
|---|---|---|
| `model/data/revenue-invoices.csv` | 68 rows, invoice-level: `invoice, invoice_date, customer_id, customer, net_subtotal, surcharge, gross, amount_paid, total_due, tip, status, source`. Confirms Follow-Up #15's finding directly: `amount_paid` = `gross` and `total_due` = `0.0` on **every** row inspected — the CRM payment fields are structurally unusable for collection timing (see Section 4). | Billed side — yes, needs schema transform, not new data. |
| `model/data/revenue-line-items.csv` | 152 rows, line-item level: adds `service_date, service_raw, service, kind, is_bundle, line_net, surcharge_pct, line_surcharge, line_gross` on top of the invoice fields. | Billed side, finer grain — same transform question, see Section 4 decision 2. |
| `model/data/service-name-map.csv`, `catalog-type-map.csv` | Classification support (legacy→canonical service names; item-vs-service tagging). Not ledger rows themselves — feed the `category`/`subcategory` columns of revenue events. | Support only. |
| `reference/cash-consolidated-2026-07-06.csv` | A **point-in-time balance snapshot** (4 accounts, one `as_of_date`). **Not usable as ledger input** — it has no transaction-level rows, so it cannot supply payment *events*. Its only role is a reconciliation check: the ledger's derived running cash balance as of 2026-07-06 should equal this file's $1,225.33 total. | Reconciliation check only, not a source. |
| `reference/fixed-overhead.md` | 6 itemized, dated, sourced overhead contract lines ($696.58/mo contracted total); explicit ACTUAL/BLOCKED tags; states cadence (monthly vs. lump-sum annual/semi-annual) — directly usable for `type=overhead` ledger rows. | Yes, directly. |
| `reference/Relay *.csv` (89 files, 2025-03 through the 2026-07 partial pulls) | Transaction-level bank data — `Date, Payee, Account #, Transaction Type, Description, Reference, Status, Amount, Currency, Balance`. This is the source D5a requires for payment/collected events. Inspected in depth for this plan (Section 4) — it is usable, but only with a matching layer that does not yet exist. | Source exists; matching logic does not. |
| `reference/expenses__January_1_2026__July_1_2026.csv` | CRM expense export, grouped by category (Insurance, etc.), itemized rows with Date/Vendor/Cost/Amount. Overlaps `fixed-overhead.md` for some lines (e.g., the $999 commercial-auto entry) but is CRM-entered, not bank-sourced — lower trust than Relay per D5a's cash-source-of-truth rule. Useful as a cross-check, not a primary ledger source for overhead cash timing. | Cross-check only. |
| `reference/revenuebycustomer__*.csv`, `salestax__*.csv`, `services__*.csv`, `services__*_1.csv`, `source__*.csv` | CRM-generated rollups (revenue by customer, sales-tax summary, service-level qty/price, **payment-type breakdown** — Check 6.09% / Credit Card 29.11% / Customer Credit Balance 0.46% / EFT 64.34% of the $10,973.57 collected total — and lead-source log). These are **derived CRM views, not atomic sources** — under D5 the ledger must be built from the underlying invoice/line-item/bank data, not from a pre-aggregated CRM report. Useful only as an independent cross-check total (e.g., "does our payment-type split for matched events look like 64% EFT / 29% credit card?"). | Cross-check only, not a source. |
| `reference/landscaping-financial-model-3.xlsx`, `report_profit_and_loss_2.pdf` | The original pre-rebuild model and P&L report. Superseded ground truth from before the rebuild decision (D5–D8) — historical reference only, not a Phase 7 input. | Not applicable. |

**Nothing needed for Section 2's inventory is missing.** The one real gap — a source that ties a specific Relay deposit to a specific invoice/customer — is not a missing *file*, it's a missing *matching layer*, addressed in Section 4.

---

## 3. (a) File layout proposal

**Options:**

1. **Single file** — `model/data/ledger.csv`, one physical file, all `type` values (revenue/labor/overhead/materials/capital) as rows. This is the literal reading of D5's "a single atomic actuals ledger."
2. **Split by `type`** — `model/data/ledger-revenue.csv`, `ledger-labor.csv`, `ledger-overhead.csv`, `ledger-materials.csv`, `ledger-capital.csv`, all sharing the identical column schema from Section 9, logically unioned into one table by `build_model.py` before any derived view is computed.

**Tradeoff, stated explicitly:**

- Single file reads D5 most literally — one file *is* "the ledger." But two practical costs: (i) rows across types are naturally interleaved by date, so a routine edit (e.g., appending Sept's overhead renewal) inserts mid-file rather than appending at the end, producing a noisier diff than a clean tail-append; (ii) it breaks from this repo's established one-concern-per-file pattern (`revenue-invoices.csv` vs. `revenue-line-items.csv` are already split by concern rather than merged; `catalog-type-map.csv` is deliberately kept separate from `service-name-map.csv` per H-038).
- Split-by-type keeps each file's own chronological append pattern clean (new labor rows always land at the tail of `ledger-labor.csv`, never disturbing revenue or overhead rows), gives each category its own reviewable diff, and lets a type-scoped fail-closed gate (e.g., "every labor row's rate is in {25, 20}") scan one small file instead of filtering a large merged one. The cost is that D5's "single ledger" becomes a logical property enforced by `build_model.py` (which reads and concatenates all `ledger-*.csv` files before deriving any view) rather than a physical one — every derived view still draws from one unified in-memory table, so D5's substance (single source of truth, atomic rows, formula-derived summaries, no typed-in totals) is preserved; only the *storage* is split.

**Recommendation:** split-by-type, for the diff-cleanliness and precedent reasons above. **This is Section 4 decision 1 — flagged for confirmation, not silently adopted**, because it reads D5's stated text less literally than the single-file option.

---

## 3. (b) Revenue events — the concrete gap

### Billed side (invoice events) — solved, needs a transform, not new data

`revenue-line-items.csv` / `revenue-invoices.csv` already carry billed revenue as ACTUAL, penny-reconciled data. Producing `type=revenue, event=invoice` ledger rows from either file is a mechanical column-mapping exercise. (Which of the two files to map from is Section 4 decision 2 — see below.)

### Payment side (collected events) — the real gap, investigated below

Nothing in the repo currently ties a specific Relay deposit to a specific invoice or customer. I did not invent a matching method and build it — I inspected the actual Relay data to see what's matchable, and how. Findings, evidence-first:

**Finding 1 — some deposits cite the invoice number directly, and it checks out exactly.** The Income account (8735) shows entries like:
```
6/17/2026  ANACOSTIA COMMUN  Receive  Reference: "Invoice #64 ACBA"   +408.10
5/26/2026  ANACOSTIA COMMUN  Receive  Reference: "Invoice 48 - ACBA"  +2332.00
6/15/2026  ANACOSTIA COMMUN  Receive  Reference: "Invoice #52 - ACBA" +267.65
```
Cross-checked against `revenue-invoices.csv`: invoice 64 gross = $408.10, invoice 48 gross = $2,332.00, invoice 52 gross = $267.65 — **exact matches on all three**, confirming the parser's `invoice` column (regex-extracted from the PDF's own "Invoice #" text, `parse_invoices.py:48,149`) is Homeworks' real invoice number, not a re-numbered index — so this class of match is a reliable, exact, invoice-number join wherever the Reference field carries one.

**Finding 2 — where no invoice number is cited, amount + payee + a short date lag matches uniquely, at least in every case checked.** The Income account also shows repeated `WOMEN LIFE FRE` / `BILL_PAY` deposits with no invoice number in the Reference field. Checked every such deposit across five months of statements against Women Life Freedom LLC's invoices:

| Deposit date | Amount | Matching invoice | Invoice date | Lag |
|---|---|---|---|---|
| 2026-03-23 | $438.76 | #38 | 2026-03-14 | 9 days |
| 2026-04-14 | $1,107.70 | #41 | 2026-04-07 | 7 days |
| 2026-05-11 | $1,371.22 | #43 | 2026-05-05 | 6 days |
| 2026-05-26 | $671.33 | #50 | 2026-05-18 | 8 days |
| 2026-06-10 | $464.17 | #53 | 2026-06-02 | 8 days |
| 2026-07-06 | $1,105.84 | #67 | 2026-06-28 | 8 days |

Every deposit ties to exactly one invoice at an exact dollar match, with a consistent ~6–9 day lag, and no case of batching (one deposit = one invoice) in the sample. This is a real, checkable pattern — but it is a pattern observed in a sample, not a guaranteed property of all future data; a matching script built on it must verify uniqueness (does the amount match more than one open invoice within the lag window?) rather than assume it.

**Finding 3 — a real, bounded share of collected cash is not attributable to any customer from Relay data alone.** `STRIPE` entries settle as aggregated `TRANSFER` receipts with no payee, invoice, or customer field at all (e.g., three separate Stripe transfers of $81.19/$304.49/$48.59 in the 2026-07-01–07-06 window alone) — consistent with a credit-card processor batching multiple card payments, net of fees, into one deposit. Per `reference/services__..._1.csv` (a CRM-derived cross-check, not a primary source — see Section 2), Credit Card payments are **29.11% of collected revenue** ($3,194.84 of $10,973.57) for the Jan–Jul window. Notably, in the partial-July data, Stripe settles directly into account 3549 (OpEx), not 8735 (Income) — a routing detail that would need to hold across the full history for any per-account reconciliation to close cleanly.

**Finding 4 — some transactions are not revenue at all and must be excluded, not matched.** `Operating Expenses`/`Income` "Instant auto transfer" and "Transfer" pairs are the business moving its own cash between its own accounts (3549↔8735) — including one of these as a payment event would double-count. `USAA FSB TRNSFER` and `Credit Card Payment` (to account 4502) appear to be unrelated personal/internal transfers. `GUSTO` entries (`NET`, `TAX`, `FEE`) are payroll cash *outflows*, not revenue — though notable: the `FEE 505876 −$127.00` line matches `fixed-overhead.md`'s $127/mo Gusto contract figure exactly, which is a useful independent validation point for **overhead** cash events (Section 3c), not revenue.

**Finding 5 — name fields don't agree across sources, reinforcing why invoice-number matching should be tried first.** `revenue-invoices.csv` records the Anacostia customer as literally `"Association"` (a truncated CRM display value), while `revenuebycustomer__*.csv` gives the full `"Anacostia Community Boathouse Association"`, and Relay's `Payee` field gives `"ANACOSTIA COMMUN"` — three different strings for one customer. A matcher relying on payee-name equality alone would need fuzzy logic and could misfire; the invoice-number Reference field (Finding 1) is the more reliable signal where present.

**Finding 6 — the Stripe routing observed in Finding 3 is not constant; it is a two-era pattern (owner-confirmed, 2026-07-09).** Card/Stripe deposits routed to **OpEx (3549)** for all activity **before 2026-07-07**, and route to **Income (8735)** for activity **from 2026-07-07 onward**. This is a real cutover, not a data artifact — the partial-July Relay files observed in Finding 3 (Stripe settling into 3549) sit right at the boundary of this change. A matching script cannot treat Stripe routing as one uniform rule; it must branch on transaction date, with 2026-07-07 as the boundary parameter. This is a parameter the eventual matching script needs as an explicit, dated input — not something to hardcode as "Stripe always routes to X" from a sample that happens to sit on one side of the cutover.

**Finding 7 — Stripe deposits are net of a known, formulaic fee, and this is a distinct phenomenon from both the surcharge and the billed-collected gap (owner-confirmed, 2026-07-09).** Stripe's fee is **3.9% + $0.30 per charge**. A Stripe-settled deposit amount is therefore *net of this fee*, not the client's full card payment — so part of any apparent "billed vs. collected" shortfall on card-paid invoices is a real, computable fee expense, not a matching failure (Finding 3) or evidence of the CRM/bank timing gap Follow-Up #15 investigates. These are **three distinct phenomena and must not be conflated into one number**:
1. The 6% surcharge (Follow-Up #10) — added to the client's bill, collected from the client, a revenue-side item.
2. The Stripe processing fee (3.9% + $0.30) — deducted from what Stripe remits to the business, a cost-side item, unrelated to the surcharge.
3. The general billed-vs-collected gap (Follow-Up #15) — a timing/recording question about when and whether an invoiced amount is actually received, orthogonal to both of the above.

No fee schedule has been supplied for card payments processed **directly through Homeworks** (as distinct from the Stripe-routed deposits visible in Relay) — this is **not assumed or estimated here**; see the new Follow-Up item added to `CONTEXT.md` this pass (Follow-Up #17) and Section 4 decision 6 below.

**Scope clarification (owner-confirmed, 2026-07-09): the Stripe fee is a payment-side (collected) fact, not a billing-side (billed) fact, and has no bearing on `model/data/ledger-revenue.csv` (Sequencing Step 2, billed/invoice events only).** The 3.9% + $0.30 fee is deducted between the client's card charge and the deposit landing in Relay — it only exists once a payment is settled, so it applies exclusively to Sequencing Step 3's payment-event matching, and within that, only to Approach A's tier 3 (the Stripe/credit-card aggregated-receipt tier). ACH transfers (confirmed via Finding 1/2's Anacostia and Women Life Freedom LLC examples) and check payments carry no processing fee at all — they should reconcile dollar-for-dollar against their invoice's full billed amount, with no fee adjustment applied. Sequencing Step 3 must not apply fee-netting uniformly across all payment channels; it is a tier-3-only adjustment.

### Candidate approaches (not adopted — flagged for owner decision, Section 4 decision 3)

**Approach A — tiered/hybrid matching (recommended as the target state).**
1. Exact match via invoice number in the `Reference` field (Finding 1) → ACTUAL, high confidence.
2. Amount + payee + date-proximity match, with a uniqueness check against all open invoices in the lag window (Finding 2) → ACTUAL, flagged as "matched by amount, not by invoice-number citation," citing both source rows.
3. Aggregated/unattributable receipts (Stripe, Finding 3) → still real cash, so still counted in the collected-cash total (D5a's "collected = sum of payment events" must sum to the true bank total), but recorded as a payment event with `customer` left blank and a `subcategory` of "aggregated/unattributed" rather than fabricating a per-customer attribution that doesn't exist in the source data. The matcher must apply Finding 6's two-era routing rule (OpEx pre-2026-07-07, Income from 2026-07-07) when deciding which account's Stripe entries belong to this tier.
4. Internal transfers and non-revenue payees (Finding 4) → excluded entirely from revenue events.

This gets real per-customer collected-revenue data for roughly 71% of collected cash (100% − the 29% Credit Card share, modulo how much of that 29% turns out to route through Stripe vs. other channels — not yet verified), and an honest, non-fabricated aggregate bucket for the rest.

**Built (Sequencing Step 3, 2026-07-09) — a `type=overhead, category=Stripe, subcategory=payment-processing-fee` ledger category.** Per Finding 7, the Stripe fee (3.9% + $0.30/charge) is a real, computable cost distinct from both the surcharge and any Follow-Up #15 gap. **Corrected design (this pass):** each Stripe-matched (tier 3, `[aggregated]`) payment event's own `amount` is the actual net Relay deposit — never a back-computed gross — because D5a requires payment events to reconcile to the bank, and a gross-valued payment event would overstate real cash and break that reconciliation. The gross card charge is back-computed from the net deposit *only* to size the paired fee row: `gross = (net + $0.30) / (1 - 0.039)`, `fee = gross - net`, recorded as its own `type=overhead` cost event. This keeps the three phenomena in Finding 7 structurally separate rather than netted into one ambiguous "shortfall" number, and keeps the payment-event ledger internally consistent with the bank. (An earlier draft of this paragraph incorrectly described recording the back-computed gross as the payment event's own revenue-side amount — that was never implemented; this text corrects it before any confusion propagated into the data.) **The Stripe-fee portion is now built and populated** (`model/match_payments.py`, `model/data/ledger-overhead.csv`); fee-netting for Homeworks-direct card payments remains **BLOCKED** until the Homeworks fee schedule is supplied (Follow-Up #17) — do not invent or estimate that figure in the interim.

**Approach B — aggregate-only (a cheaper first cut).**
Record one payment event per account per bank statement period, no per-customer attribution at all — just "cash collected into account X between date Y and Z, per this Relay statement." Satisfies D5a's letter (collected = sum of payment events, bank-sourced) and is far simpler to build and gate (its own check is trivial: does the sum of payment events per account equal that account's actual balance delta over the period?). Sacrifices any "revenue collected by customer" derived view — a real capability loss, not a neutral simplification.

**My assessment:** Approach A is worth the extra build cost given this repo's stated preference for atomic, traceable data over blended entries (the same reasoning D2 applies to labor). Approach B is a legitimate fallback if the owner wants Phase 7 to close sooner and is willing to explicitly defer per-customer collection tracking (parallel to how Follow-Up #13 deferred bundled-line decomposition). **This is Section 4 decision 3.**

### Connection to Follow-Up #15

Follow-Up #15 asks why every invoice shows `amount_paid = gross, total_due = 0.0` in the CRM even though CRM-reported billed ($12,726.01) ≠ collected ($10,973.57). Building the payment-event matching logic above is very likely the same investigation, not a separate task: once real payment events are matched against real invoices (Approach A) or at least reconciled against real bank totals (Approach B), the resulting data directly shows *which* invoices the bank confirms as paid and *when* — which is the evidence needed to characterize what the CRM's "Amount Paid" field actually represents (most likely: it reflects amount *invoiced-as-paid-in-full at send time* rather than *amount actually received*, but this is my working hypothesis from the pattern observed, not a verified conclusion — Standing Rule 3 requires it be confirmed by the matching build, not asserted here). **I agree they are the same work — Section 4 decision 4** asks the owner to confirm this framing before Follow-Up #15 is tracked as a separate open item.

---

## 3. (c) Labor, overhead, materials, capital — sourcing per category

**Labor.** Rates are real and unchanged: crew lead $25/hr, crew member $20/hr (D2). Hours remain the ESTIMATE (~20 person-hours/2wk, 2-person 50/50 split) — confirmed no time-tracking export exists anywhere in `reference/` or `model/data/` (checked directory listings; Follow-Up #2 explicitly states the seat/headcount question is deferred to a post-transition session and "full labor-actuals capture is limited" until then). One partial, aggregate-only cross-check does exist: Relay's `GUSTO` `NET`/`TAX` entries are real total payroll cash outflows (e.g., $1,137.92 NET + $199.50 TAX in the partial-July window) — useful as a coarse "does total modeled labor cost roughly track total payroll cash out" sanity check, but they carry no per-job or per-person hour detail and cannot replace or override D2's estimate.

**Overhead.** `reference/fixed-overhead.md` supplies all 6 contracted lines (Gusto, General Liability, Workers' Comp, Commercial Auto, Homeworks, Squarespace) as ACTUAL, dated, with stated cadence (monthly vs. lump-sum). The Gusto `FEE` line in Relay ($127.00, exact match) is a real, checkable validation point that this figure is traceable to actual bank cash, supporting D8's reconciliation-tab goal for overhead once ledger rows exist. Equipment-maintenance stays **BLOCKED** — no allocation base/method has been stated per Section 6 item I; it should not get a ledger row (not even a $0 placeholder row) until a basis is defined, consistent with how D1 treats materials.

**Materials/fuel.** Stays explicit `$0 BLOCKED` per D1 — no per-job attributable cost data exists yet, pending Job Costing activation. Confirmed the 3 `item`-kind catalog rows from H-038 (`Bagged Mulch`, `Landscaping Blocks (stone)`, `New Plants`) do **not** change this: those are what the business *bills clients for* (revenue-side `kind=item` rows), not what it *paid* for materials — a `type=revenue` fact, not a `type=materials` cost fact. The two must land as different ledger rows if and when both exist.

**Capital.** Two patient-capital obligations exist, both unpaid, demand-triggered, and interest-free — treated as equity for cash-buffer purposes on the same basis (`strategy/execution-timeline.md`'s Cash Buffer Policy, "Debt repayment (Xavier, owner)"): Xavier (~$1,800, per Section 6 item D) and the owner's (Cyrus's) truck-debt repayment ($3,800, added to Section 6 item D and `strategy/strategic-plan.md` Section 9's Assumptions Log this pass). **Neither belongs as a ledger row yet** — both are forward contingencies that belong in the **projection layer's assumptions**, not the actuals ledger, until actually triggered (Section 4 decision 5). The sequencing between them — Xavier repaid first, the owner's truck debt only after — is itself a fact the projection layer must encode even though neither has a ledger row: a projection that modeled the owner's $3,800 as available for repayment before Xavier's $1,800 was cleared would misstate near-term cash availability, regardless of the ledger being silent on both until trigger. Both remain gated behind the same $6,000 buffer ($4,000 reserve + $2,000 truck hedge) being intact. Truck entry (H-025) — explicitly *not* a new cash outflow (a retroactive CRM bookkeeping entry for an already-owned asset; unrelated to the owner's truck-*debt* repayment above, which is a real unpaid obligation) — should be **excluded from the ledger entirely**, not recorded as a $0 or informational capital row, so it can't later be mistaken for a real event. Auto-insurance increment (item J) — BLOCKED pending an insurer quote; no ledger row until quoted and incurred.

**Update (Sequencing Step 4, H-046):** `model/data/ledger-capital.csv` is no longer empty — two real, unrelated capital events now have ACTUAL rows: a chainsaw purchase ($408.00, 2025-08-17) and the owner's combined truck/insurance-advance reimbursement ($2,200.00, 2026-04-09), both sourced to real Relay transactions found during that pass. This does not change anything above — Xavier and the owner's remaining $3,800 truck-debt balance are still correctly absent from the ledger, for the reasons already stated in this paragraph; the two new rows are separate, already-settled events, not a repayment toward either of those two obligations.

---

## 3. (d) Sequencing plan

Each step below is sized to be its own reviewable commit, matching the granularity Gates A and B were built at:

1. **Schema + skeleton files.** Create the ledger file(s) (per Section 4 decision 1) with header row only — no data — so the schema itself is reviewed in isolation before anything is populated.
2. **Populate revenue invoice events.** Transform `revenue-line-items.csv` (or `revenue-invoices.csv`, per Section 4 decision 2) into ledger rows. Gate: ledger revenue-invoice total reconciles exactly to the already-verified $27,891.65 gross / $12,726.01 billed anchor — no new data, a pure transform check.
3. **Resolve and populate payment events.** Build the matching logic per whichever approach Section 4 decision 3 settles on, as its own reviewable script/pass, given its complexity. Gate: per-account sum of ledger payment events reconciles to that account's actual Relay balance delta over the covered window.
4. **Populate labor, overhead, materials, capital events.** Each as its own small commit: labor rate/estimate rows; overhead rows sourced from `fixed-overhead.md` with lump-sum cash events dated to real renewal/payroll dates (using the Gusto Relay entries as a validation point); materials and capital placeholders per Section 3(c).
5. **Write `build_model.py`.** Derived views (P&L, plan-vs-actual, quarterly rollups, revenue by service/customer, blended labor rate) generated by formula from the now-populated ledger.
6. **Add the reconciliation tab (D8)**, honestly scoped to revenue and collected cash only, per Section 9's existing scope statement.
7. **First full build + validate** against `reference/` (CRM revenue exports, Relay bank statements) — the first real `financial-model.xlsx` generation and inspection.

---

## 4. Open decisions requiring sign-off before any code is written

1. **File layout (Section 3a).** Single `model/data/ledger.csv` vs. type-split `ledger-revenue.csv` / `ledger-labor.csv` / `ledger-overhead.csv` / `ledger-materials.csv` / `ledger-capital.csv` sharing one schema. **Recommendation: type-split.**
2. **Revenue-event source granularity (Section 3b).** Map billed events from `revenue-invoices.csv` (68 rows, invoice-level) or `revenue-line-items.csv` (152 rows, carries `service`/`kind` detail needed for revenue-by-service views). **No recommendation stated here — flagged as a straightforward but unmade choice.**
3. **Payment-event matching approach (Section 3b).** Approach A (tiered/hybrid: invoice-number match → amount/payee match → aggregated bucket for Stripe → excluded internal transfers) vs. Approach B (aggregate-only per account/period, no customer attribution). **Recommendation: Approach A as the target, with Approach B as an acceptable, explicitly-scoped-down fallback if the owner wants to unblock the build sooner.**
4. **Whether Follow-Up #15 is the same work as decision 3, not a separate task.** **My assessment: yes** — confirm before Follow-Up #15 continues to be tracked separately in `CONTEXT.md` Section 7.
5. **Whether Xavier's and the owner's (Cyrus's) truck-debt contingent payouts get ledger rows now or stay projection-layer assumptions until demand-triggered.** Both are patient, interest-free, demand-triggered obligations on the same basis, sequenced Xavier-first (Section 3c). **Recommendation: projection-layer assumptions only for both, no ledger rows yet — but the projection layer must encode the Xavier-before-owner sequencing even without ledger rows.**
6. **Payment-processing-fee ledger category (Section 3b, Finding 7).** Not a choice awaiting a preference — a genuine external-data BLOCKED item. The Stripe-fee portion (3.9% + $0.30/charge, owner-confirmed) is now **built and populated** (`model/match_payments.py`, `model/data/ledger-overhead.csv`, Sequencing Step 3, H-044); the Homeworks-direct-card-payment portion remains **BLOCKED** until a fee schedule is supplied (Follow-Up #17 in `CONTEXT.md`). Do not estimate or invent this figure to unblock it.

**Nothing past this document should be built until decisions 1 through 5 are resolved; decision 6 is a standing BLOCKED item that limits only the fee-netting portion of Sequencing Step 3, not the schema work in Step 1.**
