<div align="center">

# LLMScout

Runs 21 technical-SEO and GEO (generative-engine-optimization) checks against your site, in pure TypeScript or pure Python, with zero Python interpreter, zero headless browser, and zero external toolchain either way.

[![CI](https://github.com/RudrenduPaul/LLMScout/actions/workflows/ci.yml/badge.svg)](https://github.com/RudrenduPaul/LLMScout/actions/workflows/ci.yml)
[![npm version](https://img.shields.io/npm/v/llmscout-cli.svg)](https://www.npmjs.com/package/llmscout-cli)
[![PyPI version](https://img.shields.io/pypi/v/llmscout-cli.svg)](https://pypi.org/project/llmscout-cli/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

</div>

![Installing llmscout-cli with npm, then running llmscout init and llmscout check against a live site, with the resulting PASS/WARN/FAIL check output in the terminal](./docs/demo.gif)

## Contents

- [Install](#install)
- [Why GEO checks matter right now](#why-geo-checks-matter-right-now)
- [Features](#features)
- [Quickstart](#quickstart)
- [The 21 checks](#the-21-checks)
- [CLI reference](#cli-reference)
- [Fleet mode](#fleet-mode)
- [Library API reference](#library-api-reference)
- [Comparison](#comparison)
- [What is LLMScout, and why does it exist](#what-is-llmscout-and-why-does-it-exist)
- [FAQ](#faq)
- [Contributing](#contributing)
- [License](#license)

## Install

LLMScout ships as two independent, complementary distributions. Both run the same 21 checks with the same PASS/WARN/FAIL verdicts, so pick whichever fits your toolchain.

**Node/TypeScript (npm):**

```bash
npm install -g llmscout-cli
llmscout init ./my-site --site-url https://example.com
llmscout check ./my-site
```

The CLI targets Node 18+ (declared in `package.json` `engines`). The two runtime dependencies are `cheerio` (HTML parsing) and `commander` (argument parsing): there is no Python interpreter, no `pip install`, and no Playwright/Chromium download anywhere in the npm install.

**Python (PyPI):**

```bash
pip install llmscout-cli
llmscout init ./my-site --site-url https://example.com
llmscout check ./my-site
```

Zero runtime dependencies -- HTML parsing and HTTP fetching both use only the Python standard library. See [python/README.md](./python/README.md) for the full Python-specific guide.

Then, in any project you want to check:

```bash
llmscout init .
```

That scaffolds a `llmscout.json` config and a small Claude Code skill file into the target directory. Set your site URL and run `llmscout check .`.

## Why GEO checks matter right now

Search traffic is genuinely shifting toward AI-mediated answers, and the shift is recent and well measured, not a hypothetical:

- **Google's own AI Overviews are already cutting click-through.** Ahrefs measured position-1 CTR on AI-Overview-triggering keywords fall from 7.3% (December 2023) to 1.6% (December 2025) -- a 58% average CTR reduction across the study. ([Ahrefs, December 2025](https://ahrefs.com/blog/ai-overviews-reduce-clicks-update/)) Semrush's independent 10-million-keyword analysis found organic CTR drops 61% and paid CTR drops 68% when an AI Overview appears on the results page. ([Semrush](https://www.semrush.com/blog/semrush-ai-overviews-study/))
- **ChatGPT itself is now a real, measurable traffic source.** Search Engine Land's analysis of 6.77 million sessions found ChatGPT accounts for 92% of all AI-assistant referral traffic, converting at 7.1% -- close to paid search's 7.8%. ([Search Engine Land](https://searchengineland.com/chatgpt-ai-referral-traffic-sessions-data-481630))
- **AI crawlers are not one crawler anymore.** Between May 2024 and May 2025, GPTBot's share of AI-crawler traffic rose from 5% to 30%. OpenAI and Anthropic have since split their bots into training crawlers (GPTBot, ClaudeBot) and separate, independently blockable search/retrieval crawlers (OAI-SearchBot, Claude-SearchBot). ([Cloudflare Radar, "From Googlebot to GPTBot"](https://blog.cloudflare.com/from-googlebot-to-gptbot-whos-crawling-your-site-in-2025/)) LLMScout's `ai-crawler-directives` check reports on all seven of the current major training and search bots (GPTBot, OAI-SearchBot, ClaudeBot, Claude-SearchBot, PerplexityBot, Google-Extended, Applebot-Extended) separately, since blocking a company's training bot has no effect on whether its assistant can still retrieve and cite your page live through its own search bot.
- **Markdown-native delivery is a real, emerging practice, not a fad.** Cloudflare documents HTTP content negotiation (`Accept: text/markdown`) as a standards-based way to serve agents a lighter, cleaner representation of a page -- their own benchmark saw an 80% token reduction on one blog post. ([Cloudflare, "Markdown for Agents"](https://developers.cloudflare.com/fundamentals/reference/markdown-for-agents/)) Worth being honest about the current state: independent analysis across 300,000 domains found that in practice, no major AI crawler currently sends the `Accept: text/markdown` header to actually negotiate it yet -- they discover Markdown only via direct links. ([Dries Buytaert](https://dri.es/markdown-llms-txt-and-ai-crawlers)) LLMScout's `markdown-negotiation` check reports on this without pretending the ecosystem is further along than it is.
- **Not every signal in this space is settled, and LLMScout does not pretend otherwise.** `llms.txt` is a real, community-driven convention (created September 2024, adopted by roughly 8-10% of top sites as of mid-2026, including Anthropic, Stripe, Cloudflare, and Vercel) -- but Google's own Gary Illyes has stated publicly that Google does not support it and has no plans to, comparing it to the deprecated `keywords` meta tag. ([Search Engine Journal](https://www.searchenginejournal.com/google-says-llms-txt-comparable-to-keywords-meta-tag/544804/)) LLMScout's `llms-txt` check reports its presence as informational, never as a required pass -- the tool's job is to report what is actually configured, not to prescribe a policy the evidence doesn't yet support.
- **Google removed FAQ rich results from Search entirely on May 7, 2026.** ([Search Engine Journal](https://www.searchenginejournal.com/google-drops-faq-rich-results-from-search/574429/)) `FAQPage` schema itself is not deprecated -- it remains valid markup other engines and AI assistants can still parse for direct-answer extraction -- so LLMScout's `faq-schema` check still reports on it, just without implying it earns a Google SERP rich result anymore.

## Features

- **21 checks across two categories.** 12 technical-SEO checks and 9 GEO checks, listed by name in [The 21 checks](#the-21-checks).
- **Zero external toolchain, either language.** `child_process` is never imported anywhere in the TypeScript source; the Python port has zero runtime dependencies. Checks run inside the process instead of shelling out to Python scripts or a headless browser.
- **Cross-platform by construction.** No `python3`-versus-`py -3` shelling and no relative-path script resolution, so the same install runs identically on Windows, macOS, and Linux.
- **Hardened fetch.** The single fetch wrapper (`src/fetch-utils.ts`) rejects any non-`http(s)` scheme, blocks loopback/private/link-local hosts, follows redirects manually one hop at a time, and bounds the chain at 5 hops and the response body at 10 MiB.
- **Fleet mode with per-site reports.** `llmscout fleet manifest.json` runs the full suite across many local client-repo paths in one invocation, and `--out-dir` writes one auto-named report file per site -- built for agencies checking many client sites at once.
- **Structured output.** Every command accepts a global `--json` flag for machine-readable output, so an agent invoking the CLI can parse results programmatically.
- **A real, configurable User-Agent.** Sends a genuine browser User-Agent by default (some SSR frameworks and CDNs reject bot-style strings outright) and a `--user-agent` flag to override it.
- **Well tested.** 248 TypeScript tests and 233 Python tests, both reproducible locally with `npm test` / `npm run test:coverage` and `pytest`. The Python distribution has zero runtime dependencies, so there is nothing for a dependency audit to flag. On the npm side, `npm audit` currently reports one high-severity advisory in `undici`, a transitive dependency pulled in by `cheerio`, not in this project's own code.

## Quickstart

Scaffold a config and run a check against a live site:

```bash
llmscout init ./my-site --site-url https://example.com
llmscout check ./my-site
```

Real output from `llmscout check` against `https://example.com`:

```
LLMScout check -- https://example.com

[PASS] (technical) Title tag
  Title "Example Domain" is 14 characters, within the recommended 10-60 range.

[WARN] (technical) Meta description
  No meta description found.
  Fix: Add <meta name="description" content="..."> with 50-160 characters summarizing the page.

[WARN] (technical) Canonical tag
  No <link rel="canonical"> tag found.
  Fix: Add a canonical link tag pointing at the preferred URL for this page.

[FAIL] (technical) robots.txt
  robots.txt was not reachable at https://example.com/robots.txt (HTTP 404).
  Fix: Add a robots.txt file at your site root, even a permissive one, so crawlers and agents have explicit directives.

[WARN] (technical) sitemap.xml
  No sitemap was reachable (tried: https://example.com/sitemap.xml).
  Fix: Add a sitemap.xml at your site root, or point to one with a Sitemap: directive in robots.txt, to help search engines discover pages.

[PASS] (technical) Heading structure
  Exactly one <h1> and no skipped heading levels detected.

[PASS] (technical) Image alt coverage
  No <img> tags found on the page.

[WARN] (technical) Open Graph tags
  No Open Graph tags found.
  Fix: Add Open Graph meta tags (og:title, og:description, og:image, og:url) so shared links render rich previews on social platforms.

[WARN] (technical) Twitter/X Card tags
  No twitter:card meta tag found.
  Fix: Add <meta name="twitter:card" content="summary_large_image"> (or another valid card type) so links render rich previews on X/Twitter.

[WARN] (technical) Meta robots directives
  No meta robots directives found; default Google Search snippet/preview limits will apply.
  Fix: Add <meta name="robots" content="max-snippet:-1, max-image-preview:large, max-video-preview:-1"> to control search snippet appearance.

[PASS] (technical) Image weight
  No <img> tags with an http(s) src to measure.

[PASS] (technical) Redirect chain
  The homepage resolved with no redirects.

[WARN] (geo) Structured data (JSON-LD)
  No JSON-LD structured data found.
  Fix: Add schema.org JSON-LD markup (e.g. Organization, WebSite, or Article) so generative engines can understand the page's entities.

[WARN] (geo) llms.txt
  No llms.txt found at https://example.com/llms.txt.
  Fix: Optional: add an llms.txt at your site root summarizing the site for LLM-based agents (see llmstxt.org).

[WARN] (geo) AI crawler directives
  robots.txt is unreachable, so AI-crawler directives could not be determined.
  Fix: Add a reachable robots.txt if you want to state an explicit policy for AI crawlers (GPTBot, OAI-SearchBot, ClaudeBot, Claude-SearchBot, PerplexityBot, Google-Extended, Applebot-Extended).

[WARN] (geo) FAQ schema
  No FAQPage structured data found.
  Fix: If this page has an FAQ section, mark it up with FAQPage JSON-LD so generative engines can surface individual answers.

[PASS] (geo) Content extraction friendliness
  Found 1 heading(s) and 1 structured text block(s); content appears reasonably extractable. (Heuristic: cannot assess semantic quality or JS-rendered content.)

[WARN] (geo) Speakable schema
  No Speakable structured data found.
  Fix: If this page has content suited for voice assistants, add a "speakable" SpeakableSpecification to its JSON-LD so voice search can surface it.

[WARN] (geo) Organization schema
  No Organization/Corporation/LocalBusiness/Person structured data found.
  Fix: Add Organization (or Person) JSON-LD with a sameAs array of your official social/profile URLs to strengthen Knowledge Panel signals.

[WARN] (geo) Markdown content negotiation
  Requesting https://example.com/ with "Accept: text/markdown" returned Content-Type "text/html" instead of text/markdown.
  Fix: Optional: serve a text/markdown representation of pages when the client sends "Accept: text/markdown" so LLM-based agents can fetch clean Markdown directly instead of parsing HTML.

[WARN] (geo) Link header (RFC 8288)
  The homepage does not send a Link response header.
  Fix: Optional: add an RFC 8288 Link response header (e.g. <https://example.com/feed>; rel="alternate") to advertise machine-readable service-discovery endpoints to crawlers and AI agents.

Summary: 6 PASS, 14 WARN, 1 FAIL (21 checks)
```

The same run with `--json`:

```bash
llmscout --json check ./my-site
```

```json
{
  "siteUrl": "https://example.com",
  "summary": {
    "pass": 6,
    "warn": 14,
    "fail": 1,
    "total": 21
  },
  "results": [
    {
      "id": "title",
      "name": "Title tag",
      "category": "technical",
      "status": "PASS",
      "message": "Title \"Example Domain\" is 14 characters, within the recommended 10-60 range."
    }
  ]
}
```

`check` exits `0` when no check FAILs, `1` when at least one check FAILs (WARN alone does not fail the run), and `2` on a usage error such as a missing or misconfigured `llmscout.json`.

## The 21 checks

Each check reports `PASS`, `WARN`, or `FAIL`, with a fix suggestion for anything that is not a clean PASS. A `WARN` is a missed optimization, not a broken page, and never fails the run on its own.

### Technical SEO (12)

| Check (`id`) | What it verifies |
| --- | --- |
| Title tag (`title`) | A `<title>` exists and is within 10-60 characters. |
| Meta description (`meta-description`) | A `<meta name="description">` exists and is within 50-160 characters. |
| Canonical tag (`canonical`) | A `<link rel="canonical">` exists and its href is a valid URL (relative hrefs are resolved, not penalized). |
| robots.txt (`robots-txt`) | `/robots.txt` is reachable and contains at least one `User-agent` directive. |
| sitemap.xml (`sitemap-xml`) | `/sitemap.xml` is reachable and valid, with a `Sitemap:` directive in robots.txt checked as a fallback location. A response that looks like a CDN challenge page (e.g. Cloudflare bot management) gets a distinct message instead of a generic "malformed sitemap" one. |
| Heading structure (`heading-structure`) | Exactly one `<h1>`, and no skipped heading levels (for example an `<h1>` followed directly by an `<h3>`). |
| Image alt coverage (`image-alt`) | `<img>` tags have an `alt` attribute (an intentional `alt=""` for decorative images counts as covered). |
| Open Graph tags (`open-graph`) | `og:title`, `og:description`, `og:image`, and `og:url` meta tags are present, for rich link previews on social platforms. |
| Twitter/X Card tags (`twitter-card`) | A valid `twitter:card` meta tag and its required companion fields are present. |
| Meta robots directives (`robots-meta-directives`) | Advanced snippet-control directives (`max-snippet`, `max-image-preview`, `max-video-preview`) are set, and flags an outright `noindex`. |
| Image weight (`image-weight`) | Each image's actual byte size (via a HEAD request), flagging oversized images that slow page load. |
| Redirect chain (`redirect-chain`) | The homepage's full redirect chain, warning on long chains and failing if the chain dead-ends in an error status. |

### GEO / generative engine optimization (9)

| Check (`id`) | What it verifies |
| --- | --- |
| Structured data (`structured-data`) | JSON-LD `<script type="application/ld+json">` blocks exist and parse as valid JSON. |
| llms.txt (`llms-txt`) | An `/llms.txt` is present at the site root (an emerging, non-standardized convention -- see [Why GEO checks matter right now](#why-geo-checks-matter-right-now); absence is informational). |
| AI crawler directives (`ai-crawler-directives`) | Reports the robots.txt allow/disallow state for GPTBot, OAI-SearchBot, ClaudeBot, Claude-SearchBot, PerplexityBot, Google-Extended, and Applebot-Extended. This is a report of what is configured, never a recommendation to allow or block. |
| FAQ schema (`faq-schema`) | `FAQPage` JSON-LD is present (informational; only relevant to pages that actually have an FAQ -- see the note on Google's May 2026 rich-result deprecation above). |
| Content extraction friendliness (`content-extraction`) | Heuristic: the page has heading/paragraph structure an engine can chunk, rather than one large unstructured block. It cannot see content that only appears after client-side JavaScript, by design. |
| Speakable schema (`speakable-schema`) | A `SpeakableSpecification` is present in JSON-LD, for voice-assistant answer eligibility. |
| Organization schema (`organization-schema`) | `Organization`/`Person` JSON-LD with a `sameAs` array of official profile URLs is present, for Knowledge Panel signals. |
| Markdown content negotiation (`markdown-negotiation`) | Whether the site serves a `text/markdown` representation when requested via `Accept: text/markdown` content negotiation. |
| Link header (`link-header`) | Whether the homepage response sends an RFC 8288 `Link` header for machine-readable service discovery. |

You can run only one category by editing the `checks` block in `llmscout.json` (`{ "checks": { "technical": true, "geo": false } }`).

## CLI reference

Transcribed from the tool's own `--help` output.

```
$ llmscout --help
Usage: llmscout [options] [command]

Zero-config, cross-platform SEO and GEO checks for local projects, with no
Python or headless-browser dependency.

Options:
  -V, --version                  output the version number
  --json                         output structured JSON instead of
                                 human-readable text (default: false)
  --user-agent <string>          override the default User-Agent header sent on
                                 outbound fetches
  -h, --help                     display help for command

Commands:
  init [options] <path>          Scaffold a LLMScout setup (llmscout.json + a
                                 Claude Code skill file) into a target
                                 directory
  check [options] <path>         Run SEO/GEO checks against a local project's
                                 configured site
  fleet [options] <config.json>  Run the full check suite against every site
                                 listed in a fleet manifest
  help [command]                 display help for command
```

| Command | Argument | Options | Purpose |
| --- | --- | --- | --- |
| `init` | `<path>` target directory | `--site-url <url>` set `siteUrl` immediately | Scaffold `llmscout.json` plus a Claude Code skill file. Idempotent: existing files are left untouched. |
| `check` | `<path>` project directory containing `llmscout.json` | `--out-dir <dir>` also write an auto-named report file for this site; (global `--json`, `--user-agent`) | Run the selected checks against the configured `siteUrl`. |
| `fleet` | `<config.json>` fleet manifest | `--out-dir <dir>` also write one auto-named report file per site, named from the manifest's `name` field; (global `--json`, `--user-agent`) | Run the full suite against every site in the manifest. |

`--json`, `--user-agent`, `-V`/`--version`, and `-h`/`--help` are the only global options.

### Exit codes

| Code | Meaning |
| --- | --- |
| `0` | `init` succeeded, or `check`/`fleet` completed with no FAIL. |
| `1` | `check`: at least one check FAILed. `fleet`: at least one site FAILed or errored. |
| `2` | Usage error: invalid URL scheme, missing/unreadable/invalid `llmscout.json`, blank `siteUrl`, missing manifest, or any other configuration error. |

## Fleet mode

![Running cat fleet.json to show a two-site manifest, then llmscout fleet ./fleet.json checking both sites and printing a per-site PASS/FAIL summary](./docs/usage.gif)

`fleet` is aimed at agencies or teams that maintain several client sites side by side as local repos. You declare each site in one manifest and check them all in a single command:

```json
{
  "sites": [
    { "name": "client-a", "path": "./clients/client-a" },
    { "name": "client-b", "path": "./clients/client-b" }
  ]
}
```

```bash
llmscout fleet ./fleet.json
```

```
LLMScout fleet report

[FAIL] client-a (/abs/path/clients/client-a) -- 6 PASS, 14 WARN, 1 FAIL
[PASS] client-b (/abs/path/clients/client-b) -- 8 PASS, 13 WARN, 0 FAIL

Fleet summary: 1 site(s) passed, 1 site(s) failed, 0 site(s) errored (2 total).
```

Add `--out-dir ./reports` and each site's result is also written to its own auto-named file (`client-a.txt`, `client-b.txt`, or `.json` with `--json`) -- instead of one combined stdout dump, an agency running this across many client sites gets one distinguishable report per client. Each manifest entry's `path` resolves against the manifest file's own directory, not the process working directory, so the same manifest works no matter where you invoke it from. Everything is local filesystem access, with no SSH and no remote-execution surface.

## Library API reference

Both distributions are also genuinely importable libraries, not just CLIs. The exports below are real (grepped from `src/index.ts` and `python/src/llmscout/__init__.py`), and the examples are tested against the published packages, not written from memory.

**TypeScript (`llmscout-cli` on npm):**

```ts
import { loadSite, runChecks, ALL_CHECKS } from "llmscout-cli";

const ctx = await loadSite("https://example.com");
const results = await runChecks(ALL_CHECKS, ctx);
console.log(results[0].status, results[0].name);
// "PASS" "Title tag"
```

| Export | Signature | What it does |
| --- | --- | --- |
| `loadSite` | `(rawSiteUrl: string, fetchFn?: FetchFn) => Promise<CheckContext>` | Validates the URL, fetches the site's resources, and builds a `CheckContext` in one call. What `check` and `fleet` both call internally. |
| `fetchSiteResources` | `(siteUrl: URL, fetchFn?: FetchFn) => Promise<SiteResources>` | Lower-level: fetches the homepage plus robots.txt/sitemap.xml/llms.txt in parallel, without building a `CheckContext`. |
| `buildCheckContext` | `(resources: SiteResources, fetchFn?: FetchFn) => CheckContext` | Builds a `CheckContext` from resources you already fetched (parses the homepage once with cheerio). |
| `runChecks` | `(checks: Check[], ctx: CheckContext) => Promise<CheckResult[]>` | Runs a list of checks against one context. A check that throws becomes a `FAIL` result instead of aborting the run. |
| `hasFailure` | `(results: CheckResult[]) => boolean` | `true` if any result's `status` is `"FAIL"`. |
| `ALL_CHECKS` / `TECHNICAL_CHECKS` / `GEO_CHECKS` | `Check[]` | The full check suite, or just one of the two categories. |
| `initProject` | `(targetPath: string, opts?: { siteUrl?: string }) => InitResult` | Scaffolds `llmscout.json` and the Claude Code skill file. Idempotent. |
| `loadFleetManifest` / `runFleet` | see `src/fleet.ts` | Load a fleet manifest and run the suite across every site in it. |
| `safeFetch` / `assertHttpUrl` | see `src/fetch-utils.ts` | The hardened fetch wrapper described in [Features](#features), exported for reuse in a custom check. |

Types: `Check`, `CheckContext`, `CheckResult`, `CheckStatus` (`"PASS" \| "FAIL" \| "WARN"`), `CheckCategory` (`"technical" \| "geo"`), `SiteResources`, `LLMScoutConfig`, `FleetManifest`. No generated API docs site exists yet; this table and the source's own TSDoc comments are the reference.

**Python (`llmscout-cli` on PyPI):**

```python
from llmscout import load_site, run_checks, ALL_CHECKS

ctx = load_site("https://example.com")
results = run_checks(ALL_CHECKS, ctx)
print(results[0].status, results[0].name)
# PASS Title tag
```

The Python package mirrors the TypeScript one function-for-function: `load_site`, `run_checks`, `has_failure`, `ALL_CHECKS`/`TECHNICAL_CHECKS`/`GEO_CHECKS`, `init_project`, `load_fleet_manifest`/`run_fleet`, `safe_fetch`/`assert_http_url`, `load_config`/`default_config`/`select_checks`, plus the `Check`, `CheckContext`, `CheckResult`, and `SiteResources` types. Full list in `python/src/llmscout/__init__.py`'s `__all__`. No generated Sphinx docs exist yet; the module docstring (`import llmscout; help(llmscout)`) and this table are the reference.

## Comparison

Every cell below is drawn from a verifiable source (a repo file, a package manifest, or an open issue), cited under the table. "Checker" means the tool audits an existing live site; "generator" means it emits SEO/GEO asset files for you to publish.

| | LLMScout | claude-seo (AgriciDaniel) | geo-seo-claude (zubair-trabzada) | geo-optimizer-skill (Auriti-Labs) |
| --- | --- | --- | --- | --- |
| Requires Python | No | Yes (Python 3.10+) | Yes | Yes (Python 3.9+) |
| Requires Playwright / headless browser | No | Optional (Chromium auto-installed by `install.sh` for SPA rendering) | Optional, for some checks | Not required for core function |
| Install | npm / PyPI (deps: `cheerio`+`commander` or none) | `git clone` + `install.sh` / `install.ps1`, or Claude Code `/plugin` | `git clone` + `install.sh` / `install-win.sh` | `pip install` or `uvx` |
| Cross-platform / Windows out of the box | Yes (no shelling, no path resolution) | Ships a Windows `install.ps1`, but fresh-install/Windows/path failures are a recurring pattern: issues [#137](https://github.com/AgriciDaniel/claude-seo/issues/137), [#138](https://github.com/AgriciDaniel/claude-seo/issues/138), [#139](https://github.com/AgriciDaniel/claude-seo/issues/139) | Windows install pain is a recurring pattern here too: issues [#69](https://github.com/zubair-trabzada/geo-seo-claude/issues/69), [#21](https://github.com/zubair-trabzada/geo-seo-claude/issues/21), [#3](https://github.com/zubair-trabzada/geo-seo-claude/pull/3) | pip/uv are cross-platform; not verified further |
| AI-crawler bot coverage | 7 bots, training and search crawlers tracked separately (GPTBot/OAI-SearchBot, ClaudeBot/Claude-SearchBot, PerplexityBot, Google-Extended, Applebot-Extended) | Not a dedicated check | Not a dedicated check | Not verified |
| Markdown content negotiation check | Yes (`markdown-negotiation`) | No | No | No |
| Role | Checker | Checker | Checker + report generator | Checker |
| Coverage | Technical + GEO (21 checks) | Technical + GEO (broad) | GEO-focused | Technical + GEO |
| License | MIT | MIT | Not verified | MIT |

Sources: LLMScout, from this repo's `package.json`, `src/fetch-utils.ts`, `src/checks/index.ts`, and the absence of `child_process` in `src/`. claude-seo, from its README install section (Python 3.10+, `install.sh`/`install.ps1`, `/plugin`), its MIT license, and open issues #137/#138/#139. geo-seo-claude, from its README and its own issue tracker (Windows install pain issues #69, #21, #3, all cited above). geo-optimizer-skill, from its README (Python 3.9+, `pip install geo-optimizer-skill` / `uvx`, MIT, CLI with audit/fix commands).

Hosted analytics products such as Profound, Peec, and Evertune are a different category (paid, hosted GEO-tracking dashboards, not installable OSS checkers) and are intentionally not in this table.

## What is LLMScout, and why does it exist

LLMScout is an independent, open-source command-line tool that checks a website for 21 technical-SEO and generative-engine-optimization issues. It ships as two genuinely independent, feature-equivalent distributions: a TypeScript/Node CLI with two runtime dependencies (`cheerio`, `commander`) and zero external interpreter or browser, and a Python CLI with zero runtime dependencies at all. Neither `child_process` (TypeScript) nor a subprocess call (Python) appears anywhere in either implementation's checks.

It exists to replace the install flow of an existing project, [`AgriciDaniel/claude-seo`](https://github.com/AgriciDaniel/claude-seo), for one specific class of problem. That project is a Claude Code SEO/GEO skill that carries out its checks by shelling out to Python scripts (Playwright-based rendering, `pip`-installed dependencies) from skill instructions. That external-toolchain-plus-path-resolution chain is the root cause behind a recurring pattern of install/Windows/path bugs filed against it, including three issues (since closed, but each documenting the architectural failure mode this project exists to avoid): [#137](https://github.com/AgriciDaniel/claude-seo/issues/137) (a fresh `/plugin` install provisions neither the Python dependencies nor Playwright Chromium), [#138](https://github.com/AgriciDaniel/claude-seo/issues/138) (skill instructions hardcode `python3`, which does not exist on a stock Windows install), and [#139](https://github.com/AgriciDaniel/claude-seo/issues/139) (skills call `scripts/*.py` through a relative path that does not resolve when the scripts live under the plugin root). The same class of pain shows up independently in `zubair-trabzada/geo-seo-claude`, another actively used Claude Code GEO skill (issues [#69](https://github.com/zubair-trabzada/geo-seo-claude/issues/69), [#21](https://github.com/zubair-trabzada/geo-seo-claude/issues/21), [#3](https://github.com/zubair-trabzada/geo-seo-claude/pull/3)) -- the failure mode is architectural, not specific to one project.

LLMScout is not a fork of either project. It shares no code with them, has a different name, and reimplements the equivalent checks from scratch. The design choice that matters is what it does not do: because the checks run inside the host process rather than by launching an external interpreter and a headless browser, the entire failure class behind those bugs does not exist here. There is no interpreter to provision, no `pip install` to run beyond the package itself, no browser binary to download, and no relative script path to resolve, so a fresh install behaves the same on every platform. The direct cost of that choice is that the content-extraction check is a static-HTML heuristic and cannot evaluate content that only appears after client-side JavaScript renders. The check documents this limitation in its own output.

Beyond the install-fix wedge, LLMScout's checks track the concrete, evidence-backed direction the GEO space has actually moved since mid-2025 -- see [Why GEO checks matter right now](#why-geo-checks-matter-right-now) for the cited sources behind that claim, including the training-versus-search AI crawler split, Markdown content negotiation, and Google's own documented FAQ-rich-result deprecation.

LLMScout is at v0.3, freshly renamed from its original name, SeoFleet. Both distributions are being republished under the new package name (`llmscout-cli` on both npm and PyPI) -- see [Install](#install) for both paths, and the badges above for live version status.

## FAQ

**Does LLMScout require Python?**
No. The npm distribution is pure TypeScript/Node with two dependencies (`cheerio`, `commander`). There is no `pip install` step and no Python interpreter involved at any point in that path.

**Does it use Playwright or a headless browser?**
No, in either distribution. Both fetch HTML over `http(s)` and parse it (`cheerio` in TypeScript, the standard library in Python). There is no Chromium download and no subprocess call anywhere in either implementation's checks. The trade-off is that the content-extraction check reads static HTML only and cannot see JavaScript-rendered content. It says so in its own result message.

**What does "zero-config" mean here, concretely?**
`llmscout init <path>` writes a working `llmscout.json` and a Claude Code skill file with no prompts. The one value you must supply is your live site URL (via `--site-url` or by editing the file), because the tool cannot infer a project's public URL from its local files. After that, `llmscout check <path>` runs with no further configuration; all 21 checks run by default.

**Why does LLMScout track training crawlers and search crawlers separately?**
Because OpenAI and Anthropic actually run them as separate, independently blockable user agents now. Blocking GPTBot (training) has no effect on whether OAI-SearchBot can still retrieve and cite your page live in a ChatGPT answer, and the same split applies to ClaudeBot versus Claude-SearchBot. Reporting them together would hide a real, actionable distinction.

**Does LLMScout tell me to add an llms.txt?**
No, it only reports whether one exists. `llms.txt` is a real, growing convention, but Google has stated publicly it does not support it -- see [Why GEO checks matter right now](#why-geo-checks-matter-right-now) for the source. LLMScout reports facts a site owner can act on; it does not take a position on an unsettled question.

**Why not just fix claude-seo or geo-seo-claude directly instead of building a separate tool?**
Their install/Windows bugs share a single root cause: checks are performed by shelling out to an external interpreter-plus-browser toolchain from skill instructions. Patching each symptom leaves that architecture in place. LLMScout removes the architecture instead: with no external toolchain, that class of install and path failure cannot recur. It is an independent reimplementation, not a patch.

**Can I run it against many sites at once?**
Yes. `llmscout fleet manifest.json` runs the full suite against every site in a local JSON manifest in one invocation, and `--out-dir` writes one auto-named report file per site instead of one combined stdout dump -- built for agencies checking many client sites.

**Can an agent or script consume the output?**
Yes. Pass the global `--json` flag to any command for structured JSON, including per-check `id`, `status`, `message`, and `fix` fields, plus a summary object. Exit codes are stable: `0` clean, `1` at least one FAIL, `2` a usage/config error.

**Is there a Python version?**
Yes -- `pip install llmscout-cli` installs a genuine, independent Python port (not a wrapper around the Node binary), with zero runtime dependencies. It runs the same 21 checks with the same PASS/WARN/FAIL verdicts as this npm package. See [python/README.md](./python/README.md).

**Can I use LLMScout commercially, or in a closed-source project?**
Yes. Both distributions are MIT licensed (see [LICENSE](./LICENSE)): you can use, modify, and redistribute LLMScout in commercial and closed-source work, with no royalty and no obligation to open-source anything it checks. The only requirement is keeping the copyright notice and license text if you redistribute the source itself.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for the full guide, covering both the TypeScript and Python codebases. Useful commands for this package:

```bash
npm install
npm run build       # tsc build to dist/
npm run typecheck   # tsc --noEmit
npm test            # vitest run (248 tests)
npm run test:coverage
npm run lint        # eslint src test
```

CI (`.github/workflows/ci.yml`) runs lint, typecheck, build, coverage, and `npm audit --audit-level=high` on every push and pull request to `main`. Issues and pull requests are welcome at <https://github.com/RudrenduPaul/LLMScout/issues>.

Adding a 22nd check is intentionally small: implement the `Check` interface (`src/types.ts`) in a new file under `src/checks/`, then register it in `src/checks/index.ts` (and the Python equivalent under `python/src/llmscout/checks/`, per [CONTRIBUTING.md](./CONTRIBUTING.md)).

## License

MIT. See [LICENSE](./LICENSE).
