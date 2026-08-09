# Changelog

All notable changes to LLMScout are documented in this file. This
changelog covers both distributions -- the npm package (`llmscout-cli`,
TypeScript) and the PyPI package (`llmscout-cli`, Python) -- since they
run the same checks; entries note which distribution they apply to.

## [0.3.6] (npm) / [0.3.5] (PyPI) - 2026-08-08

### Fixed

- `llmscout --version` printed a stale, hardcoded version string that had
  drifted from the actually published package version on both
  distributions: npm printed `0.3.0` while the published package was
  `0.3.5`, and PyPI printed `0.3.3` while the published package was
  `0.3.4`. Both distributions now read their version from the package's
  own metadata at runtime instead of a string literal that has to be
  remembered on every release -- `package.json` via `fs.readFileSync` for
  npm, `importlib.metadata.version("llmscout-cli")` for PyPI -- so this
  class of drift cannot recur. Found via a real clean-install smoke test
  (`npm pack` + global install from the tarball, and a fresh venv `pip
  install`), not a code read.

## [0.3.0] - 2026-07-22

### Changed

- Renamed project from SeoFleet to LLMScout.
- npm package: `seofleet-cli` -> `llmscout-cli`.
- PyPI package: `seofleet-cli` -> `llmscout-cli`.
- CLI binary: `seofleet` -> `llmscout`.
- Config file: `seofleet.json` -> `llmscout.json`.
- GitHub repo: `RudrenduPaul/SeoFleet` -> `RudrenduPaul/LLMScout`.
- The old `seofleet-cli` packages received one final release each (npm
  and PyPI, `0.2.2`) carrying a deprecation notice before this rename;
  no further releases will be published under that name.

## [0.2.0] - 2026-07-18

Nine new checks (nine, not eight -- one item shipped as a bug fix to an
existing check rather than a new one) bringing the total from 12 to 21,
plus two CLI features, in both the npm and PyPI distributions.

### Added

- `open-graph`, `twitter-card`, and `robots-meta-directives` technical
  checks.
- `speakable-schema`, `organization-schema`, `markdown-negotiation`, and
  `link-header` GEO checks.
- `image-weight` and `redirect-chain` technical checks, reusing the
  redirect-hop data the fetch layer already computed internally.
- `--user-agent <string>` global flag to override the default outbound
  User-Agent; the default itself changed from a bot-style identifying
  string to a real browser User-Agent, since some SSR frameworks and CDNs
  reject non-browser UAs outright.
- `--out-dir <dir>` flag on `check` and `fleet`, writing one auto-named
  report file per site (slugified from the site URL, or the fleet
  manifest's `name` field) instead of only a combined stdout summary.
- `ai-crawler-directives` now tracks `OAI-SearchBot` and `Claude-SearchBot`
  as crawlers separate from their training-only counterparts (`GPTBot`,
  `ClaudeBot`), plus `Applebot-Extended` -- seven bots total, up from four.
- Sitemap discovery now falls back to a robots.txt `Sitemap:` directive
  when the default `/sitemap.xml` isn't reachable.

### Fixed

- `sitemap-xml` now detects an HTML-shaped response body (e.g. a CDN
  challenge page) and reports it distinctly from a genuinely malformed
  sitemap.
- `redirect-chain`'s FAIL condition previously could not fire against real
  fetch output, since it only inspected the `hops` array, which by
  construction never contains a terminal error status. It now also checks
  the resource's own terminal status.

## [Python 0.1.0] - 2026-07-16

Initial public release of the Python port, published to PyPI as
`llmscout-cli` (`pip install llmscout-cli`). Complementary to, not a
replacement for, the existing npm package -- both are first-class and
maintained together. See `python/README.md` for Python-specific usage.

### Added

- `llmscout [init|check|fleet]` CLI (console script `llmscout`, package
  `llmscout`) with the same commands and `--json` global flag as the npm
  CLI's own `--help` output.
- Programmatic library API: `from llmscout import load_site, run_checks,
  ALL_CHECKS, TECHNICAL_CHECKS, GEO_CHECKS`, returning the same
  `CheckResult` shape (`id`, `name`, `category`, `status`, `message`,
  optional `fix`) as the CLI's own JSON output.
- All 12 checks reimplemented as genuine Python logic against the same
  check contract the npm package uses (7 technical: title, meta
  description, canonical tag, robots.txt, sitemap.xml, heading structure,
  image alt coverage; 5 GEO: structured data / JSON-LD, llms.txt, AI
  crawler directives, FAQ schema, content extraction friendliness) -- the
  same thresholds, the same PASS/WARN/FAIL verdicts, and the same message/
  fix text as the TypeScript originals.
- Fleet mode (`llmscout fleet <manifest.json>`): runs the full 12-check
  suite against every site declared in a local JSON manifest in one
  invocation, ported from `src/fleet.ts`.
- **Zero runtime dependencies.** Unlike the npm package (which uses
  `cheerio` for HTML parsing and `commander` for argument parsing), the
  Python port uses only the standard library: a small `html.parser`-based
  tree builder (`llmscout.html_util`, no TypeScript equivalent needed --
  cheerio provided this directly on that side) in place of cheerio, and
  `argparse` in place of commander. There is no third-party HTTP library
  either -- the redirect-following, scheme-validating fetch wrapper
  (`llmscout.fetch_utils.safe_fetch`) is built on `urllib.request`.
- Full pytest suite (106 tests) ported from the TypeScript vitest suite,
  covering all 12 checks (FAIL/WARN/PASS branches), the HTML tree builder,
  the fetch wrapper's URL/redirect validation, config loading, fleet
  manifest loading, output formatting, `init` scaffolding, the CLI, and an
  end-to-end init-then-check pipeline test -- all served by fetch stubs, no
  real network calls in the automated suite.

## [0.1.0] - npm, initial public release

The original TypeScript/Node CLI. See the
[project README](https://github.com/RudrenduPaul/LLMScout#readme) for its
own history; this changelog file was added alongside the Python port and
does not retroactively document npm-only changes that predate it.
