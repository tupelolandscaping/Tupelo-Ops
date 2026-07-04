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

- [ ] GitHub account active, signed in.
- [ ] VS Code Desktop installed, with its built-in Git and the GitHub/Codespaces integration.
- [ ] Claude Code installed and authenticated (your existing work setup). *This runbook assumes familiarity with Claude Code in VS Code; it does not re-teach install.*
- [ ] You have every file in the **Phase 2 upload manifest** ready to hand (Phase 2 is the single authoritative list — don't maintain a second copy here; just confirm you can produce all of them).

**Done when:** all four boxes are true.

---

## Phase 1 — Create the repository and open a Codespace

- [ ] Create a **new, empty, private** GitHub repository named exactly **`Tupelo-Ops`** under the **business's dedicated free GitHub account** (registered under the business email — not your personal or work account). Initialize it with a README so it's clonable (you'll overwrite that README later). *If you already created it under a personal account, recreate it under the business account and delete the personal copy — the repo is nearly empty, so recreating is cleaner than transferring.*
- [ ] Open the repo in a **Codespace** via VS Code Desktop (GitHub repo → Code → Codespaces → create; or the VS Code "Create Codespace" command). Wait for it to finish building and attach.

**First-bring-up environment check** (this becomes `SETUP.md` in Phase 4):

- [ ] In the terminal, confirm tooling: `node -v`, `npm -v`, `git --version` each return a version.
- [ ] Set git identity so commits succeed: `git config user.name "Your Name"` and `git config user.email "you@example.com"`.
- [ ] Confirm Claude Code is authenticated to the correct account.
- [ ] Confirm Python: `python3 --version`.
- [ ] Install VS Code extensions (Extensions panel): **Python** (Microsoft; bundles Pylance) and **Rainbow CSV** — essential. **GitLens** and an **Excel viewer** — optional.

**Done when:** the Codespace is open in VS Code, the four tools report versions, git identity is set, and the two essential extensions are installed.

---

## Phase 2 — Upload the source files 🧑 OWNER

*This phase is yours alone — Claude Code cannot reach files that live on your computer until you put them in the working tree.*

- [ ] Create a temporary folder at the repo root named `incoming/`.

**Upload into `incoming/`** (drag into the VS Code Explorer, or use the upload command). **This is the single authoritative upload manifest — every file any later phase consumes must appear here:**

- [ ] `Strategic_Plan_2026-2027.md`
- [ ] `Operational_Toolkit.md`
- [ ] `CheckIn_Template.md`
- [ ] `Execution_Timeline_2026-2027.md`
- [ ] `Landscaping_Financial_Model_3.xlsx`
- [ ] the CRM CSV exports — six files: services, expenses, revenue-by-customer, source, sales-tax, and the payment-type breakdown (the second "services" file, `services__..._1.csv`, which is actually a payment-method report)
- [ ] the P&L report `report_profit_and_loss_2.pdf`
- [ ] the Relay bank statements (all the `Relay_*.csv` files)
- [ ] `CONTEXT.md` (revision 6) and `RUNBOOK.md` (this file) — the two documents you're working from
- [ ] 🧑 **Fixed-overhead contract figures** — the actual amounts behind insurance, workers' comp, commercial auto, payroll provider, and CRM subscription (a short file or note). These are **owner-supplied**: they are not in any CRM export (the CRM's expense buckets are too coarse — that is *why* Phase 5 item I needs them), and Claude Code must not invent them. If you don't have them yet, that's fine — but Phase 5 item I and the overhead portion of Phase 7 are blocked until you do.

**Done when:** every listed file is visible in `incoming/`.

---

## Phase 3 — Populate the baseline and commit it 🤖 CLAUDE CODE

*Goal: get the files into their repo homes **unedited**, and commit that untouched state, so the "before" is preserved in history before any correction.*

- [ ] Instruct Claude Code to create the folder structure: `strategy/`, `check-ins/`, `model/data/`, `reference/`.
- [ ] Move and **kebab-case rename** the already-Markdown files:
  - `CheckIn_Template.md` → `check-ins/check-in-template.md`
  - `Execution_Timeline_2026-2027.md` → `strategy/execution-timeline.md`
- [ ] Move and **kebab-case rename** the two strategy documents (they arrive as Markdown — no conversion needed):
  - `Strategic_Plan_2026-2027.md` → `strategy/strategic-plan.md`
  - `Operational_Toolkit.md` → `strategy/operational-toolkit.md`
- [ ] Place raw source data in `reference/` unedited: the CRM CSV exports, the P&L report `report_profit_and_loss_2.pdf`, all Relay statements, **the source workbook `Landscaping_Financial_Model_3.xlsx`** (→ `reference/landscaping-financial-model-3.xlsx` — it is ground truth that Phase 7 decomposes and Phase 5 item F reads for `B43`), and **the fixed-overhead contract figures** if uploaded.
- [ ] Move `CONTEXT.md` and `RUNBOOK.md` to the repo root.
- [ ] Confirm `incoming/` is now genuinely empty (every file has been moved to its home), then delete it. *If anything remains, it means a file has no destination — resolve that before deleting, don't delete files with the folder.*
- [ ] **Commit the unedited baseline:** stage all, commit with a message like `baseline import — unedited source files in repo homes`. Do **not** apply any content corrections yet. *(As with every 🤖 commit step below: Claude Code stages and prepares the commit, then pauses for your review before committing — it does not auto-commit.)*

**Done when:** `git log` shows the baseline commit, and no Phase-5 corrections have been made yet. *(Checkpoint: the repo now mirrors the old project workspace, just relocated — stale content and all. That staleness is intentional and gets fixed in Phase 5.)*

---

## Phase 4 — Author the scaffold files 🤖 CLAUDE CODE

*Build the files that make the repo self-governing. Specs are in `CONTEXT.md` Section 8.*

- [ ] **`CLAUDE.md`** (queue item G) — per the Section 8 spec: project identity; standing rules + engagement preferences; architecture summary; the model-update operating procedure; the ground-truth rule; file conventions; the cross-reference check on structured edits; the history-logging rule; RAG-readiness conventions; deferred-tooling statement (Ruflo/RuVector not in use). Include the machine-global `~/.claude/CLAUDE.md` correctness note — and actually **check whether that global file exists** in this environment; if it does and carries Ruflo directives, the affirmative "deferred for this project" statement matters; if not, note it as not applicable.
- [ ] **`SETUP.md`** (G2) — the standalone new-Codespace guide (verify tooling, git identity, Claude Code auth, Python + `pip install -r model/requirements.txt`, extensions, Auto Save, sanity check). No Ruflo/RuVector steps.
- [ ] **`README.md`** (G3) — repository map / entry point.
- [ ] **`HISTORY.md`** (G3) — master append-only audit log; **seed** it from `CONTEXT.md`'s locked decisions and events so it starts populated. Include the `DECISION` entry for the cross-reference-legibility review check (basis: three review rounds where every surviving defect was join drift).
- [ ] **`.gitignore`** (G4) — exclude `model/financial-model.xlsx` and transient build artifacts.
- [ ] **`model/requirements.txt`** (G4) — pinned dependencies (start with `openpyxl`, pinned to a specific version). **Created here, once.**
- [ ] **Install the dependencies now:** `pip install -r model/requirements.txt`. (Creating the file does not install it — the build in Phase 7 will fail with `ModuleNotFoundError` if this is skipped. The architecture deliberately relies on the *installed, pinned* file, not on whatever the Codespace image happens to ship.)
- [ ] Commit, e.g. `add repo scaffold: CLAUDE.md, SETUP.md, README, HISTORY, gitignore, requirements`. *(Claude Code prepares the commit, then pauses for your review — it does not auto-commit.)*

**Done when:** all six files exist and are committed, `.gitignore` excludes the workbook, and `HISTORY.md` is non-empty.

---

## Phase 5 — Clear the reconciliation queue 🤖 CLAUDE CODE

*Now apply the "decided, not yet applied" corrections to the imported files — each as its own small, reviewable commit. Full detail per `CONTEXT.md` Section 6, items B–D, F, H, I, J. (A, G, G2, G3, G4 are already done.)*

- [ ] **B — Execution timeline:** mark the Konji tripwire resolved; backup-lead search active; add the end-of-July Job Costing anchor; correct GBP status (active, no reviews/leads); note no residual Konji family gate; add the auto-insurance / Konji-insured-driver decision point.
- [ ] **C — Strategic plan:** replace the placeholder crew-lead comp with Konji's finalized structure; check off "weekday crew lead secured."
- [ ] **D — Assumptions log:** Xavier ~$1,800, unpaid, demand-triggered late winter, status Track (with the equity-vs-contingent-outflow reconciliation); starting cash → $1,400 tagged **interim ESTIMATE**, superseded by Phase 6 consolidation. Do not lock it as ACTUAL.
- [ ] **F — Revenue anchor:** supersede `B43 = $9,562.71` with the current $12,726.01 billed / $10,973.57 collected; carry the anchor and Konji's 6% base as **gross-of-surcharge** pending the tax session (#10).
- [ ] **H — Truck entry:** record the $5,000 April entry as a retroactive log of an owned asset, **not** a new outflow.
- [ ] **I — Overhead** (🧑 owner supplies figures + 🤖 writes them in): the fixed-overhead **contract figures are owner-supplied** (from Phase 2's upload) — Claude Code writes them into a sourced `reference/` file but must **not** invent or back-fill them from the coarse CRM P&L. The equipment-maintenance line is **BLOCKED until an allocation base + method are stated** (then ESTIMATE); current commercial-auto = ACTUAL, Konji-driven increment = BLOCKED. *If the contract figures were not uploaded, this item is blocked — do not proceed to the overhead portion of Phase 7 without them.*
- [ ] **J — Auto insurance:** capture the premium increase as **BLOCKED pending an insurer quote** and a dated timeline decision point (before vs. after the Oct 10 term end); frame as coverage/liability, owner-to-verify; Anais already insured and in scope.
- [ ] Append a `HISTORY.md` entry for each material change as you go. *(Each item is its own small commit; Claude Code pauses for your review before committing each — it does not auto-commit.)*

**Done when:** items B, C, D, F, H, I, J are applied and committed, and `HISTORY.md` reflects them. *(Checkpoint: repo files and `CONTEXT.md` are now back in sync.)*

---

## Phase 6 — Clear the two pre-build gates

*Both must resolve before the model build. These are working sessions, not one-click tasks.*

- [ ] **Gate A — Bank consolidation (#9)** 🧑 OWNER + 🤖: consolidate the Relay accounts, identify each account's purpose (operating / reserve / dormant), and establish the full cash picture from the actual statements. This is a **hard gate** — the build's cash side is bank-sourced (per D5a), so it does not proceed on CRM cash data alone. **Save the consolidated output into `reference/`** as new ground truth (and commit it).
- [ ] **Gate B — Revenue export format + service mapping (#6)** 🧑 OWNER + 🤖: obtain the flat transaction-line export (one row per date/customer/service/amount) and map the raw services to the ~16-item catalog. Resolve the exact raw-entry count here. **Save the flat export into `reference/`** as new ground truth (and commit it).
  - [ ] *If Gate B is deferred:* explicitly choose the **named partial path** — build revenue events with `category`/`subcategory` tagged `BLOCKED — unmapped`, never guessed. (Amounts/totals are still correct; only classification is deferred.)

**Done when:** Gate A is done, and Gate B is either done or the partial path is explicitly chosen and recorded in `HISTORY.md`.

---

## Phase 7 — Build the model 🤖 CLAUDE CODE

*Item E. Full architecture in `CONTEXT.md` Section 9.*

- [ ] Define the **data-layer CSVs** in `model/data/`: the atomic ledger (schema `date | type | event | category | subcategory | customer | quantity | unit_rate | amount | status | source`, with **separate invoice and payment events** per D5a) and the assumption tables.
- [ ] Populate what's real; tag every estimate/placeholder (`ESTIMATE` / `BLOCKED`): itemized labor (rates real, hours ESTIMATE); materials/fuel `$0` BLOCKED; overhead from `reference/`; sales-tax BLOCKED; capital events per Phase 5.
- [ ] Write `model/build_model.py` — reads `data/`, generates the workbook. Append any new dependency it needs to `requirements.txt` (do not recreate the file).
- [ ] **Re-install dependencies** if the script added any: `pip install -r model/requirements.txt` (safe to run even if nothing changed).
- [ ] Add the **reconciliation tab** with its honest scope: verifies revenue (vs. CRM exports) and collected cash (CRM payment events vs. Relay statements); states on its face that it does **not** yet verify itemized overhead or materials/fuel.
- [ ] Run the build: `python3 model/build_model.py`. Inspect the generated (gitignored) `model/financial-model.xlsx`.
- [ ] Validate the reconciliation tab against `reference/` (CRM revenue + bank cash). Resolve or flag any mismatch.
- [ ] Commit the **data and script only** (the `.xlsx` is gitignored). Message e.g. `first model build: atomic ledger + build script + reconciliation`. *(Claude Code pauses for your review before committing.)*

**Done when:** the build runs cleanly, the workbook generates, the reconciliation tab passes or flags known-open items, and data + script are committed (workbook is not).

---

## Phase 8 — Resume operations

- [ ] Resume the biweekly check-in cadence (`check-ins/check-in-template.md`) in the repo.
- [ ] Confirm the follow-up list in `CONTEXT.md` Section 7 is your queue for the remaining dedicated sessions (crew reduction, seat question, forecast page, door-to-door package, expense convention, P&L cross-reference, tax treatment, Anais comp).

**Done when:** the first in-repo check-in is scheduled and the follow-up queue is live.

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
