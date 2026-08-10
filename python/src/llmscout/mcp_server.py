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


def _capture_help() -> str:
    """Best-effort `--help` capture, used as the tool's dynamic description
    instead of a hardcoded string."""
    fallback = "Run the llmscout CLI (init/check/fleet subcommands)."
    try:
        proc = subprocess.run(
            [*_base_command(), "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return proc.stdout.strip() or fallback
    except Exception as exc:  # noqa: BLE001 - degrade to a generic description
        print(f"llmscout-mcp: could not capture --help: {exc}", file=sys.stderr)
        return fallback


mcp = MCPServer(name="llmscout")


@mcp.tool(description=_capture_help())
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
