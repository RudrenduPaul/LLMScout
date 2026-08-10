# llmscout-cli (Python)

<!-- mcp-name: io.github.RudrenduPaul/llmscout -->
<!-- Ownership-proof string for registry.modelcontextprotocol.io publishing. Do not remove. -->


Zero-config SEO and GEO (generative engine optimization) checker: 21 checks
against a live site, plus a multi-site fleet mode for agencies checking
several client sites at once, in pure Python with no extra runtime
toolchain -- no headless browser, no separate interpreter to provision.

[![PyPI version](https://img.shields.io/pypi/v/llmscout-cli.svg)](https://pypi.org/project/llmscout-cli/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/RudrenduPaul/LLMScout/blob/main/LICENSE)
[![Python versions](https://img.shields.io/pypi/pyversions/llmscout-cli.svg)](https://pypi.org/project/llmscout-cli/)
[![CI](https://github.com/RudrenduPaul/LLMScout/actions/workflows/ci.yml/badge.svg)](https://github.com/RudrenduPaul/LLMScout/actions/workflows/ci.yml)
[![npm version](https://img.shields.io/npm/v/llmscout-cli.svg)](https://www.npmjs.com/package/llmscout-cli)

## Why this exists

LLMScout checks a website for 21 technical-SEO and GEO issues --
title/meta description length, canonical tags, robots.txt/sitemap.xml
reachability (with a robots.txt `Sitemap:` fallback), heading structure,
image alt coverage and weight, Open Graph and Twitter Card tags, meta
robots directives, redirect-chain health, JSON-LD structured data, llms.txt,
AI-crawler directives (training and search crawlers tracked separately --
GPTBot/OAI-SearchBot, ClaudeBot/Claude-SearchBot, PerplexityBot,
Google-Extended, Applebot-Extended), FAQ schema, Speakable schema,
Organization schema, Markdown content negotiation, an RFC 8288 Link header,
and content-extraction friendliness -- and reports PASS/WARN/FAIL with a
fix suggestion for anything short of a clean pass. This package is the
Python distribution of the tool: a genuine, independent port of the npm
CLI's logic, not a wrapper around the Node binary. It ships with **zero
runtime dependencies** -- HTML parsing and HTTP fetching both use only the
Python standard library.

## Install

```bash
pip install llmscout-cli
```

or with [uv](https://docs.astral.sh/uv/):

```bash
uv add llmscout-cli
```

The complementary JS/TS distribution installs from npm:
`npm install -g llmscout-cli` -- see the
[project README](https://github.com/RudrenduPaul/LLMScout#readme) for that
package. Both packages read the same 21-check spec and are intended to
report the same PASS/WARN/FAIL verdicts for the same site; neither is
deprecated in favor of the other.

## Quickstart

```bash
llmscout init ./my-site --site-url https://example.com
llmscout check ./my-site
```

`init` scaffolds a `llmscout.json` config (and a Claude Code skill file) in
the target directory; `check` runs all 21 checks against the configured
`siteUrl` and prints a PASS/WARN/FAIL line per check plus a summary. Pass
`--json` before the subcommand for structured output an agent can parse:

```bash
llmscout --json check ./my-site
```

Or call the library directly (the agent-native path, no subprocess):

```python
from llmscout import load_site, run_checks, ALL_CHECKS

ctx = load_site("https://example.com")
results = run_checks(ALL_CHECKS, ctx)
for r in results:
    print(f"[{r.status}] ({r.category}) {r.name}: {r.message}")
```

## How it works

```
llmscout.json -> site URL -> fetch homepage + robots.txt + sitemap.xml + llms.txt (parallel)
   -> 21 checks (12 technical + 9 GEO) run against the shared fetched context
   -> PASS / WARN / FAIL per check -> exit code (0 clean / 1 any FAIL / 2 usage error)
```

Full data model, the 21 checks explained, and fleet-mode semantics are in
[docs/concepts.md](https://github.com/RudrenduPaul/LLMScout/blob/main/docs/concepts.md)
and [docs/getting-started.md](https://github.com/RudrenduPaul/LLMScout/blob/main/docs/getting-started.md).
The checks are reimplemented as genuine Python logic against the same
check contract the npm package uses (`Check.run(ctx) -> CheckResult`) --
see those docs for what each check actually verifies.

## The 21 checks

Each check reports `PASS`, `WARN`, or `FAIL`, with a fix suggestion for anything that is not a clean PASS. A `WARN` is a missed optimization, not a broken page, and never fails the run on its own.

### Technical SEO (12)

| Check (`id`) | What it verifies |
| --- | --- |
| Title tag (`title`) | A `<title>` exists and is within 10-60 characters. |
| Meta description (`meta-description`) | A `<meta name="description">` exists and is within 50-160 characters. |
| Canonical tag (`canonical`) | A `<link rel="canonical">` exists and its href is a valid URL (relative hrefs are resolved, not penalized). |
| robots.txt (`robots-txt`) | `/robots.txt` is reachable and contains at least one `User-agent` directive. |
| sitemap.xml (`sitemap-xml`) | `/sitemap.xml` is reachable and valid, with a `Sitemap:` directive in robots.txt checked as a fallback location. |
| Heading structure (`heading-structure`) | Exactly one `<h1>`, and no skipped heading levels. |
| Image alt coverage (`image-alt`) | `<img>` tags have an `alt` attribute (an intentional `alt=""` for decorative images counts as covered). |
| Open Graph tags (`open-graph`) | `og:title`, `og:description`, `og:image`, and `og:url` meta tags are present. |
| Twitter/X Card tags (`twitter-card`) | A valid `twitter:card` meta tag and its required companion fields are present. |
| Meta robots directives (`robots-meta-directives`) | Advanced snippet-control directives (`max-snippet`, `max-image-preview`, `max-video-preview`) are set, and flags an outright `noindex`. |
| Image weight (`image-weight`) | Each image's actual byte size (via a HEAD request), flagging oversized images that slow page load. |
| Redirect chain (`redirect-chain`) | The homepage's full redirect chain, warning on long chains and failing if the chain dead-ends in an error status. |

### GEO / generative engine optimization (9)

| Check (`id`) | What it verifies |
| --- | --- |
| Structured data (`structured-data`) | JSON-LD `<script type="application/ld+json">` blocks exist and parse as valid JSON. |
| llms.txt (`llms-txt`) | An `/llms.txt` is present at the site root (an emerging, non-standardized convention; absence is informational). |
| AI crawler directives (`ai-crawler-directives`) | Reports the robots.txt allow/disallow state for GPTBot, OAI-SearchBot, ClaudeBot, Claude-SearchBot, PerplexityBot, Google-Extended, and Applebot-Extended. This is a report of what is configured, never a recommendation to allow or block. |
| FAQ schema (`faq-schema`) | `FAQPage` JSON-LD is present (informational; only relevant to pages that actually have an FAQ). |
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
usage: llmscout [-h] [-V] [--json] [--user-agent USER_AGENT]
                {init,check,fleet} ...

Zero-config, cross-platform SEO and GEO checks for local projects, with no
extra runtime toolchain.

positional arguments:
  {init,check,fleet}
    init                Scaffold a LLMScout setup (llmscout.json + a Claude
                        Code skill file) into a target directory
    check               Run SEO/GEO checks against a local project's
                        configured site
    fleet               Run the full check suite against every site listed in
                        a fleet manifest

options:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  --json                output structured JSON instead of human-readable text
  --user-agent USER_AGENT
                        override the default User-Agent header sent on
                        outbound fetches
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

```bash
llmscout fleet ./fleet.json
```

Runs the full 21-check suite against every site declared in a local JSON
manifest (`{"sites": [{"name": ..., "path": ...}]}`) in one invocation --
local filesystem only, no SSH, no remote execution. Aimed at agencies or
teams checking several client repos side by side. Add `--out-dir ./reports`
to also write one auto-named report file per site, named from the
manifest's `name` field.

## CI integration

```yaml
- uses: actions/checkout@v4
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'
- run: pip install llmscout-cli
- run: llmscout check ./my-site --json > results.json
```

Full walkthrough in
[docs/integrations/ci.md](https://github.com/RudrenduPaul/LLMScout/blob/main/docs/integrations/ci.md).

## Comparison

Every cell below is drawn from a verifiable source (a repo file, a package manifest, or an open issue), cited under the table. "Checker" means the tool audits an existing live site; "generator" means it emits SEO/GEO asset files for you to publish.

| | LLMScout (Python) | claude-seo (AgriciDaniel) | geo-seo-claude (zubair-trabzada) | geo-optimizer-skill (Auriti-Labs) |
| --- | --- | --- | --- | --- |
| Runtime dependencies | Zero (stdlib only) | Python 3.10+, Playwright optional | Python 3.x, Playwright optional | Python 3.9+ |
| Requires Playwright / headless browser | No | Optional (Chromium auto-installed by `install.sh` for SPA rendering) | Optional, for some checks | Not required for core function |
| Install | `pip install llmscout-cli` or `uv add llmscout-cli` | `git clone` + `install.sh` / `install.ps1`, or Claude Code `/plugin` | `git clone` + `install.sh` / `install-win.sh` | `pip install` or `uvx` |
| Cross-platform / Windows out of the box | Yes (stdlib only, no shelling out) | Ships a Windows `install.ps1`, but fresh-install/Windows/path failures are a recurring pattern: issues [#137](https://github.com/AgriciDaniel/claude-seo/issues/137), [#138](https://github.com/AgriciDaniel/claude-seo/issues/138), [#139](https://github.com/AgriciDaniel/claude-seo/issues/139) | Windows install pain is a recurring pattern here too: issues [#69](https://github.com/zubair-trabzada/geo-seo-claude/issues/69), [#21](https://github.com/zubair-trabzada/geo-seo-claude/issues/21), [#3](https://github.com/zubair-trabzada/geo-seo-claude/pull/3) | pip/uv are cross-platform; not verified further |
| AI-crawler bot coverage | 7 bots, training and search crawlers tracked separately (GPTBot/OAI-SearchBot, ClaudeBot/Claude-SearchBot, PerplexityBot, Google-Extended, Applebot-Extended) | Not a dedicated check | Not a dedicated check | Not verified |
| Markdown content negotiation check | Yes (`markdown-negotiation`) | No | No | No |
| Role | Checker | Checker | Checker + report generator | Checker |
| Coverage | Technical + GEO (21 checks) | Technical + GEO (broad) | GEO-focused | Technical + GEO |
| License | MIT | MIT | Not verified | MIT |

Sources: LLMScout, from this package's `pyproject.toml` (`dependencies = []`) and `src/llmscout/`. claude-seo, from its README install section and open issues #137/#138/#139. geo-seo-claude, from its README and issue tracker (#69, #21, #3). geo-optimizer-skill, from its README (Python 3.9+, `pip install`/`uvx`, MIT).

The complementary npm/TypeScript distribution of LLMScout has its own comparison table with the same competitors in the [main project README](https://github.com/RudrenduPaul/LLMScout#comparison).

## Security

llmscout's fetch layer only ever dials `http(s)`, follows redirects
manually one hop at a time, refuses to follow a redirect whose `Location`
targets a non-`http(s)` scheme, and bounds the redirect chain at 5 hops so
a redirect loop can't hang the process -- see
[SECURITY.md](https://github.com/RudrenduPaul/LLMScout/blob/main/SECURITY.md)
for the full policy and how to report a vulnerability. **Honest note**:
this project does not currently publish SLSA provenance, Sigstore
signatures, or an SBOM, and has no OpenSSF Scorecard badge set up -- none
of that infrastructure exists yet for either distribution, so it isn't
claimed here.

## FAQ

**Does this package require Node.js or the npm distribution?**
No. `llmscout-cli` on PyPI is a genuine, independent Python port with zero runtime dependencies -- not a wrapper around the npm CLI. It runs the same 21 checks with the same PASS/WARN/FAIL verdicts.

**Does it use Playwright or a headless browser?**
No. HTML parsing and HTTP fetching both use only the Python standard library. There is no Chromium download and no subprocess call anywhere in the checks. The trade-off is that the content-extraction check reads static HTML only and cannot see JavaScript-rendered content -- it says so in its own result message.

**How is this different from `claude-seo` or `geo-seo-claude`?**
Both of those are Claude Code skills that shell out to Python scripts (and, for some checks, Playwright-based rendering) from skill instructions. That external-toolchain-plus-path-resolution chain is the root cause behind a recurring pattern of install/Windows/path bugs filed against both projects -- see the [Comparison](#comparison) table above for the specific open issues. `llmscout-cli` runs checks inside the host process instead, so that failure class does not exist here.

**Does it need my own API keys?**
No. There is no LLM call anywhere in the check pipeline -- every check is a deterministic HTML/HTTP inspection (parsing tags, following redirects, checking headers). No account, API key, or external service is required to run it.

**Is this safe to run against a production site?**
Yes. The fetch layer only ever dials `http(s)`, refuses to follow a redirect whose `Location` targets a non-`http(s)` scheme, and bounds the redirect chain at 5 hops so a redirect loop can't hang the process. It only ever performs `GET`/`HEAD` requests; it never submits forms, follows links beyond the declared entry points, or writes anything to the target site. See [Security](#security) above for the full policy.

**Can I use this from an agent, not just a human running the CLI?**
Yes, two ways: pass the global `--json` flag to any command for structured output (`id`, `status`, `message`, `fix` fields plus a summary), or import the library directly (`from llmscout import load_site, run_checks, ALL_CHECKS`) with no subprocess call at all -- see [Quickstart](#quickstart).

**Is this a library or just a CLI?**
Both. The `llmscout` console script is the CLI entry point, and the same package is directly importable for programmatic use (`load_site`, `run_checks`, `select_checks`, `ALL_CHECKS`, `TECHNICAL_CHECKS`, `GEO_CHECKS`).

**Can I run it against many sites at once?**
Yes. `llmscout fleet manifest.json` runs the full suite against every site in a local JSON manifest in one invocation, and `--out-dir` writes one auto-named report file per site instead of one combined stdout dump -- built for agencies checking many client sites.

**What Python versions are supported?**
3.9 through 3.13, per this package's `classifiers`. No third-party runtime dependencies means there's nothing else to version-match.

**Can I use this commercially, or in a closed-source project?**
Yes. MIT licensed (see [License](#license) below): use, modify, and redistribute in commercial and closed-source work, with no royalty and no obligation to open-source anything it checks.

## Contributing

See [CONTRIBUTING.md](https://github.com/RudrenduPaul/LLMScout/blob/main/CONTRIBUTING.md).

```bash
cd python
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## License

MIT, see [LICENSE](https://github.com/RudrenduPaul/LLMScout/blob/main/LICENSE).
