---
title: Fixed Overhead — Contracted Figures
type: reference
status: sourced (owner-supplied)
date: 2026-07-04
source: owner-provided (Cyrus), 2026-07-04
tags: [overhead, fixed-costs, insurance, payroll, crm, reference]
---

# Fixed Overhead — Contracted Figures

**Purpose.** Ground-truth record of the actual contracted amounts behind the business's fixed monthly overhead, so the financial model's overhead lines trace to a real source (per `CONTEXT.md` Section 6 item I; reconcilable by the D8 self-check). This lives in `reference/` and is **never edited except to record a new contract term** — append, don't overwrite, and log the change in `HISTORY.md`.

**How to read the table.** *Contract term* is the amount exactly as billed. *Monthly-equivalent* amortizes non-monthly premiums evenly across their term (annual ÷ 12, semi-annual ÷ 6) so a monthly P&L can use one figure. Status tags: **ACTUAL** = current contracted figure; **BLOCKED** = a change that is coming but not yet quantified (do not model it until a real number exists).

| Item | Contract term (as billed) | Cadence | Monthly-equivalent | Status | Renewal / notes |
|---|---|---|---|---|---|
| Gusto (payroll provider) | $49 base + $6/person/mo → **$127/mo** | Monthly | $127.00 | ACTUAL | Headcount-dependent (semi-variable). At $127 the formula implies **13 people on payroll** ($49 + $6×13). Each person added/removed = ±$6/mo. |
| General Liability Insurance | $33.75/mo | Monthly | $33.75 | ACTUAL | Renews **2026-09-05**; likely slight increase — post-renewal amount **BLOCKED** until quoted. |
| Workers' Compensation Insurance | $544 / year | Annual (lump) | $45.33 | ACTUAL | Renews **2026-11-30**; likely slight increase (BLOCKED). Cash outflow is a **lump sum on renewal**, not a monthly debit. |
| Commercial Auto Insurance | $999 / 6 months | Semi-annual (lump) | $166.50 | ACTUAL | Renews **2026-10-09**; likely slight increase (BLOCKED). **Separately**, adding Konji as an insured driver raises the premium — BLOCKED pending quote (`CONTEXT.md` item J). Cash outflow is a lump sum on renewal. |
| Homeworks (CRM) | $299/mo | Monthly | $299.00 | ACTUAL | Optional annual billing = $2,628/yr (**$219/mo-equivalent, saves ~$80/mo**) — a future election "when capital allows," not current. |
| Squarespace (website) | $25/mo | Monthly | $25.00 | ACTUAL | Planned cancellation; to be replaced by Claude Pro at $20/mo (or $200/yr = $16.67/mo-equivalent). See follow-up #12(b). Not yet changed. |

**Current monthly fixed overhead (contracted, ACTUAL): $696.58/month** (= **$8,359/year**).
Component sum: 127.00 + 33.75 + 45.33 + 166.50 + 299.00 + 25.00 = 696.58.

## Notes for the model rebuild

- **Accrual vs. cash (ties to D5a).** The monthly-equivalent column is the *amortized accrual* figure for a monthly P&L. The actual *cash* events for the annual (workers' comp) and semi-annual (commercial auto) premiums are **lump sums on their renewal dates** — model those as dated cash outflows, not monthly debits, the same way billing and payment are separated for revenue.
- **Equipment maintenance is NOT included here.** It stays BLOCKED until an allocation base and method are stated (`CONTEXT.md` item I). Adding it will raise the total above $696.58.
- **Reconciliation to the plan.** This contracted total ($696.58/mo, excluding maintenance) essentially matches the strategic plan's earlier **~$695/mo** estimate (which nominally *included* maintenance). So the itemized contracts supersede that rough figure, and any maintenance allocation is net-new on top of $696.58 — the old estimate slightly understates true fixed overhead once maintenance is added.
- **Fall renewal cluster.** Three renewals fall in a tight window and each is expected to rise: general liability (2026-09-05), commercial auto (2026-10-09), workers' comp (2026-11-30). Treat every post-renewal amount as BLOCKED until its quote lands, then append the new term here and log it.
- **Headcount sensitivity.** Gusto scales at $6/person/mo; both the crew-reduction decision (follow-up #1) and the time-tracking seat question (#2) move this line.
- **Homeworks (CRM) here is the flat $299/mo subscription only — do not conflate with the separate, transactional 1% Homeworks platform markup on card payments.** That markup (confirmed 2026-07-12, `HISTORY.md` H-063) is a per-charge cost blended into the `Stripe, payment-processing-fee` ledger category (`model/data/ledger-overhead.csv`), not a fixed monthly line — it scales with card-paid revenue volume, not headcount or a contract term, and is not part of this file's $696.58/mo total. The two are structurally unrelated costs that happen to share the Homeworks name: one is what the business pays Homeworks for the CRM software itself (this row), the other is what Homeworks keeps out of every card charge it routes through Stripe (H-062/H-063).
