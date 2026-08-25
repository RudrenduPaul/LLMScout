# Security Policy

LLMScout fetches content from URLs its own configuration points it at
(a site's homepage, robots.txt, sitemap.xml, llms.txt) and parses that
content. A vulnerability that lets a fetched response escape the intended
read-only, no-eval handling of that content -- for example, a crafted
response body triggering code execution, or a redirect target that
reaches an internal/non-`http(s)` resource -- is taken seriously and
handled as a priority.

## Supported versions

| Package | Version | Supported |
| --- | --- | --- |
| `llmscout-cli` (npm) | 0.3.x | Yes |
| `llmscout-cli` (PyPI) | 0.3.x | Yes |

Both distributions are pre-1.0 and under active development. Security
fixes land on the latest `0.3.x` release of each; there is no older
supported line to backport to yet.

## Reporting a vulnerability

**Do not open a public GitHub issue for a security vulnerability.**

Report it privately via
[GitHub Security Advisories](https://github.com/RudrenduPaul/LLMScout/security/advisories/new)
for this repository. Include:

- Which distribution is affected (npm package, PyPI package, or both).
- A minimal reproduction: the URL/response shape that triggers the issue,
  and the command or library call used.
- What you expected LLMScout to do, and what it actually did.
- Your assessment of impact.

## What counts as in scope

- Any code path where content fetched from a scanned site (HTML,
  robots.txt, sitemap.xml, llms.txt, or a redirect `Location` header) is
  executed, evaluated, or dynamically imported, rather than only read and
  parsed.
- A redirect chain that reaches a non-`http(s)` scheme (e.g. `file://`)
  without being refused. Both CLIs validate every hop, not just the
  initial URL: the TypeScript fetch wrapper (`src/fetch-utils.ts`) and its
  Python port (`python/src/llmscout/fetch_utils.py`) both reject a
  redirect `Location` that isn't `http(s)`, and both bound the redirect
  chain at 5 hops.
- A crafted response body that causes unbounded resource consumption
  (ReDoS in a check's regex, unbounded memory) in either CLI's checks or
  its HTML/robots.txt parsing.
- A crafted URL or fleet-manifest path that reads or writes outside the
  intended project directory (path traversal in `init`, `check`, or
  `fleet`).

## Trust model for local paths

`init`'s target directory and a `fleet` manifest's `path` entries are
treated as trusted local input, the same way `mkdir` or `cp` treats a
path argument -- neither CLI sandboxes or restricts them to a base
directory. This is intentional: both are local developer tools operating
with the invoking user's own filesystem permissions, not services
processing untrusted remote input. If you build automation that feeds an
externally-supplied path into `init` or a fleet manifest without your own
validation, that validation is your responsibility.

## What is out of scope

- False positives/negatives in a check's own SEO/GEO heuristic (for
  example, the content-extraction check's documented inability to see
  JavaScript-rendered content) -- these are documented, known limitations
  of static analysis, not vulnerabilities. Open a normal issue for these.
- Vulnerabilities in a site LLMScout is checking -- report those to that
  site's own owners, not here.

## Response

We aim to acknowledge a report within 5 business days and to have a fix or
a mitigation plan within 30 days for a confirmed, in-scope vulnerability.
Credit is given in the release notes unless you ask to remain anonymous.
