# STATUS — The AI Scam Safety Guide

Built: 2026-10-25 · Owner: Asdale Dynamics, LLC

## What was built

A complete beginner's manual on staying safe in the AI age, delivered as
both readable Markdown and a self-contained static HTML site:

- **`docs/` — 13 Markdown pages (the source of truth):**
  - `index.md` — start-here intro, the "calm promise," the route table,
    and explicit companion rules vs. *The Privacy Comfort Handbook*
    (complements it, never repeats it: passwords/2FA/phishing basics live
    there and are only pointed at from here).
  - `01` how AI changed scams (better writing, fake photos, cloned
    voices; the unchanged three-part scam anatomy; pause/channel/payment
    rules).
  - `02` spotting AI-written scams (five context tells, reply test, name
    test, two worked examples of scam text).
  - `03` deepfake photos (visual tells in order, context tells, listing
    photo checks, fake screenshot checks).
  - `04` cloned-voice calls (call anatomy, family passphrase, the
    hang-up-and-call-back drill, other voice scams).
  - `05` fake AI tool sites (five shapes of the scam, what harvested data
    costs, six pre-use checks, throwaway-account rule).
  - `06` too-good deals (price-math question, listing tells, buyer
    protection table, marketplace specials).
  - `07` verifying people and payments (three-rung verification ladder,
    invoice-change rule, payment traffic light, "pending never arrives").
  - `08` what to do if you fell for one (first 15 minutes, first day,
    sextortion guidance, recovery-scam second wave, honest money-odds
    note).
  - `09` the Family Friday talk (30-minute outline with scripts,
    passphrase setup, role-play, versions for grandparents/teens/skeptics,
    monthly follow-up).
  - `checklist.md` — printable full scam-spotting checklist (checkboxes).
  - `stories.md` — six annotated story examples (voice clone, fake
    seller, fake AI app, boss BEC, slow-warm fake profile, grant fee).
  -   `glossary.md` — plain-English glossary, 29 terms with chapter
  cross-links.
- **`build.py`** — a stdlib-only static site generator
  (`docs/` + `assets/` → `site/`, no dependencies, no network).
- **`assets/`** — in-house stylesheet + SVG favicon (no CDNs, no fonts
  fetched).
- **`tests/test_build.py`** — 29 tests: converter unit tests plus
  end-to-end build checks (page set, link/anchor resolution, footer
  copyright, checkbox rendering, print button on the checklist only,
  secret-shaped-string scan, no external asset references).
- **`README.md`** — with credits for Asdale Dynamics, LLC; **`LICENSE`**
  — MIT, `Copyright (c) 2026 Asdale Dynamics, LLC`.

## How to run it

```bash
python3 build.py                          # build site/ (about 0.1 s)
open site/index.html                      # read it (any browser, offline)
python3 -m unittest discover -s tests -v  # run the 29 tests
python3 build.py --out DIR                # build elsewhere (used by tests)
```

## Verification results (actual runs, 2026-10-25)

- `python3 -m unittest discover -s tests -v` → **Ran 29 tests … OK**
  (all pass, including the end-to-end link/anchor/copyright checks).
- `python3 build.py` → **Built 15 files into site/** (13 pages +
  `style.css` + `favicon.svg`).
- Cross-build check into a temp dir (`--out /tmp/opencode/scam-site-check`)
  → also 15 files, so the generator is not dependent on the repo path.
- Internal-link/anchor resolution is enforced by test (every
  `chapter.md#anchor` in the Markdown resolves in the built HTML).
- Secret scan (part of the suite) found no API-key- or key-shaped
  strings in the repo; the site itself references no external URLs for
  assets (no JS/CDN/analytics; the only network links are the two fraud
  reporting sites, which are outbound text links only).
- Manual read-through of generated pages (stripped-HTML dump of index,
  ch04, ch06, ch07, ch09, stories) for tone and garbles; several writing
  glitches were caught and fixed during the pass.

## Known gaps / honest limits

- The Markdown→HTML converter covers the subset used in `docs/`
  (headings, paragraphs, lists, task lists, tables, blockquotes, fences,
  inline bold/italic/code/links). It does not aim to be full CommonMark —
  e.g., emphasis spanning multiple source lines and reference-style
  links are unsupported — and the tests pin the supported subset.
- Story examples are invented composites of widely reported scam
  patterns, not case files; they are labeled as such in `stories.md`.
- The payment-traffic-light table reflects general US-centric rails
  (FTC/IC3 reporting, Zelle/Venmo/gift cards). Readers outside the US
  will need local equivalents; the principles (irreversible rails are
  red) transfer.
- Advice chapters intentionally avoid regurgitating privacy-basics that
  *The Privacy Comfort Handbook* covers; on its own, this guide assumes
  that companion exists.
- No deepfake-detection tooling is bundled — deliberately: kit-avoidant,
  manual-first; the checks chosen work without any tool.
- Site is per-page (no search); fine at 13 pages.

## Boundaries honored

- Local-first: no accounts, no keys, no network calls in build or site.
- No secrets, API keys, or personal data in any file.
- Git initialized local-only; no remote, no push, nothing published.
