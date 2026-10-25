# The AI Scam Safety Guide

Staying safe in the AI age — explained like a friend would. A beginner's
manual covering:

- spotting **AI-written scams** (the tells that survive perfect grammar),
- **deepfake photos** and fake profiles (and the reverse-image checks),
- **cloned-voice phone calls** and the family-passphrase defense,
- **fake AI tool sites** that harvest logins, cards, and pasted files,
- **too-good deals**: AI-made listings, fake reviews, and payment traffic
  lights,
- **verifying people and payments** — a three-rung ladder anyone can climb,
- a calm, step-by-step **what to do if you fell for one** (including the
  "recovery scam" second wave),
- a gentle **Family Friday talk** outline with scripts and role-plays,
- a printable **scam-spotting checklist**, six annotated **story examples**,
  and a plain-English **glossary**.

The theme throughout: be alert, not scared. A handful of second-long habits —
pause, verify on a channel you chose, never pay the scam-shaped way — catch
almost everything the new wave of AI-powered scams throws at people.

## A companion, not a repeat

This guide deliberately complements *The Privacy Comfort Handbook* (the
privacy-focused sibling guide): passwords, two-factor logins, what never to
paste into a chatbot, and the anatomy of ordinary phishing live **there**;
here the focus is scams aimed at *you personally* — faces, voices, deals,
and the human moments around them. The two handbooks cross-link instead of
re-teaching.

## Who's behind it

Written and maintained by **Asdale Dynamics, LLC** as part of its
beginner-friendly guide series — the same spirit behind the book
*The Massive AI Manual*: plain English, step by step, warm, never
condescending, never alarmist.

## Read it

The Markdown "source of truth" lives in [`docs/`](docs/). Build the static
site and open it in any browser:

```bash
python3 build.py
```

That generates `site/` — a self-contained static HTML site with no external
dependencies, no analytics, no cookies, and no JavaScript requirement (one
optional print button for the checklist). Open `site/index.html` to start
reading. Everything works offline.

## Test it

```bash
python3 -m unittest discover -s tests -v
```

The suite covers the Markdown-to-HTML converter (headings, anchors, lists,
task lists, tables, quotes, code fences, inline formatting, link rewriting)
and an end-to-end build check: every page renders, every internal link and
anchor resolves, the required copyright line appears in each footer, the
checklist renders with checkboxes and a print button, and no secret- or
API-key-shaped strings appear anywhere in the repo.

## Where things live

```
docs/             13 Markdown pages (the source of truth)
assets/           stylesheet + favicon, copied into the site
build.py          stdlib-only static site generator (docs/ -> site/)
tests/            converter unit tests + end-to-end build tests
site/             generated output (not committed; run build.py)
```

## Project principles

- **Local-first.** No accounts, no keys, no network calls; run and read
  it anywhere.
- **No secrets, no personal data.** The repo contains none, by design and
  by test.
- **Beginner tone.** Plain English, no condescension, calm throughout.
- **Practical.** Every chapter ends in something you can actually do:
  a line for the fridge, a passphrase, a script for family.

## License

MIT — see [`LICENSE`](LICENSE). Copyright (c) 2026 Asdale Dynamics, LLC.
