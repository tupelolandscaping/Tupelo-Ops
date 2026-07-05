# Check-In Template — Arlington Landscaping

**How to use:** Paste this whole block at the start of each check-in chat in the project. Fill Section 0 (carried-forward state) and Section 1–2 (current numbers) before sending; leave the rest for Claude. Claude reads today's date automatically — you do not need to supply it. At the end, Claude returns an updated Section 0 for you to paste into the *next* check-in. That carried-forward block is the memory bridge between sessions.

**Cadence:** Target ≤2 weeks between check-ins July–December (high-activity); monthly January–June. Timing can be sporadic — what matters is the gap, not the day of week.

---

## 0. Carried-Forward State *(fill from last check-in's output)*

- **Last check-in date:** ___
- **Last bank balance (cash buffer):** $___
- **Crew-lead status last time:** Konji ___ / backup ___
- **Systems-built % last time:** ___%
- **Cumulative leads captured last time:** ___
- **Open items carried in** (what was outstanding/blocked): ___
- **Pending file-updates queue** (edits agreed but not yet applied to project memory): ___

*(First check-in only: write "baseline — no prior state." Claude will establish the starting values.)*

---

## 1. Pulse Check — Tier 1 leading indicators *(every check-in)*

- **Cash buffer — raw bank balance, AS OF [date]:** $___
  - Reference: $4k business reserve / $6k target (see Cash Buffer Policy in the timeline)
- **Leads captured — cumulative YTD:** ___ total
  - By tag: interested-spring ___ / has-service-declined ___ / one-off project ___ / booked ___
- **Crew-lead status:**
  - Konji: [decided? yes/no/pending — date] · Backup: [identified? cross-trained?]
- **Systems-built %:** ___% of Owner→Lead transfer checklist + Homeworks config
  - (Or list which items closed since last time.)

## 2. Tier 2 — Homeworks forward-looking pulls *(every check-in, near-zero cost)*

- **Revenue Forecast (Homeworks):** $___
- **AR Aging (Homeworks):** any balances at 30 / 60 / 90+ days? ___
- **Customer Source (Homeworks):** channel mix — door ___ / sign ___ / referral ___ / online ___
  - (The question this answers: is acquisition shifting *off* door-to-door, as the strategy requires?)

## 3. Milestone Status *(every check-in)*

- **Calendar-anchored items due since last check-in** (pull the dated [ANCHOR]/[GATE] items from the Execution Timeline for the elapsed interval):
  - For each: ✅ complete / ◐ in progress / ⛔ blocked. If blocked → what's blocking.
- **Any tripwire conditions hit?** (Konji deadline, $4k floor, Nov-1 checklist <70%, truck event) ___

## 4. Tier 3 — Monthly calibration *(skip on biweekly check-ins; run ~once a month)*

- P&L (billed **and** collected) · Revenue by Customer · Revenue by Crew · Inactive / Written-Off Customers · Revenue by City/County · Truck Mileage
- **Period label for each:** state the date range (YTD unless noted).
- Purpose: reconcile model assumptions against actuals; feed any assumption breach into the file-update protocol.

---

## 5. What Claude Assesses & Outputs *(leave blank — Claude fills this)*

Claude, using the sections above + the Execution Timeline + the variance matrix below:

1. **Elapsed time:** compute days since last check-in; flag if >14 (Jul–Dec) or >31 (Jan–Jun).
2. **Curve comparison:** compare each Tier 1 metric to the plan curve (timeline's Monthly Financial Targets table) and to last check-in's value (delta).
3. **Classify each divergence** via the variance matrix — which milestone type × recoverable-or-breach × single-or-trend.
4. **Decision per divergence — exactly one of:**
   - **STAY** — within tolerance; no action.
   - **ADJUST** — reschedule/tighten a timeline item; log it; no model change.
   - **ESCALATE** — structural breach or invalidated assumption → open a re-planning / file-update pass.
5. **Pending file-updates:** list any new entries for the queue (Tier B status updates or Tier C model re-runs), with the specific edit drafted.
6. **Updated Section 0:** regenerate the carried-forward state block with today's values, so it can be pasted into the next check-in.

---

## Variance Matrix *(reference — how STAY/ADJUST/ESCALATE is decided)*

**First screen — which milestone does the divergence touch?**
- **Demand-triggered ([DT]) item:** floats by design → almost never a problem → STAY / log.
- **Calendar-anchored / load-bearing item:** proceed to the matrix below.

**Second screen — recoverable within slack, or breach?**

| | **Single occurrence** | **Trending (2+ check-ins, same direction)** |
|---|---|---|
| **Recoverable within slack** | Noise → **STAY**, log | Watch → **ADJUST**, tighten focus, no re-plan |
| **Breaches a buffer/gate** | Contingency event → activate pre-built response (truck rental, backup lead) — not re-planning | **ESCALATE** → re-plan / file update |

- **Re-planning is reserved for the bottom-right cell** — a *sustained* divergence that *breaches a structural limit.* Everything else is absorbed, watched, or handled by contingency.
- **Posture (confirmed):** trend required for *flow* metrics (revenue, leads, margins) before ESCALATE; *binary gate* breaches (crew-lead deadline, $4k floor, handoff checklist) act on a single occurrence.

---

## Reference Conventions

**Data periods**
- Cash / reserve: point-in-time — "as of [date]."
- Flow metrics (revenue, leads, expenses): **YTD**; per-interval delta is derived by differencing against last check-in's carried-forward figure.
- Never compare a YTD figure to a monthly target.

**Cash buffer** (full policy lives in the Execution Timeline)
- Raw bank balance. $4k business reserve (hard floor) + $2k truck hedge = $6k target.
- Below $4k → freeze scaling + debt repayment. Truck event drawing ~$6k→$4k = expected absorption, not a breach. Repay Xavier/owner only above $6k.

**File-update protocol** (full version in the Strategic Plan / Item 4 design)
- **Tier A — log only:** routine variance, single data points, in-progress items → stay in this chat.
- **Tier B — status update:** a load-bearing fact changed state → lightweight edit to the durable file (batched ~monthly).
- **Tier C — model re-run:** an *assumption* invalidated with a representative sample behind it → re-run model, cascade targets, preserve original values in the changelog.
- Changes decided here are drafted by Claude, applied by you on upload, and tracked in the pending-updates queue until applied.

---

## First-Time Setup Notes

- The very first check-in establishes baselines: current bank balance, current lead count (likely ~0 captured if capture just started), Konji status, and a systems-built % of roughly 0 against the Owner→Lead checklist.
- Expect the first ~4–6 weeks of check-ins to partly calibrate the *timeline itself* — if you're consistently ahead or behind, that's information about the estimates, not only execution. Adjust pace at the revision points.
