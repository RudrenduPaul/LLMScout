"""
MCP (Model Context Protocol) stdio server wrapping the llmscout CLI.

Pilot implementation of the generic MCP server template described in
strategy-b2a-ideas/gtm/mcp-plugins.md ("Generic MCP Server Template"): one
exposed tool that shells out to the underlying CLI with --json appended,
parses the JSON stdout, and returns it as the tool result.

Deliberately shells out to the Node/TypeScript CLI (`npx llmscout`) rather
than calling into this same Python package's own native `llmscout.cli`
module. Per the template, the MCP wrapper's implementation language is
independent of the CLI's: this keeps one wrapper shape reusable across the
whole portfolio regardless of whether a given repo's CLI is Node or Python,
and it exercises the actual published `llmscout` npm binary end to end
rather than a parallel code path.

stdout is reserved for MCP's JSON-RPC framing, so anything this module
logs goes to stderr.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Any

from mcp.server import MCPServer

# Local-test override: point at a built dist/cli.js instead of `npx llmscout`.
# The npm package may not be globally linked on a dev machine, so testing
# this wrapper against a repo checkout needs a direct `node <path>` command.
# Production default (no env var set) is `npx llmscout`.
_LOCAL_CLI_JS = os.environ.get("LLMSCOUT_CLI_JS")


def _base_command() -> list[str]:
    if _LOCAL_CLI_JS:
        return ["node", _LOCAL_CLI_JS]
    return ["npx", "llmscout"]


_TOOL_DESCRIPTION = """Run the llmscout CLI (published as `llmscout-cli` on npm and PyPI) and return its structured output as JSON. Call this to scaffold an SEO/GEO config for a local project, run llmscout's 21-check technical-SEO and generative-engine-optimization audit against a site, or batch-run that audit across a fleet of sites, without shelling out yourself.

Call it once you have a local project directory path, and for `check`/`fleet` a site that already has an `llmscout.json` (created by a prior `init` call, or already present in the project). Do not call `check` on a directory that has never been `init`-ed: it fails fast with a missing-config error rather than guessing a site URL. No API key or auth is required. `check` and `fleet` make live outbound HTTP requests to the target site(s) (the page itself, robots.txt, sitemap.xml, and related resources) so they need network access and will be slower or noisier against unreachable hosts; `init` only writes local files (a config and a small skill file) and makes no network calls. All subcommands are safe to re-run: `init` overwrites its scaffolded config, and `check`/`fleet` never write anything unless `--out-dir` is given, in which case a report file is rewritten each run. On failure (non-zero exit, bad args, unreachable site), the underlying process's stderr is captured rather than raised.

`args` is a list[str] of the CLI's own argv, split exactly as you would type it on a command line (never a single shell string), and should never include `--json` yourself since this wrapper appends it automatically. Real examples:
  - ["init", "./my-site", "--site-url", "https://example.com"]
  - ["check", "./my-site", "--out-dir", "./reports"]
  - ["fleet", "./fleet.json", "--out-dir", "./reports"]
Pass ["--help"] or ["<subcommand>", "--help"] (e.g. ["check", "--help"]) as `args` to discover the live, authoritative list of subcommands and flags.

Returns a dict. On success it is the parsed JSON the CLI printed: `init` returns the scaffolded config paths, `check` returns {siteUrl, summary: {pass, warn, fail, total}, results: [{id, name, category, status, message, fix?}, ...]}, and `fleet` returns one such result per site. On failure it returns {"error": ..., "stderr": ..., "command": ...} if the CLI exited non-zero, or {"error": ..., "stdout": ..., "command": ...} if stdout was not valid JSON; it never raises."""


mcp = MCPServer(name="llmscout")


@mcp.tool(description=_TOOL_DESCRIPTION)
def run(args: list[str]) -> dict[str, Any]:
    """Run the llmscout CLI with `args` (subcommand + its own arguments,
    e.g. ["init", "/path/to/project", "--site-url", "https://example.com"])
    and return its parsed `--json` output. `--json` is appended
    automatically, callers should not pass it themselves."""
    command = [*_base_command(), *args, "--json"]
    print(f"llmscout-mcp: running {command!r}", file=sys.stderr)
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=120)
    except OSError as exc:
        return {"error": f"failed to exec {command!r}: {exc}"}
    if proc.stderr:
        print(f"llmscout-mcp: stderr: {proc.stderr}", file=sys.stderr)
    if proc.returncode != 0:
        return {
            "error": f"llmscout exited with code {proc.returncode}",
            "stderr": proc.stderr.strip(),
            "command": command,
        }
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return {
            "error": f"could not parse JSON output: {exc}",
            "stdout": proc.stdout,
            "command": command,
        }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
