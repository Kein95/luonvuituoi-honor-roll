---
hide:
  - navigation
  - toc
---

<div class="lvt-hero" markdown>

<img src="assets/logo.svg" alt="LUONVUITUOI-HONOR ROLL logo" class="lvt-hero-logo">

# LUONVUITUOI-HONOR ROLL

<p class="lvt-hero-tagline">
Config-driven student honor-roll toolkit. Bring your results CSV/Excel/JSON and a config to obtain a public honor roll with search, admin panel, and multi-competition galleries in minutes.
</p>

<div class="lvt-cta-row">
  <a href="quickstart/" class="lvt-btn lvt-btn-primary">🚀 Quickstart (10 min)</a>
  <a href="https://honor-roll.luonvuituoi.work" class="lvt-btn lvt-btn-primary">🌟 Live Demo</a>
  <a href="https://honor-roll.luonvuituoi.work/login" class="lvt-btn lvt-btn-ghost" target="_blank" rel="noopener">🔐 Admin demo</a>
  <a href="https://github.com/Kein95/luonvuituoi-honor-roll" class="lvt-btn lvt-btn-ghost" target="_blank" rel="noopener">⭐ View on GitHub</a>
</div>

<div class="lvt-badges">
  <img src="https://img.shields.io/github/v/release/Kein95/luonvuituoi-honor-roll?style=flat-square&color=7c5cff&label=release" alt="release">
  <img src="https://img.shields.io/github/license/Kein95/luonvuituoi-honor-roll?style=flat-square&color=7c5cff" alt="license">
  <img src="https://img.shields.io/github/actions/workflow/status/Kein95/luonvuituoi-honor-roll/test.yml?style=flat-square&color=7c5cff&label=tests" alt="tests">
  <img src="https://img.shields.io/github/stars/Kein95/luonvuituoi-honor-roll?style=flat-square&color=fb7185" alt="stars">
</div>

</div>

## Why this exists

Running a competition, awarding medals, or hosting an olympiad requires a public showcase where students see their achievements, parents confirm results, and schools track their medals, all searchable, styled beautifully, and easy to manage. **LUONVUITUOI-HONOR ROLL delivers all three capabilities**, deployable to Vercel's free tier or any Docker host, with zero boilerplate.

<div class="lvt-features" markdown>

<div class="lvt-feature" markdown>
<span class="lvt-feature-icon">🏆</span>
### Multi-competition gallery
Define one or many competitions across years. Each runs independently; students see all their medals across every edition.
</div>

<div class="lvt-feature" markdown>
<span class="lvt-feature-icon">🎖️</span>
### Flexible medal registry
Define each medal once (rank, label, color, icon). Badges stay consistent. CSV/Excel/JSON ingest.
</div>

<div class="lvt-feature" markdown>
<span class="lvt-feature-icon">🔍</span>
### Public honor roll + search
Beautiful card and table views. Visitors search by name or ID, see every achievement instantly.
</div>

<div class="lvt-feature" markdown>
<span class="lvt-feature-icon">🛠️</span>
### Admin surface built in
Add, correct, or delete entries without touching files. Password-protected, audit log included.
</div>

<div class="lvt-feature" markdown>
<span class="lvt-feature-icon">⚡</span>
### Deploy anywhere
One-command Vercel deploy (free tier), production Dockerfile, or docker-compose. Select your preferred infrastructure.
</div>

<div class="lvt-feature" markdown>
<span class="lvt-feature-icon">🌐</span>
### Bilingual & mobile-ready
English + Vietnamese. Responsive, animated UI that shines on desktop, tablet, phone.
</div>

</div>

<div class="lvt-stats" markdown>

<div class="lvt-stat">
<div class="lvt-stat-num">10min</div>
<div class="lvt-stat-label">First deploy</div>
</div>

<div class="lvt-stat">
<div class="lvt-stat-num">0</div>
<div class="lvt-stat-label">Boilerplate code</div>
</div>

<div class="lvt-stat">
<div class="lvt-stat-num">$0</div>
<div class="lvt-stat-label">Vercel free tier</div>
</div>

<div class="lvt-stat">
<div class="lvt-stat-num">MIT</div>
<div class="lvt-stat-label">License</div>
</div>

</div>

## Getting started

<div class="lvt-features" markdown>

<div class="lvt-feature" markdown>
<span class="lvt-feature-icon">🚀</span>
### [Quickstart →](quickstart.md)
Deploy your first honor roll in 10 minutes. CLI scaffold, config walk-through, local run, Vercel push.
</div>

<div class="lvt-feature" markdown>
<span class="lvt-feature-icon">⚙️</span>
### [Configuration →](config-reference.md)
Every `honor.config.json` field + environment variable documented. Learn how to define competitions, medals, and rules.
</div>

<div class="lvt-feature" markdown>
<span class="lvt-feature-icon">🏛️</span>
### [Architecture →](architecture.md)
How the pieces fit: handlers, data model, search index, admin auth, and UI layers.
</div>

<div class="lvt-feature" markdown>
<span class="lvt-feature-icon">🔐</span>
### [Security →](security.md)
Hardening checklist for production. Admin auth, data validation, rate limiting.
</div>

<div class="lvt-feature" markdown>
<span class="lvt-feature-icon">🛠️</span>
### [Operations →](operations.md)
Health probe, log triage, backup strategy, incident checklist.
</div>

<div class="lvt-feature" markdown>
<span class="lvt-feature-icon">❓</span>
### [Troubleshooting →](troubleshooting.md)
Common failure modes, data import issues, and their fixes.
</div>

</div>

## Sibling projects

- **[LUONVUITUOI-CERT](https://github.com/Kein95/luonvuituoi-cert)**: A certificate portal toolkit. Issues and verifies PDF certificates with QR codes and admin panel. Whereas HONOR ROLL celebrates achievements, CERT proves them.
