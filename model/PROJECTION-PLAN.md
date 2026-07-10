---
title: Projection-Layer Scoping — Cash Trajectory & Plan vs Actual
type: planning
status: draft — awaiting owner sign-off on Section 6 open decisions
date: 2026-07-10
tags: [projection-layer, assumptions, cash-trajectory, planning]
---

# Projection-Layer Scoping — Cash Trajectory & Plan vs Actual

**Purpose.** This is Phase 7's deferred second half. `build_model.py`'s "Plan vs Actual" sheet has been an explicit, empty stub since H-047 (no `model/data/assumptions.csv` exists; D6 forbids hardcoding `strategy/`'s prose tables into the script). This document scopes the assumptions schema and the cash-trajectory calculation *before* any CSV or code is written, mirroring `PHASE7-PLAN.md`'s own discipline. **No data files are created and no code is written in this pass.** Section 6 collects every decision needing the owner's sign-off before implementation begins.

---

## 1. Spec re-read (Step 1) — and is the existing plan baseline stale?

Re-read fresh: `CONTEXT.md` Section 9 (D6/D7), Section 3, D4, Section 6 item D; `strategy/execution-timeline.md`'s Cash Buffer Policy and Monthly Financial Targets table; `strategy/strategic-plan.md`'s Quarterly Goals table, Financial Assumptions Log, and Revision Note.

**D6/D7, restated for this document's own discipline:** the projection layer may only reference derived data-layer values or clearly-labeled assumption cells — never a hardcoded number. This governs everything below: any figure this plan proposes putting in `model/build_model.py` must trace to either `model/data/ledger-*.csv` (computed fresh at build time) or `model/data/assumptions.csv` (a labeled, sourced, dated row) — never a number typed into the script.

**Section 3's objectives, the actual target this layer serves:** roughly double peak monthly revenue from the **May 2026 actual peak of $4,908** toward **~$10,000/month**, and — more importantly per Section 3's own ordering — make the business **operate owner-absent** before the January 2027 relocation. D4 requires Konji's crew-lead cost be built as an explicit **phase switch** (full negotiated terms through May 2027; a generic $25/hr line, no share, no bonuses, after). Section 6 item D requires Xavier's ~$1,800 payout and the owner's $3,800 truck-debt repayment be encoded as **sequenced, demand-triggered** contingent outflows (Xavier first, both gated on the $6,000 buffer being intact) even though neither has a ledger row.

**Direct answer to Step 1's question: the existing monthly/quarterly targets are known-stale, not a legitimate comparison baseline, and the source documents already say so explicitly — this was not close.** Both `strategy/execution-timeline.md`'s Monthly Financial Targets table and `strategy/strategic-plan.md`'s Quarterly Goals table are the same underlying figures (Jul '26 $4,140 → Jun '27 $9,180 revenue), and both carry the same footnote: **"reconciled to the financial model on 2026-06-17"**, built on a **$4,500 peak anchor** — before the $4,908 May 2026 actual was validated. `strategic-plan.md` line 25 states this even more directly: *"the quarterly target tables and any '~$9K peak' references below still derive from the 2026-06-17 model built on the $4,500 anchor, and will be regenerated against the updated anchor during the Phase 7 model rebuild — treat their values as superseded pending that rebuild."* That rebuild is what this document scopes. **Do not import these tables as the comparison baseline.** They should be superseded by the recomputed trajectory this plan proposes, with their values preserved in `strategy/strategic-plan.md`'s Revision Note (already the repo's convention) rather than silently discarded.

**A second, more consequential staleness finding, surfaced only by Step 2's fresh computation below: even the $4,908 anchor itself is now stale.** See Step 2.

---

## 2. The real trend, computed fresh from the actuals ledger (Step 2)

Computed directly from `model/data/ledger-revenue.csv` (invoice events = billed; payment events = collected), `model/data/ledger-labor.csv`, and `model/data/ledger-overhead.csv` — not recalled from any prior session narration.

### 2.1 A new finding: the peak has already moved

| Month | Billed |
|---|---|
| 2026-04 | $1,277.30 |
| 2026-05 | $4,915.54 |
| 2026-06 | **$6,019.89** |

May 2026 billed ($4,915.54) closely matches the $4,908 anchor everyone has been citing (the ~$7.54 gap is an immaterial method/bucketing difference, not a discrepancy worth chasing). **But June 2026 billed is $6,019.89 — a new, higher peak that has never been surfaced anywhere in `CONTEXT.md`, the strategic plan, or `HISTORY.md`.** This is a real finding, not a data artifact: 106 line-item-derived rows, dated across the whole month (2026-06-02 through 2026-06-29), from the same reconciled invoice source. **The "$4,908 is the strongest month to date" framing in `CONTEXT.md` Section 3 is itself now stale and should be corrected when this plan is implemented** — not asserted as fixed here, since Standing Rule 3 requires tracing a number before using it, but flagged prominently since it directly bears on how close the business already is to the $10,000 target (60% of the way there in the peak month observed, not 49%).

### 2.2 Full seasonal-cycle net cash rate (Jul 2025 – Jun 2026, 12 complete calendar months)

The only full cycle the ledger currently covers — includes the real winter trough (Jan/Feb 2026 show **zero** collected revenue and zero labor: a genuine seasonal dead zone, not a data gap, confirmed during H-049's payroll parse).

| | Total | Avg/month |
|---|---|---|
| Collected | $22,046.98 | $1,837.25 |
| Labor + overhead (outflow) | $19,953.84 | $1,662.82 |
| **Net** | **$2,093.14** | **$174.43** |

Only **5 of 12 months** were net-cash-positive. Materials are excluded from outflow (D1: $0, BLOCKED, real materials cost is not yet captured, so true net is likely somewhat worse than this).

### 2.3 Recent 3-month rate (Apr–Jun 2026) vs. the same window a year earlier

| | Apr–Jun 2025 | Apr–Jun 2026 | YoY |
|---|---|---|---|
| Collected | $5,789.56 | $10,182.91 | **+75.9%** |
| Outflow | — | $9,752.55 | — |
| Net | — | $430.36 (avg $143.45/mo) | — |

**Revenue growth is real and strong** (+75.9% YoY on collected cash — direct evidence the doubling objective is underway). **But net cash is not growing at anywhere near that rate**, because outflow has grown almost as fast (Konji's payroll ramp-up chief among the causes — see 2.4). This is the single most important, non-obvious finding this fresh computation surfaces: strong top-line growth has not yet translated into proportionally stronger cash accumulation.

*Caveat on the YoY comparison basis:* this uses **collected** cash (Relay-sourced, available back to March 2025). A billed-basis YoY comparison is not currently possible over the same 3-month window — the invoice PDF (`reference/invoices_2025-06_2026-06.pdf`) only covers billing from June 2025 onward, so April–May 2025 has no billed data at all. Only June has a true billed YoY pair (2025: $3,670.36 → 2026: $6,019.89, +64.0%). This is a real data-coverage limit, not a choice — flagged for awareness, not something to resolve in this pass.

### 2.4 Forward crew-labor-cost signal (crew roles only, per H-050's `CREW_ROLES` scoping)

| | Total | Avg/month |
|---|---|---|
| Full cycle (Jul'25–Jun'26) | $10,671.63 | $889.30 |
| Recent 3 months (Apr–Jun'26) | $5,611.83 | **$1,870.61** |
| D2's old synthetic model (superseded, for comparison only) | — | ~$977.68 |

The full-cycle average is reasonably close to D2's old planning estimate. **The recent 3-month average is more than double it** — real, current crew spending has already outgrown the original synthetic estimate by ~90%, consistent with Konji's move to weekday crew lead. This directly informs the Step 3/6 design choice on which forward labor-cost assumption to use.

### 2.5 Plain answer to "is the business tracking toward the targets?"

**It depends entirely on which trend rate is extrapolated — and the honest answer is that the current data supports wildly different conclusions depending on that choice.** At the full-cycle average net rate ($174.43/mo), reaching the $6,000 buffer from today's verified $1,225.33 (a $4,774.67 gap) takes **~27 months** — landing around late 2028, more than two years behind the plan's Nov–Dec 2026 target. At a growth-adjusted rate reflecting recent momentum (worked in Section 5), the same gap closes in **~2.4 months** — essentially on schedule. Neither number should be presented alone as "the" answer; this is exactly why Section 4's calculation method proposes a range, not a point estimate.

---

## 3. Proposed `model/data/assumptions.csv` schema (Step 3)

**Column schema:**

```
assumption_id, category, label, value, unit, effective_date, end_date, trigger_condition, status, source
```

- `assumption_id` — stable short key (e.g. `peak_revenue_target`, `cash_buffer_reserve`, `konji_hourly_rate`), referenced by the calculation logic.
- `category` — groups related rows (`revenue_target`, `cash_buffer`, `labor_cost`, `capital_obligation`).
- `label` — human-readable description.
- `value` — the number. Blank/`0.00` with `status=BLOCKED` when genuinely unavailable (mirrors how `ledger-materials.csv`'s BLOCKED placeholder already works) — never a guessed number.
- `unit` — `$`, `$/hr`, `%`, `$/month`, etc.
- `effective_date` / `end_date` — for time-varying assumptions, one row per period (the same pattern `model/data/employee-role-map.csv` already established for Xavier's role change). Blank `effective_date` means "from the ledger's start"; blank `end_date` means "open-ended, still current."
- `trigger_condition` — plain-text description of a conditional (not calendar-date) trigger — see 3.4. Blank for date-certain or ongoing assumptions.
- `status` — **a new vocabulary, distinct from the ledger's ACTUAL/ESTIMATE/BLOCKED**, since assumption rows are inherently forward-looking/normative, not "did this happen": `TARGET` (a goal, e.g. peak revenue), `POLICY` (an owner decision, e.g. buffer composition), `CONTRACTED` (a real agreed rate, e.g. Konji's terms), `DERIVED` (computed from real ledger data, not asserted), `BLOCKED` (unavailable), `ACTUAL` (reused only for a dated snapshot fact that cannot be derived from the ledger — see 3.2). **Flagged for sign-off in Section 6** — extending the ledger's status vocabulary to a different kind of row is a real design choice, not a foregone one.
- `source` — H-number, `strategy/` section citation, or an owner-confirmation date.

**Design principle, stated once so it doesn't need repeating per row: derive from the ledger whenever the ledger can support it; only hardcode a snapshot into `assumptions.csv` when the ledger structurally cannot reconstruct the figure.** This is why the peak-revenue *actual* does **not** get its own assumptions.csv row below (Section 2.1 shows it's already derivable, and self-correcting, straight from `ledger-revenue.csv` — exactly the failure mode that let the $4,908 anchor go stale in the first place must not be re-introduced here).

### 3.1 Peak-revenue target

```
peak_revenue_target, revenue_target, "Peak monthly revenue target", 10000.00, $, , , , TARGET, CONTEXT.md Section 3
```
The build script computes the *actual* peak-to-date fresh from `ledger-revenue.csv` at every build (never stored here) — this is what would have caught the June 2026 peak automatically had it existed already.

### 3.2 Cash-buffer target and starting position

```
cash_buffer_reserve, cash_buffer, "Operating reserve floor", 4000.00, $, , , , POLICY, strategy/execution-timeline.md Cash Buffer Policy
cash_buffer_truck_hedge, cash_buffer, "Truck hedge", 2000.00, $, , , , POLICY, strategy/execution-timeline.md Cash Buffer Policy
cash_starting_balance, cash_buffer, "Verified starting cash", 1225.33, $, 2026-07-06, , , ACTUAL, HISTORY.md H-039
```
**`cash_starting_balance` is the one snapshot fact that must be hardcoded, not derived** — `build_model.py`'s own Reconciliation tab already documents that ~85% of real settled Spend-side Relay cash has no ledger row at all (uncaptured vendor spend, internal transfers), so the ledger's own net-cash arithmetic cannot reconstruct the real bank balance. The projection must start from the independently-verified figure and project *forward* from there using the ledger-derived trend rate, not attempt to re-derive the historical starting point from an incomplete ledger. This snapshot will need periodic re-verification (the same discipline as the $1,500→$1,400→$1,225.33 lineage) — flagged in Section 6 as a standing-maintenance need, not solved here.

### 3.3 Konji's phase-switch cost structure — one row per rate component per period

D4's phase switch is more granular than a single before/after number: Konji has a base hourly rate (itself already time-varying, per H-048/H-049 — $20/hr through his last completed period, $25/hr from his next, negotiated period, exact start date not yet run as of the payroll exports), a revenue share, two seasonal canvassing bonuses, and a winter project rate — each ends or changes at the May/June 2027 phase boundary, not just the base rate:

```
konji_hourly_rate, labor_cost, "Konji base hourly rate", 20.00, $/hr, , 2026-0?-??, , CONTRACTED, HISTORY.md H-048 (rate not yet run as of exports -- effective end-date is an OPEN ITEM, see Section 6)
konji_hourly_rate, labor_cost, "Konji base hourly rate (negotiated)", 25.00, $/hr, 2026-0?-??, 2027-05-31, , CONTRACTED, HISTORY.md H-048/CONTEXT.md D4
konji_hourly_rate, labor_cost, "Konji base hourly rate (post-phase-switch)", 25.00, $/hr, 2027-06-01, , , CONTRACTED, CONTEXT.md D4
konji_revenue_share_pct, labor_cost, "Konji revenue share on jobs he leads", 6.00, %, 2026-09-01, 2027-05-31, , CONTRACTED, CONTEXT.md D3/D4
konji_canvassing_rate, labor_cost, "Konji canvassing hourly rate", 15.00, $/hr, , 2027-05-31, , CONTRACTED, strategy/strategic-plan.md Section 4
konji_canvassing_bonus_fall, labor_cost, "Konji per-fall-client-signed bonus", 15.00, $/client, , 2027-05-31, , CONTRACTED, strategy/strategic-plan.md Section 4
konji_canvassing_bonus_spring, labor_cost, "Konji per-spring-client-signed bonus", 20.00, $/client, , 2027-05-31, , CONTRACTED, strategy/strategic-plan.md Section 4
konji_winter_project_rate, labor_cost, "Konji winter business-side project rate", 25.00, $/hr, , 2027-05-31, , CONTRACTED, strategy/strategic-plan.md Section 4
```
After 2027-05-31, only the post-phase-switch base-rate row applies — the absence of a later row for revenue share/canvassing/winter-project *is* the "no share, no bonuses" statement, per D4, rather than needing an explicit zero row. This atomic-per-component design mirrors D2's own founding principle ("itemized by role, never a raw blended entry") — Konji's real compensation structure genuinely has this many independent parts, and collapsing them into one blended number would repeat the exact mistake D2 was written to prevent.

### 3.4 Xavier's payout and the owner's truck-debt — trigger conditions, not dates

Both are **demand-triggered on a state condition** (the $6,000 buffer being intact), not a calendar date — `strategy/strategic-plan.md`'s own Equipment Investment Plan table already states this precisely ("Trigger: Reserve intact; external before internal"). Proposed representation: a plain-text `trigger_condition`, evaluated by the calculation engine against the *projected* trajectory (Section 4), not computed inside the CSV itself — consistent with this repo's general preference for explicit, human-auditable text over implicit logic buried in a cell formula:

```
xavier_payout, capital_obligation, "Xavier equity payout", 1800.00, $, , , "cash_buffer_target reached (projected balance >= $6,000)", TARGET, CONTEXT.md Section 6 item D / strategy/strategic-plan.md Section 6 Phase 3
owner_truck_debt_repayment, capital_obligation, "Owner truck-debt repayment", 3800.00, $, , , "xavier_payout completed", TARGET, CONTEXT.md Section 6 item D / strategy/strategic-plan.md Section 6 Phase 3
```
The exact Xavier figure is itself still `~$1,800 (exact figure not yet confirmed)` per the Assumptions Log — carried through as-is, not rounded or firmed up here.

### 3.5 Anais's compensation — explicitly excluded, not guessed

Follow-Up #11: her canvassing rate and backup crew-lead rate are not yet specified anywhere. Proposed:

```
anais_canvassing_rate, labor_cost, "Anais canvassing rate", 0.00, $/hr, , , , BLOCKED, CONTEXT.md Follow-Up #11
anais_backup_lead_rate, labor_cost, "Anais backup crew-lead rate", 0.00, $/hr, , , , BLOCKED, CONTEXT.md Follow-Up #11
```
**The calculation must treat `BLOCKED` rows as excluded-with-a-stated-caveat, not as `$0` silently summed in** — the same distinction `build_model.py`'s Monthly P&L already draws for materials (shown as the literal text "BLOCKED," never folded into a numeric total as if it were a real zero). Confirmed recommendation: exclude Anais's cost from the trajectory entirely until the rates exist, with the sheet stating this gap on its face — do not invent a placeholder number.

### 3.6 Forward crew-labor-cost assumption — a genuine, flagged design choice

D2's reframed 2-person/50-50/$25-$20 model is available as-is:
```
crew_labor_model, labor_cost, "D2 planning model: 2-person 50/50 split", 22.50, $/hr blended, , , , TARGET, CONTEXT.md D2 (reframed H-049)
```
But Section 2.4's fresh computation shows real recent crew spending (~$1,870.61/mo) already running ~90% above what that model implies (~$977.68/mo). **This is flagged as a genuine, non-obvious design choice, not decided here:** project forward crew labor from (a) D2's static planning model, (b) the real recent-trend average, or (c) some blend. Section 6 records this for sign-off with a recommendation.

**Superseded, post-implementation (H-052 amendment):** option (b) as originally scoped — a flat recent-trend average applied to every projected month uniformly — was implemented, then investigated further before being trusted, per the owner's explicit instruction not to treat the resulting negative-balance finding as final without checking whether crew labor is itself seasonal. It is (Section 4's revision, above): crew labor is now projected seasonal-naive (prior-year same-month × a crew-labor-specific growth rate), not as a flat monthly constant. Option (b)'s "recent-trend average" framing is retired in favor of this finer-grained, seasonally-aware version of the same underlying idea (real, recent data — just not collapsed into one flat number that ignores the calendar).

---

## 4. Proposed cash-trajectory calculation method (Step 4)

**Where it lives:** replace the existing "Plan vs Actual" stub in `build_model.py` (`build_plan_vs_actual()`) — this is the sheet's originally-reserved purpose, already correctly named, already flagged since H-047 as pending exactly this build. No new sheet needed; the reserved slot should finally be filled rather than adding a redundant one alongside a still-empty stub.

**Method — month-by-month accumulation from the last real data point:**
1. **Starting point:** `cash_starting_balance` (Section 3.2), dated. Every month between its date and the ledger's last real month is filled from *actual* ledger data (collected − labor − overhead), not projected — the projection only begins after the last real month.
2. **Each subsequent month M**, project:
   - **Revenue:** seasonal-naive — take the *actual* collected revenue from month `M − 12` and scale it by an observed recent YoY growth rate (Section 2.3's +75.9%, or whatever rate Section 6 settles on). This is a standard, transparent technique directly derived from real data — not a fitted curve, which a single observed seasonal cycle can't responsibly support.
   - **Crew labor cost:** **revised, post-implementation (H-052 amendment) — seasonal-naive, not a flat trend.** Section 3.6 originally resolved "recent-trend average vs. D2's static model" without asking whether crew labor is seasonal at all; that question turned out to matter. Investigated directly: crew labor correlates with revenue seasonally (r=0.77 vs. billed revenue, r=0.69 vs. collected, over the cleanest 13-month window with full data coverage on both sides — June 2025–June 2026). The starkest evidence is that crew labor and revenue both go to **exactly $0** in January and February 2026 — confirmed *not* a hiring-gap artifact (Konji's first labor row is 2025-05-19, nine months before this gap; every other crew member also has zero rows in both months). A flat trailing-3-month average (the original design) would have wrongly carried ~$1,870/mo of crew cost into a projected January or February, when the real historical pattern shows it collapsing to zero — materially overstating projected winter cash burn. **Now projected the same way as revenue:** prior-year same-month crew labor × a crew-labor-specific growth-rate assumption (see the new open decision below — crew labor's own observed YoY growth, 92.8%, differs materially from revenue's 75.9%, since Konji's staffing ramp-up is a cost driver independent of revenue volume).
   - **Overhead:** flat-continue the most recent 1–3 actual months (overhead is mostly fixed monthly contracts, not seasonal, so a trend-scaling approach used for revenue doesn't apply here).
   - **Konji's phase-switch:** a discrete step-change applied to the crew-labor-cost and revenue-share terms the calendar month `konji_*` assumption rows' `effective_date`/`end_date` cross June 2027 — not a separate branch of logic, just the natural result of reading time-varying assumption rows for the month in question.
   - **Xavier/owner triggers:** evaluated *after* each month's running balance is computed — the first month the projected balance is `>=` `cash_buffer_reserve + cash_buffer_truck_hedge` ($6,000), subtract `xavier_payout`'s value as a one-time outflow that month; the first month *after* that where the balance again clears $6,000, subtract `owner_truck_debt_repayment`'s value. This is why `trigger_condition` is evaluated by the engine against the live projection, not pre-computed into a static date in the CSV.
3. `projected_cash[M] = projected_cash[M-1] + projected_revenue[M] − projected_outflow[M] − (any triggered one-time payout that month)`.

**Uncertainty — a range, not a point estimate, and this is a real design choice, not a default.** Section 2.5 already showed the same starting data supports outcomes from "buffer reached in ~2.4 months" to "~27 months," a 10x+ spread — presenting one number would be false precision the ledger's own thin history (13 months of billed data, one full seasonal cycle) cannot support. **Recommendation: show three scenarios side by side** — a low bound (full-cycle average net rate, no growth assumption), a mid bound (the growth-adjusted seasonal-naive method above), and — if the owner wants it — a high bound (a more optimistic YoY rate). Each scenario's own arithmetic should be fully shown (per this repo's arithmetic-self-check discipline), not just a final number.

---

## 5. Worked example — projecting August 2026 (Step 5)

**Superseded by implementation and a follow-on investigation (H-052 + H-052 amendment) — this section originally hand-computed a single flat-trend month and naively straight-lined it across the whole buffer gap. Both the crew-labor method and the "months to buffer" framing below were corrected once the real code was built and the crew-labor-seasonality question was investigated. The corrected figures (from the actual generated workbook, not a hand estimate) are shown here in place of the original illustration.**

August 2026 is the next full calendar month after the ledger's last real data point (July 2026's own ledger data is partial — labor's last completed period starts 2026-06-15, per H-050 — so July itself cannot yet be projected cleanly; this worked example shows one link in the chain, not a fully resolved multi-month projection, since July's own actuals aren't complete at the time of this document).

**Revenue (seasonal-naive, growth-adjusted):**
- August 2025 actual collected: $2,659.70
- Revenue growth-rate assumption (`assumptions.csv`, rounded from the raw observed +75.884%): **75.9%**
- Projected August 2026 revenue: $2,659.70 × 1.759 = **$4,678.41** (differs by $0.42 from a hand-calc using the raw unrounded rate — immaterial, and expected, since the assumption is deliberately stored rounded, not as a silently-carried float)

**Outflow (seasonal-naive crew labor, per Section 4's revised method — NOT the flat recent-trend average originally proposed here — plus flat-continued overhead):**
- August 2025 actual crew labor: $743.45
- Crew-labor growth-rate assumption (`assumptions.csv`, Decision 11, not yet owner-confirmed): **92.8%**
- Projected August 2026 crew labor: $743.45 × 1.928 = **$1,433.37**
- Recent 3-month overhead average: ($621.36 + $617.77 + $1,169.92) ÷ 3 = **$803.02**
- Projected outflow: $1,433.37 + $803.02 = **$2,236.39**

**Projected net for August 2026:** $4,678.41 − $2,236.39 = **$2,442.02**

**What this implies for the buffer timeline** (gap from the $1,225.33 verified starting cash to the $6,000 target = $4,774.67), shown across all three Section 4 scenarios rather than picking one — the High scenario now run as a genuine month-by-month trajectory (not a single strong month straight-lined across the whole gap):

| Scenario | Monthly net rate / method | Result |
|---|---|---|
| Low (flat-continue June 2026's actual net) | **−$943.12/mo** (negative) | Never reaches the buffer at that rate |
| Mid (full seasonal-cycle average) | $174.43/mo | **~27.4 months** (~late 2028) |
| High (seasonal-naive month-by-month, revised crew labor) | varies by month, seasonal | **Reaches $6,000 in June 2027 (~11 months)**, triggering Xavier's payout — balance stays positive throughout, dipping to a low of $865.47 in April 2027 |

**This is a materially different and more honest picture than the original single-month extrapolation implied.** A naive straight-line of August's own strong net rate ($2,442.02/mo, or the pre-correction $2,004.36/mo) across the $4,774.67 gap suggested ~2 months — but the real month-by-month trajectory shows negative-net months every winter (crew labor and revenue both collapse toward $0 in January/February, mirroring the real historical pattern) alternating with strongly positive months, and the buffer is genuinely reached only after riding out one full additional seasonal cycle, in June 2027. Before the crew-labor-seasonality correction, running the same month-by-month mechanic with a flat crew-labor trend produced an even worse-looking, and wrong, result — the balance went negative for six straight months (Oct 2026–Apr 2027) and never reached $6,000 within the horizon, because a flat ~$1,870/mo crew-labor cost was being wrongly charged even in months where real crew labor historically drops to zero. This is exactly why the three-scenario range (Decision 6) and the seasonal-naive method (Decision 11) both matter: a single point estimate, or an unexamined flat-trend cost assumption, would have produced a materially wrong answer to "when does the plan's buffer target get reached."

---

## 6. Open decisions requiring sign-off (Step 6)

1. **Are the existing monthly/quarterly targets (Jul '26 $4,140 → Jun '27 $9,180) dead, or should they be preserved as a comparison baseline alongside the recomputed trajectory?** *Recommendation:* supersede them (they're built on the stale $4,500 anchor, and the source documents themselves say to), but preserve the old table in `strategy/strategic-plan.md`'s Revision Note per the repo's changelog-preservation convention — don't delete.
2. **Should `CONTEXT.md` Section 3's "$4,908 is the strongest month to date" be corrected to cite June 2026's $6,019.89 now, or held until this projection layer is actually built?** *Recommendation:* correct it now, as its own small fix, independent of whether/when the rest of this plan is implemented — it's a plain factual staleness, already caught, cheap to fix, and Standing Rule 3 says not to keep citing a superseded number once found.
3. **Forward crew-labor-cost assumption: D2's static planning model, or the real recent-trend average (Section 2.4/3.6)?** *Recommendation:* the recent-trend average, re-derived from the ledger at each build (not hardcoded as a fixed number even as the "data-derived" choice) — D2's model already undershoots real spending by ~90% and was explicitly reframed as forward-looking-only, not sacred; letting it silently understate cost risk in the one place the business most needs an honest cash forecast doesn't serve the plan's own stated purpose. But this is a real trade-off (recent-trend risks overreacting to a temporary staffing blip) and belongs to the owner, not a default. ***Resolved and superseded, post-implementation (H-052 amendment):*** implemented as a flat recent-trend average first, then investigated and found materially wrong for winter months (see Section 4's revision) — crew labor is genuinely seasonal (r=0.77 vs. billed revenue), so it's now projected seasonal-naive like revenue, not as a flat monthly constant. This closes Decision 3 but opens **Decision 11** below.
11. **RESOLVED (H-053, owner-confirmed 2026-07-10) — which growth rate should scale crew labor's seasonal-naive projection: revenue's own growth rate (75.9%), or crew labor's own separately-observed growth rate (92.8%)?** Both are real, computed the same way (Apr–Jun 2025 vs. Apr–Jun 2026), but they diverge materially — crew labor has grown faster than revenue, plausibly because Konji's move to weekday crew lead is a staffing decision, not purely a volume-driven cost. Using revenue's rate implicitly assumes crew cost scales proportionally with revenue; using crew labor's own rate assumes the recent staffing ramp-up continues at its own pace. This plan's own recommendation (crew labor's own rate, 92.8%) was implemented first, then **explicitly rejected by the owner in favor of revenue's rate (75.9%)** — the two assumption rows were unified rather than kept as manually-synced duplicates (`model/data/assumptions.csv`'s standalone `crew_labor_growth_rate_assumption` row removed; `revenue_growth_rate_assumption` is now the single shared rate `model/build_model.py` references for both calculations). Under the resolved 75.9% rate, the High scenario's buffer-reached date moved one month earlier (May 2027, not June) and — for the first time — the owner's truck-debt repayment also triggers within the horizon (June 2027), not just Xavier's payout. See `HISTORY.md` H-053 for the full re-run and re-verification.
4. **How should Anais's cost be handled?** *Recommendation:* excluded entirely with a stated caveat on the sheet's face (per Section 3.5) until Follow-Up #11 resolves her rates — never a placeholder number.
5. **How should Xavier/owner trigger conditions be expressed and evaluated — plain-text `trigger_condition` read by the calculation engine against the live projection (Section 3.4/4), or some other mechanism?** *Recommendation:* the plain-text approach as designed — auditable, consistent with this repo's preference for explicit statements over implicit computed logic.
6. **Uncertainty representation: a single point projection, or the three-scenario range (Section 4/5)?** *Recommendation:* the range — a point estimate would be false precision given how thin the underlying history is (13 months of billed data, one full seasonal cycle), and Section 5's worked example shows the spread between scenarios is enormous (never vs. ~2.4 months to the buffer).
7. **`assumptions.csv`'s status vocabulary (TARGET/POLICY/CONTRACTED/DERIVED/BLOCKED/ACTUAL, Section 3) is new and distinct from the ledger's ACTUAL/ESTIMATE/BLOCKED — confirm this is acceptable, or propose an alternative.** *Recommendation:* adopt it as proposed; conflating "a target" with "a measured fact" under one vocabulary would blur exactly the distinction D6 exists to preserve.
8. **Konji's exact rate-change effective date (Section 3.3) is not yet knowable — his negotiated $25/hr rate hasn't run in any payroll period as of the current exports.** *Recommendation:* leave the `end_date`/`effective_date` blank/open until the next Gusto payroll refresh (per `reference/PAYROLL-UPDATE.md`) surfaces the real date, rather than guessing one now.
9. **`cash_starting_balance`'s periodic re-verification (Section 3.2) — should this get its own standing update procedure (mirroring `CATALOG-UPDATE.md`/`REVENUE-UPDATE.md`/`PAYROLL-UPDATE.md`), or is an ad hoc re-check at each Cash Buffer Policy check-in sufficient?** *Recommendation:* out of scope for this pass; flagged so it isn't forgotten, not solved here.
10. **Should the growth-rate assumption feeding the seasonal-naive revenue projection (Section 2.3/4/5) be pinned to the observed +75.9% collected-cash YoY figure, or should the owner set a separate, more conservative planning growth-rate assumption independent of the raw observed number?** *Recommendation:* make it its own labeled `assumptions.csv` row (e.g. `revenue_growth_rate_assumption`) rather than hardcoding the observed figure into the calculation — exactly the kind of number D6 requires be a labeled assumption cell, even when it's derived from real data.
