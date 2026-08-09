import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import * as path from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";

const CLI = path.resolve(__dirname, "..", "dist", "cli.js");
const PACKAGE_VERSION = (
  JSON.parse(readFileSync(path.resolve(__dirname, "..", "package.json"), "utf-8")) as { version: string }
).version;

function runCli(args: string[]): { stdout: string; stderr: string; status: number } {
  try {
    const stdout = execFileSync("node", [CLI, ...args], { encoding: "utf-8" });
    return { stdout, stderr: "", status: 0 };
  } catch (err) {
    const e = err as { stdout?: string; stderr?: string; status?: number };
    return { stdout: e.stdout ?? "", stderr: e.stderr ?? "", status: e.status ?? 2 };
  }
}

let dir: string;

beforeEach(() => {
  dir = mkdtempSync(path.join(tmpdir(), "llmscout-cli-e2e-"));
});

afterEach(() => {
  rmSync(dir, { recursive: true, force: true });
});

describe("CLI", () => {
  it("prints help listing all three subcommands", () => {
    const { stdout, status } = runCli(["--help"]);
    expect(status).toBe(0);
    expect(stdout).toMatch(/init/);
    expect(stdout).toMatch(/check/);
    expect(stdout).toMatch(/fleet/);
  });

  it("lists --user-agent as a global option in help", () => {
    const { stdout, status } = runCli(["--help"]);
    expect(status).toBe(0);
    expect(stdout).toMatch(/--user-agent <string>/);
  });

  it("prints the version", () => {
    // Asserts against package.json's actual version rather than a hardcoded
    // literal, so this test can't silently drift from the real published
    // version the way the CLI's own `.version()` string once did.
    const { stdout, status } = runCli(["--version"]);
    expect(status).toBe(0);
    expect(stdout.trim()).toBe(PACKAGE_VERSION);
  });

  it("scaffolds a real project directory via `init`", () => {
    const { stdout, status } = runCli(["init", dir]);
    expect(status).toBe(0);
    expect(stdout).toContain("Created");
  });

  it("supports --json on init", () => {
    const { stdout, status } = runCli(["--json", "init", dir]);
    expect(status).toBe(0);
    expect(() => JSON.parse(stdout)).not.toThrow();
  });

  it("exits 2 on `check` against a directory with no llmscout.json", () => {
    const { status, stderr } = runCli(["check", dir]);
    expect(status).toBe(2);
    expect(stderr).toMatch(/Run `llmscout init/);
  });

  it("exits 2 on `check` against a nonexistent path", () => {
    const { status } = runCli(["check", path.join(dir, "nope")]);
    expect(status).toBe(2);
  });

  it("exits 2 on `fleet` with a missing manifest", () => {
    const { status } = runCli(["fleet", path.join(dir, "fleet.json")]);
    expect(status).toBe(2);
  });

  it("lists --out-dir as a check subcommand option in help", () => {
    const { stdout, status } = runCli(["check", "--help"]);
    expect(status).toBe(0);
    expect(stdout).toMatch(/--out-dir <dir>/);
  });

  it("lists --out-dir as a fleet subcommand option in help", () => {
    const { stdout, status } = runCli(["fleet", "--help"]);
    expect(status).toBe(0);
    expect(stdout).toMatch(/--out-dir <dir>/);
  });
});
