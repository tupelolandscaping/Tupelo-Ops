# RUNBOOK — Tupelo-Ops: Repository Setup Through First Model Build

**What this is.** A linear, checkable execution guide that operationalizes Section 10 of `CONTEXT.md`. Work top to bottom; each phase gates the next. `CONTEXT.md` is the *reference* (the why and the specs); this runbook is the *procedure* (the what, in order).

**How to use it.**
- Do the phases in order. Do not skip ahead — later phases assume earlier ones are done.
- Each step is a checkbox. `[ ]` = not done, `[x]` = done. Check it only when the **Done when** condition is true.
- **Two kinds of step:** 🧑 **OWNER** = you do it by hand (uploads, decisions, external sessions). 🤖 **CLAUDE CODE** = you instruct Claude Code in the Codespace to do it, then review its output. Steps unmarked are simple owner actions (clicks/commands).
- **Commit discipline:** commit in small, labeled pieces (the whole point of the migration). A good commit message says *what changed and why* in one line.
- **Product UIs drift.** Where a step depends on a GitHub or Claude Code interface, the described flow is the current standard; if the UI differs, follow the on-screen path for the same goal or ask Claude Code — don't force a stale click-path.

---

## Phase 0 — Prerequisites (confirm before starting)

- [x] GitHub account active, signed in. *(Owner-confirmed 2026-07-10. Also inferable: the repo has had commits pushed to `origin/main` under the business GitHub account throughout this session.)*
- [x] VS Code Desktop installed, with its built-in Git and the GitHub/Codespaces integration. *(Owner-confirmed 2026-07-10. Also inferable: the live Codespace this session runs in could only have been opened via this integration.)*
- [x] Claude Code installed and authenticated (your existing work setup). *This runbook assumes familiarity with Claude Code in VS Code; it does not re-teach install.* *(Directly confirmed: this session is itself an authenticated Claude Code session running in this Codespace — `code --list-extensions` also shows `anthropic.claude-code` installed.)*
- [x] You have every file in the **Phase 2 upload manifest** ready to hand (Phase 2 is the single authoritative list — don't maintain a second copy here; just confirm you can produce all of them). *(Owner-confirmed 2026-07-10; also inferable from Phase 2/3 having succeeded.)*

**Done when:** all four boxes are true. *(2026-07-10 sync: owner-confirmed; three of four also independently inferable from repo/session state — see per-item notes.)*

---

## Phase 1 — Create the repository and open a Codespace

- [x] Create a **new, empty, private** GitHub repository named exactly **`Tupelo-Ops`** under the **business's dedicated free GitHub account** (registered under the business email — not your personal or work account). Initialize it with a README so it's clonable (you'll overwrite that README later). *If you already created it under a personal account, recreate it under the business account and delete the personal copy — the repo is nearly empty, so recreating is cleaner than transferring.* *(`git remote -v` confirms `https://github.com/tupelolandscaping/Tupelo-Ops`; `eeff63a "Initial commit"` is the repo-init commit; H-020 documents business-account hosting. Private/visibility status is not verifiable from repo contents — a GitHub setting, not a file trace.)*
- [x] Open the repo in a **Codespace** via VS Code Desktop (GitHub repo → Code → Codespaces → create; or the VS Code "Create Codespace" command). Wait for it to finish building and attach. *(Directly observable in the current live session: `$CODESPACES=true`, working directory `/workspaces/Tupelo-Ops` — the Codespace path convention. Not a repo-file citation, but a direct environment fact, not inference.)*

**First-bring-up environment check** (this becomes `SETUP.md` in Phase 4):

- [x] In the terminal, confirm tooling: `node -v`, `npm -v`, `git --version` each return a version. *(Owner-confirmed as done 2026-07-10; re-verified fresh this same day: node v24.14.0, npm 11.9.0, git 2.53.0 — all present, unchanged from the 2026-07-09 reading.)*
- [x] Set git identity so commits succeed: `git config user.name "Your Name"` and `git config user.email "you@example.com"`. *(Confirmed: all repo commits are authored under `Cyrus <tupelolandscapingllc@gmail.com>` or `tupelolandscaping <tupelolandscapingllc@gmail.com>` — the business email, not a personal one — proving identity was set correctly, not just set.)*
- [x] Confirm Claude Code is authenticated to the correct account. *(Owner-confirmed 2026-07-10; also directly evident — this session is itself running as an authenticated Claude Code session.)*
- [x] Confirm Python: `python3 --version`. *(Owner-confirmed as done 2026-07-10; re-verified fresh this same day: Python 3.12.1.)*
- [x] Install VS Code extensions (Extensions panel): **Python** (Microsoft; bundles Pylance) and **Rainbow CSV** — essential. **GitLens** and an **Excel viewer** — optional. *(Directly confirmed via `code --list-extensions`, 2026-07-10: `ms-python.python` + `ms-python.vscode-pylance` (Python + Pylance) and `mechatroner.rainbow-csv` (Rainbow CSV) present — both essentials installed; `eamodio.gitlens` (GitLens) and `development42.csv-excel-viewer` (Excel/CSV viewer) also present — both optionals installed too. This checkbox was previously marked unverifiable; the CLI listing makes it directly checkable after all.)*

**Done when:** the Codespace is open in VS Code, the four tools report versions, git identity is set, and the two essential extensions are installed. *(2026-07-10 sync: all now confirmed — repo creation, Codespace, and git identity from repo evidence; tool versions, Claude Code auth, and extensions from a fresh live check plus owner confirmation.)*

---

## Phase 2 — Upload the source files 🧑 OWNER

*This phase is yours alone — Claude Code cannot reach files that live on your computer until you put them in the working tree.*

- [x] Create a temporary folder at the repo root named `incoming/`. *(Confirmed via commit `c1cfd9c "checkpoint: upload Phase 2 source files"` and `2fc197b`'s rename diffs, which show every baseline file moving `incoming/... → ...`. `incoming/` no longer exists now, consistent with its Phase 3 deletion.)*

**Upload into `incoming/`** (drag into the VS Code Explorer, or use the upload command). **This is the single authoritative upload manifest — every file any later phase consumes must appear here:**

- [x] `Strategic_Plan_2026-2027.md` *(→ `strategy/strategic-plan.md`, exists)*
- [x] `Operational_Toolkit.md` *(→ `strategy/operational-toolkit.md`, exists)*
- [x] `CheckIn_Template.md` *(→ `check-ins/check-in-template.md`, exists)*
- [x] `Execution_Timeline_2026-2027.md` *(→ `strategy/execution-timeline.md`, exists)*
- [x] `Landscaping_Financial_Model_3.xlsx` *(→ `reference/landscaping-financial-model-3.xlsx`, exists)*
- [x] the CRM CSV exports — six files: services, expenses, revenue-by-customer, source, sales-tax, and the payment-type breakdown (the second "services" file, `services__..._1.csv`, which is actually a payment-method report) *(all six present in `reference/`: `services__...csv`, `services__..._1.csv`, `expenses__...csv`, `revenuebycustomer__...csv`, `salestax__...csv`, `source__...csv`)*
- [x] the P&L report `report_profit_and_loss_2.pdf` *(exists in `reference/`)*
- [x] the Relay bank statements (all the `Relay YYYY-MM-DD #NNNN.csv` files — note spaces and a `#`, not underscores; some are marked `Relay (Partial) YYYY-MM-DD #NNNN.csv`) *(85 Relay CSVs confirmed by H-006; `reference/` currently holds those plus the later Part-4 additions)*
- [x] `CONTEXT.md` (revision 6) and `RUNBOOK.md` (this file) — the two documents you're working from *(both at repo root)*
- [x] 🧑 **Fixed-overhead contract figures** — the actual amounts behind insurance, workers' comp, commercial auto, payroll provider, and CRM subscription (a short file or note). These are **owner-supplied**: they are not in any CRM export (the CRM's expense buckets are too coarse — that is *why* Phase 5 item I needs them), and Claude Code must not invent them. If you don't have them yet, that's fine — but Phase 5 item I and the overhead portion of Phase 7 are blocked until you do. *(`reference/fixed-overhead.md` exists; H-005 confirms owner-supplied 2026-07-04.)*

**Done when:** every listed file is visible in `incoming/`. *(2026-07-09 sync: `incoming/` itself is gone — correctly, per Phase 3's cleanup step — but every listed file is confirmed present at its Phase-3 destination, which is the same fact one step later.)*

---

## Phase 3 — Populate the baseline and commit it 🤖 CLAUDE CODE

*Goal: get the files into their repo homes **unedited**, and commit that untouched state, so the "before" is preserved in history before any correction.*

- [x] Instruct Claude Code to create the folder structure: `strategy/`, `check-ins/`, `model/data/`, `reference/`. *(All four exist; confirmed by directory listing and commit `2fc197b`.)*
- [x] Move and **kebab-case rename** the already-Markdown files:
  - `CheckIn_Template.md` → `check-ins/check-in-template.md`
  - `Execution_Timeline_2026-2027.md` → `strategy/execution-timeline.md`
  *(Both exist at destination; `2fc197b`'s diff shows the exact renames.)*
- [x] Move and **kebab-case rename** the two strategy documents (they arrive as Markdown — no conversion needed):
  - `Strategic_Plan_2026-2027.md` → `strategy/strategic-plan.md`
  - `Operational_Toolkit.md` → `strategy/operational-toolkit.md`
  *(Both exist at destination.)*
- [x] Place raw source data in `reference/` unedited: the CRM CSV exports, the P&L report `report_profit_and_loss_2.pdf`, all Relay statements, **the source workbook `Landscaping_Financial_Model_3.xlsx`** (→ `reference/landscaping-financial-model-3.xlsx` — it is ground truth that Phase 7 decomposes and Phase 5 item F reads for `B43`), and **the fixed-overhead contract figures** if uploaded. *(All present per the Phase 2 file-by-file check above; `2fc197b` + H-006.)*
- [x] Move `CONTEXT.md` and `RUNBOOK.md` to the repo root. *(Both present at root; `2fc197b`'s diff shows `incoming/CONTEXT.md => CONTEXT.md` and `incoming/RUNBOOK.md => RUNBOOK.md`.)*
- [x] Confirm `incoming/` is now genuinely empty (every file has been moved to its home), then delete it. *If anything remains, it means a file has no destination — resolve that before deleting, don't delete files with the folder.* *(`incoming/` does not exist in the current tree — confirmed by direct check.)*
- [x] **Commit the unedited baseline:** stage all, commit with a message like `baseline import — unedited source files in repo homes`. Do **not** apply any content corrections yet. *(As with every 🤖 commit step below: Claude Code stages and prepares the commit, then pauses for your review before committing — it does not auto-commit.)* *(Commit `2fc197b`, exact matching message; see H-006: 100 files, zero content changes.)*

**Done when:** `git log` shows the baseline commit, and no Phase-5 corrections have been made yet. *(Checkpoint: the repo now mirrors the old project workspace, just relocated — stale content and all. That staleness is intentional and gets fixed in Phase 5.)* *(2026-07-09 sync: confirmed via `2fc197b` and H-006 — all items citable to concrete repo evidence.)*

---

## Phase 4 — Author the scaffold files 🤖 CLAUDE CODE

*Build the files that make the repo self-governing. Specs are in `CONTEXT.md` Section 8.*

- [x] **`CLAUDE.md`** (queue item G) — per the Section 8 spec: project identity; standing rules + engagement preferences; architecture summary; the model-update operating procedure; the ground-truth rule; file conventions; the cross-reference check on structured edits; the history-logging rule; RAG-readiness conventions; deferred-tooling statement (Ruflo/RuVector not in use). Include the machine-global `~/.claude/CLAUDE.md` correctness note — and actually **check whether that global file exists** in this environment; if it does and carries Ruflo directives, the affirmative "deferred for this project" statement matters; if not, note it as not applicable. *(Exists at repo root; content matches this spec.)*
- [x] **`SETUP.md`** (G2) — the standalone new-Codespace guide (verify tooling, git identity, Claude Code auth, Python + `pip install -r model/requirements.txt`, extensions, Auto Save, sanity check). No Ruflo/RuVector steps. *(Exists at repo root.)*
- [x] **`README.md`** (G3) — repository map / entry point. *(Exists at repo root.)*
- [x] **`HISTORY.md`** (G3) — master append-only audit log; **seed** it from `CONTEXT.md`'s locked decisions and events so it starts populated. Include the `DECISION` entry for the cross-reference-legibility review check (basis: three review rounds where every surviving defect was join drift). *(Exists, currently H-001 through H-039 plus the undated D1–D10/H-018 foundational section; H-018 is the cross-reference-legibility DECISION entry.)*
- [x] **`.gitignore`** (G4) — exclude `model/financial-model.xlsx` and transient build artifacts. *(Exists; contents: `model/financial-model.xlsx`, `__pycache__/`, `*.pyc`, `.DS_Store`.)*
- [x] **`model/requirements.txt`** (G4) — pinned dependencies (start with `openpyxl`, pinned to a specific version). **Created here, once.** *(Exists: `openpyxl==3.1.5`; `pdfplumber==0.11.10` was appended later for `parse_invoices.py`, not a recreation — consistent with the "append, don't recreate" rule.)*
- [x] **Install the dependencies now:** `pip install -r model/requirements.txt`. (Creating the file does not install it — the build in Phase 7 will fail with `ModuleNotFoundError` if this is skipped. The architecture deliberately relies on the *installed, pinned* file, not on whatever the Codespace image happens to ship.) *(Directly confirmed 2026-07-10: `pip show openpyxl` → 3.1.5 and `pip show pdfplumber` → 0.11.10, both matching `requirements.txt`'s pinned versions exactly and both importable. `pdfplumber` was already confirmed working via `parse_invoices.py`'s runs (H-030 onward); `openpyxl`'s installation is now directly confirmed too, even though `model/build_model.py` hasn't been written yet to actually exercise it.)*
- [x] Commit, e.g. `add repo scaffold: CLAUDE.md, SETUP.md, README, HISTORY, gitignore, requirements`. *(Claude Code prepares the commit, then pauses for your review — it does not auto-commit.)* *(Commit `def8d9b "add repo scaffold: gitignore, requirements, CLAUDE, SETUP, README, HISTORY"`.)*

**Done when:** all six files exist and are committed, `.gitignore` excludes the workbook, and `HISTORY.md` is non-empty. *(2026-07-10 sync: true, per `def8d9b` and current file listing. The `pip install` sub-step is now also directly confirmed, not just inferred.)*

---

## Phase 5 — Clear the reconciliation queue 🤖 CLAUDE CODE

*Now apply the "decided, not yet applied" corrections to the imported files — each as its own small, reviewable commit. Full detail per `CONTEXT.md` Section 6, items B–D, F, H, I, J. (A, G, G2, G3, G4 are already done.)*

- [x] **B — Execution timeline:** mark the Konji tripwire resolved; backup-lead search active; add the end-of-July Job Costing anchor; correct GBP status (active, no reviews/leads); note no residual Konji family gate; add the auto-insurance / Konji-insured-driver decision point. *(Commit `174ef6d "correct execution timeline to current reality: Konji resolved, backup-lead active, GBP active, Job Costing anchored end-July"`; the operational-toolkit's parallel Konji item was also reconciled — commit `c665d99`, H-023.)*
- [x] **C — Strategic plan:** replace the placeholder crew-lead comp with Konji's finalized structure; check off "weekday crew lead secured." *(Commit `2ee485a`; H-021 confirms both the comp replacement and the checklist item.)*
- [x] **D — Assumptions log:** Xavier ~$1,800, unpaid, demand-triggered late winter, status Track (with the equity-vs-contingent-outflow reconciliation); starting cash → $1,400 tagged **interim ESTIMATE**, superseded by Phase 6 consolidation. Do not lock it as ACTUAL. *(Commit `2ee485a`, H-021 confirms the original Xavier/starting-cash entries as written here. **Further superseded since:** the starting-cash figure this item describes ($1,400 interim ESTIMATE) was itself replaced by the verified $1,225.33 ACTUAL when Gate A closed — see H-039 and `strategy/strategic-plan.md` Section 9's Revision Note. This box describes a since-superseded intermediate state, not the current one.)*
- [x] **F — Revenue anchor:** supersede `B43 = $9,562.71` with the current $12,726.01 billed / $10,973.57 collected; carry the anchor and Konji's 6% base as **gross-of-surcharge** pending the tax session (#10). *(Commit `de7e633 "record F and H as Phase 7 build-time instructions"`, H-024. Recorded as a build-time instruction, applied at the Phase 7 rebuild (now complete, H-047–H-050). **Correction (2026-07-09):** the "gross-of-surcharge" text above is superseded — H-031/H-032, recorded the very next day (2026-07-06), resolved this the opposite way: Konji's 6% revenue share is computed on **net** service revenue ($12,024.58 for the Jan–Jul 2026 window), excluding the $701.43 surcharge, not on the gross anchor. See `CONTEXT.md` Section 6 item F for the current, authoritative statement.)*
- [x] **H — Truck entry:** record the $5,000 April entry as a retroactive log of an owned asset, **not** a new outflow. *(Commit `de7e633`, H-025.)*
- [x] **I — Overhead** (🧑 owner supplies figures + 🤖 writes them in): the fixed-overhead **contract figures are owner-supplied** (from Phase 2's upload) — Claude Code writes them into a sourced `reference/` file but must **not** invent or back-fill them from the coarse CRM P&L. The equipment-maintenance line is **BLOCKED until an allocation base + method are stated** (then ESTIMATE); current commercial-auto = ACTUAL, Konji-driven increment = BLOCKED. *If the contract figures were not uploaded, this item is blocked — do not proceed to the overhead portion of Phase 7 without them.* *(`reference/fixed-overhead.md` exists, H-005 confirms sourcing 2026-07-04; the strategic-plan-facing figure update is in commit `2ee485a`, H-021.)*
- [x] **J — Auto insurance:** capture the premium increase as **BLOCKED pending an insurer quote** and a dated timeline decision point (before vs. after the Oct 9 term end); frame as coverage/liability, owner-to-verify; Anais already insured and in scope. *(Commit `9e6a944`, H-022. The premium figure remains BLOCKED by design — that's the correct state, not an incomplete item.)*
- [x] Append a `HISTORY.md` entry for each material change as you go. *(Each item is its own small commit; Claude Code pauses for your review before committing each — it does not auto-commit.)* *(H-021 through H-025 each cite the `CONTEXT.md` section and commit they close.)*

**Done when:** items B, C, D, F, H, I, J are applied and committed, and `HISTORY.md` reflects them. *(Checkpoint: repo files and `CONTEXT.md` are now back in sync.)* *(2026-07-09 sync: confirmed via H-021–H-025 and the cited commits. Note the D item's dollar figure is itself now historical — see its parenthetical above.)*

---

## Phase 6 — Clear the two pre-build gates

*Both must resolve before the model build. These are working sessions, not one-click tasks.*

- [x] **Gate A — Bank consolidation (#9)** 🧑 OWNER + 🤖: consolidate the Relay accounts, identify each account's purpose (operating / reserve / dormant), and establish the full cash picture from the actual statements. This is a **hard gate** — the build's cash side is bank-sourced (per D5a), so it does not proceed on CRM cash data alone. **Save the consolidated output into `reference/`** as new ground truth (and commit it). *Closed 2026-07-06: `reference/cash-consolidated-2026-07-06.csv`, verified $1,225.33 across all four active accounts — see `HISTORY.md` H-039.*
- [x] **Gate B — Revenue export format + service mapping (#6)** 🧑 OWNER + 🤖: obtain the flat transaction-line export (one row per date/customer/service/amount) and map the raw services to the ~16-item catalog. Resolve the exact raw-entry count here. **Save the flat export into `reference/`** as new ground truth (and commit it). *(Closed 2026-07-06, commit `46de380 "close Gate B"`, H-033. Refined further by H-036/H-037 (service classification, legacy-name mapping) and H-038 (22-item catalog formally sourced, replacing the "~16-item" estimate this item describes). The flat export itself now lives in `model/data/revenue-line-items.csv` — relocated from `reference/` per H-035, since it's a script-regenerated derivative, not a raw source.)*
  - [ ] *If Gate B is deferred:* explicitly choose the **named partial path** — build revenue events with `category`/`subcategory` tagged `BLOCKED — unmapped`, never guessed. (Amounts/totals are still correct; only classification is deferred.) *(N/A — Gate B was resolved via full mapping, not deferred; the partial path was never invoked. Left unchecked because it did not happen, not because it's unverified.)*

**Done when:** Gate A is done, and Gate B is either done or the partial path is explicitly chosen and recorded in `HISTORY.md`. *(2026-07-09 sync: both true. Gate A per H-039, Gate B per H-033. No pre-build gate remains open.)*

---

## Phase 7 — Build the model 🤖 CLAUDE CODE

*Item E. Full architecture in `CONTEXT.md` Section 9.*

- [x] Define the **data-layer CSVs** in `model/data/`: the atomic ledger (schema `date | type | event | category | subcategory | customer | quantity | unit_rate | amount | status | source`, with **separate invoice and payment events** per D5a) and the assumption tables. *(Schema defined by H-041 (2026-07-09) and unchanged since: all five files — `ledger-revenue.csv`, `ledger-labor.csv`, `ledger-overhead.csv`, `ledger-materials.csv`, `ledger-capital.csv` — still share the identical 11-column header (`date,type,event,category,subcategory,customer,quantity,unit_rate,amount,status,source`), reconfirmed directly against all five files this pass. Checking this box now on the schema itself, not on population — all five files hold real data as of Sequencing Steps 2–4 (H-043, H-044, H-046), but that status is covered in detail by the next checkbox, not restated here.)*
- [x] Populate what's real; tag every estimate/placeholder (`ESTIMATE` / `BLOCKED`): itemized labor (rates real, hours ESTIMATE); materials/fuel `$0` BLOCKED; overhead from `reference/`; sales-tax BLOCKED; capital events per Phase 5. *(Substantially done, Sequencing Steps 2–4 (H-043, H-044, H-046), further updated since. **Labor is no longer ESTIMATE**, per H-049 (2026-07-10): the original 66-row synthetic ESTIMATE ledger (rates real, hours estimated per D2) was fully replaced with 130 real ACTUAL rows sourced from Gusto payroll data, per employee per pay period, gated by a full-history reconciliation against Relay (`model/reconcile_payroll_relay.py`, 24/24 Net Pay + 24/25 tax exact matches). D2's original 2-person/50-50/$25-$20 model is preserved as a forward-looking projection-layer assumption only (see `CONTEXT.md` D2). Materials: one `$0.00` BLOCKED placeholder row in `ledger-materials.csv`, per D1, unchanged. Overhead: **102 ACTUAL rows** as of H-049 (not 79) — 77 pre-existing (32 Stripe + 15 Gusto payroll-provider-fee + 15 General Liability + 13 Homeworks/Copilot + 1 Workers Comp + 1 Squarespace, post-H-048's $316.00 bounced-FEE-charge fix) plus 25 new employer-payroll-tax-burden rows ($3,093.17) added by H-049 alongside the labor rebuild; Commercial Auto and equipment-maintenance correctly still have no row (no confirmed cash date / no allocation basis, not an oversight). Sales-tax: the surcharge dollar amount is already booked as 148 ACTUAL rows in `ledger-revenue.csv` ($1,556.47, per H-043) — "BLOCKED" as literally written here refers to Follow-Up #10's open *structural* treatment question (revenue vs. pass-through liability), not to whether the figure exists; the amount itself is measured, not blocked. Capital events per Phase 5 (Xavier ~$1,800, the owner's $3,800 truck-debt): correctly still un-ledgered, projection-layer-only, per the existing decision — not part of what this box's "done" status covers. Separately, `ledger-capital.csv` still holds two real ACTUAL rows outside Phase 5's scope entirely — a chainsaw purchase ($408.00) and the owner's truck/insurance reimbursement ($2,200.00), per H-046.)*
- [x] Write `model/build_model.py` — reads `data/`, generates the workbook. Append any new dependency it needs to `requirements.txt` (do not recreate the file). *(Done, H-047 (2026-07-10): seven sheets — Monthly P&L, Plan vs Actual, Quarterly Rollups, Revenue by Service, Revenue by Customer, Reconciliation, Raw Ledger. No new dependency was needed; `openpyxl==3.1.5`, already pinned, was sufficient. A real workbook non-determinism bug (openpyxl's writer unconditionally re-stamping `docProps/core.xml`'s `modified` timestamp) was found and fixed the same pass, so re-running with unchanged input produces a byte-identical file.)*
- [x] **Re-install dependencies** if the script added any: `pip install -r model/requirements.txt` (safe to run even if nothing changed). *(Not applicable — H-047 confirmed no new dependency was needed.)*
- [x] Add the **reconciliation tab** with its honest scope: verifies revenue (vs. CRM exports) and collected cash (CRM payment events vs. Relay statements); states on its face that it does **not** yet verify itemized overhead or materials/fuel. *(Done, H-047, scope since broadened twice: H-047 also added overhead-ACTUAL-rows-sourced and capital-rows-sourced checks beyond the original revenue/cash-only scope stated here; H-049/this pass (2026-07-10) added a fifth check referencing `model/reconcile_payroll_relay.py`'s full-history labor gate — 24/24 Net Pay + 24/25 tax exact matches — now that labor is real payroll-sourced ACTUAL data, not ESTIMATE. Current stated non-coverage: materials' BLOCKED placeholder, the ~85% of real Spend-side Relay cash with no ledger row by design, and labor's own known residual gaps (Follow-Ups #19–20).)*
- [x] Run the build: `python3 model/build_model.py`. Inspect the generated (gitignored) `model/financial-model.xlsx`. *(Done, first in H-047, re-run in H-048, H-049, and this pass to keep the workbook in sync with each data/script change; the workbook itself stays gitignored, never committed, per D7.)*
- [x] Validate the reconciliation tab against `reference/` (CRM revenue + bank cash). Resolve or flag any mismatch. *(Done, H-047: 4 checks passed (revenue invoice total exact vs. anchor; payment classification restated by reference to H-044's gate; overhead ACTUAL rows sourced; capital rows sourced), with named non-coverage stated rather than hidden. H-048 found and fixed a real $316.00 overhead overstatement (bounced Gusto FEE charges wrongly booked ACTUAL) via a broader RETURNED-transaction sweep, not this tab's own checks. H-049/this pass added the labor check: 24/24 Net Pay + 24/25 tax exact matches, one named exception (Follow-Up #20) explicitly flagged, not forced or hidden.)*
- [x] Commit the **data and script only** (the `.xlsx` is gitignored). Message e.g. `first model build: atomic ledger + build script + reconciliation`. *(Claude Code pauses for your review before committing.)* *(Done across multiple commits, not one: H-046 (`8024cc4`, ledger population), H-047 (`febe13e`, build_model.py), H-048 (`93b482a`, payroll files + Relay-reversal fix), H-049 (`07852f6`, labor rebuilt from real payroll data). The workbook has never been committed at any point, per D7.)*

**Done when:** the build runs cleanly, the workbook generates, the reconciliation tab passes or flags known-open items, and data + script are committed (workbook is not). *(2026-07-10 sync, this pass: all of the above are true and evidenced across H-046–H-049. Phase 7's original scope is complete; ongoing refinements (this pass's reconciliation-tab labor check, blended-rate crew-only scoping, `reference/PAYROLL-UPDATE.md`) are standing-maintenance work on an already-built model, not remaining Phase 7 setup.)*

---

## Phase 8 — Resume operations

- [ ] Resume the biweekly check-in cadence (`check-ins/check-in-template.md`) in the repo. *(Not started — `check-ins/` contains only the template; no dated check-in entries exist yet.)*
- [x] Confirm the follow-up list in `CONTEXT.md` Section 7 is your queue for the remaining dedicated sessions (crew reduction, seat question, forecast page, door-to-door package, expense convention, P&L cross-reference, tax treatment, Anais comp). *(Section 7 exists and is demonstrably live — several items have been actively tracked and status-updated across multiple `HISTORY.md` entries: #6 substantially resolved (H-033, H-036–H-038), #9 closed (H-039), #16 added (H-037). It is functioning as the queue, not a static list.)*

**Done when:** the first in-repo check-in is scheduled and the follow-up queue is live. *(2026-07-09 sync: the queue half is true and evidenced; the check-in cadence has not yet resumed.)*

---

## Quick reference — the everyday model-update loop (after the build)

Once the model exists, every change to the numbers follows the same four steps (this is the operating loop, not part of the one-time setup):

1. Edit a **data file** in `model/data/` (e.g., add invoice/payment events).
2. Regenerate: `python3 model/build_model.py`.
3. Inspect the workbook.
4. Review the plain-text CSV diff in Source Control → write a one-line message → commit.

Claude Code's standing rule: it edits **data or script**, regenerates, reports what changed, and **stops for your review before committing** — it never hand-edits the generated workbook, and never auto-commits.

---

*This runbook operationalizes `CONTEXT.md` (revision 6). If any step conflicts with `CONTEXT.md`, `CONTEXT.md` governs and the conflict should be logged and reconciled.*
