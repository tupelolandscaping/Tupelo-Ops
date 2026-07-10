# SETUP.md — New-Codespace Environment Setup for Tupelo-Ops

**Purpose:** a self-contained checklist to run every time you open a *fresh* Codespace on this repository. Follow it top to bottom before doing any other work.

**Read this first — a fresh Codespace starts bare.** Each new Codespace is a brand-new cloud machine. It does **not** come with Claude Code installed or authenticated, and it does **not** come with the VS Code extensions listed below pre-installed — even though a previous Codespace on this same repo had them. This is real, recurring friction: expect to redo this setup every time you spin up a new Codespace (as opposed to reopening an existing, still-running one, which keeps its state). Do not assume any step below is already done just because it was done last time.

---

## 1. Verify the dev environment

In the VS Code terminal, confirm the basics are present and return version numbers:

```
node --version
npm --version
git --version
```

If any command is not found, the Codespace's base image is missing an expected tool — stop and investigate before continuing (this repo's tooling assumes all three are available).

## 2. Set your Git identity

Codespaces do not always pre-populate commit identity, and commits will fail without it. Set it explicitly:

```
git config --global user.name "Your Name"
git config --global user.email "your-business-email@example.com"
```

Use the business email associated with this repository's GitHub account, not a personal one, so commit authorship stays consistent with the account the repo lives under.

## 3. Confirm Claude Code is installed and authenticated

Claude Code is not preinstalled in a fresh Codespace. Confirm the CLI is available and check its authentication status:

```
claude --version
```

If it's not installed, install it, then authenticate and verify you are logged into the correct account (the business-associated account this project uses, not a personal one — see `CONTEXT.md` Section 7 item 12 for the account-consolidation context). The Claude Code editor extension for VS Code is a separate install from the CLI — confirm it as well (see Section 5 below).

## 4. Confirm Python and install pinned dependencies

Confirm Python is available:

```
python --version
```

Then install the pinned build dependencies (this is what makes the model build reproducible — pinned versions, not a committed binary):

```
pip install -r model/requirements.txt
```

This installs `openpyxl` (and any dependencies it pulls in) at the exact version the build script expects. If `model/requirements.txt` later grows additional pinned packages, re-run this same command to pick them up.

## 5. Install VS Code extensions

**Essential — install these every fresh Codespace:**
- **Python** (Microsoft) — bundles **Pylance**. Needed to run and edit `build_model.py` with proper language support.
- **Rainbow CSV** — makes the CSV data layer under `model/data/` and the raw exports under `reference/` legible as columns instead of raw comma-separated text.

**Optional — recommended but not required:**
- **GitLens** — richer Git history/blame views in the editor.
- An **Excel viewer** extension — lets you preview `model/financial-model.xlsx` without leaving VS Code (useful since the workbook is gitignored and only exists locally after a build).

Do not install any Ruflo, claude-flow, or RuVector extensions or packages — this project deliberately does not use them (see `CLAUDE.md`, "Deferred tooling").

## 6. Enable Auto Save

Turn on Auto Save (**File → Auto Save** in VS Code, or set `"files.autoSave": "afterDelay"` in settings) so edits persist to the Codespace's disk as you work.

This only protects against losing *in-editor* edits — it is not a substitute for committing. Persistence to GitHub still requires `git commit` + `git push`; if the Codespace itself is deleted or rebuilt, any uncommitted work is lost regardless of Auto Save.

## 7. First-run sanity check

**(a) Always-valid environment test.** This works on any fresh Codespace, even before the model build script exists, and proves Python plus the pinned dependency from Step 4 are both working:

```
python -c "import openpyxl; print(openpyxl.__version__)"
```

This should print a version number with no error. If it fails, something in Steps 1 or 4 is misconfigured — resolve it before starting any real work.

**(b) Fuller end-to-end check.** `model/build_model.py` exists and generates the workbook from the current data layer. Run:

```
python model/build_model.py
```

This should run without error and (re)generate `model/financial-model.xlsx` from the current contents of `model/data/`. Then open the generated workbook (via the Excel viewer extension, or by downloading it) to confirm it opened correctly. Treat this as the real sanity check going forward; (a) remains useful as a quick first-pass test even without running a build. For refreshing the underlying data (not just regenerating the workbook from what's already there), see `README.md`'s "Model data-refresh pipeline" section and `python model/refresh_all.py`.

---

*Once all seven steps pass, the environment is ready. For what to actually do in this repository — the model architecture, standing rules, and file conventions — see `CLAUDE.md` and `CONTEXT.md`.*
