# Quickstart — spectrIDA on a Windows x86/x64 PE

A guided first run, from an empty machine to a named, exportable function list.
Works for both 64-bit (PE32+) and — as of this fork — 32-bit x86 PEs.

---

## Step 0 — Project workspace (persistent memory)

This project keeps a model-neutral persistent workspace so any agent (or
future you) can resume without the chat history. It lives in the project
directory — by convention:

```
%USERPROFILE%\Documents\GitHub\spectrIDA-Reverse_Engineering_Stack
```

If you cloned this fork, **the workspace is already bootstrapped** at the
repo root: `AGENTS.md`, `PROJECT_STATUS.md`, `CONTEXT.md`, `stages/`,
`runs/`, `shared/knowledge/okf/`, `retrieval/`, `_config/`.

1. Read `AGENTS.md` → `PROJECT_STATUS.md` → `CONTEXT.md` (in that order).
2. If you're starting a *new* project elsewhere, the bootstrap specification
   is at `docs/PERSISTENT-MEMORY-BOOTSTRAP-SPEC.md` — hand it to any agent
   and it will create the same structure in that project's root.
3. Governing rule for everything in the workspace:

> Recall may suggest. Authority decides. Live state verifies.

Note the initial state: `execution_hold: true` in `PROJECT_STATUS.md`.
Consequential actions (merge, push, release) need your explicit approval.

## Step 1 — Install

Requirements: **IDA Pro 9.x with idalib** · **Python 3.10+** · **Ollama**
(optional — only needed for AI naming).

```powershell
pip install spectrida            # base: pipeline + TUI + scanners (lz4/capstone/numpy included)
pip install "spectrida[gpu]"     # optional: torch, GPU prologue scanning
pip install "spectrida[graph]"   # optional: Neo4j + MCP server
pip install "spectrida[atlas]"   # optional, heavy: phantomrt dynamic layer
```

Sanity checks:

```powershell
spectrida formats      # expect: ELF, NSO, PE, generic
spectrida --demo       # full TUI on canned data — no IDA or Ollama needed
```

## Step 2 — First-run setup

```powershell
spectrida onboard
```

Auto-detects IDA, writes `%USERPROFILE%\.spectrida\config.toml`, offers the
8.7 GB naming model. If it misses IDA, edit the config:

```toml
[ida]
idalib = "C:/Program Files/IDA Professional 9.1"
output_dir = "~/.spectrida/output"

[ollama]
base_url = "http://localhost:11434"
model = "spectrida-re"

[pipeline]
workers = 8          # physical cores; each worker is a full idalib process
```

AI naming (optional):

```powershell
winget install Ollama.Ollama
ollama pull hf.co/gdfhhjk/spectrida-re-gguf:latest
ollama cp hf.co/gdfhhjk/spectrida-re-gguf:latest spectrida-re
spectrida serve
```

## Step 3 — Analyze a PE

```powershell
spectrida analyze C:\path\to\target.dll --workers 8
```

Under the hood:

1. **Format detection** — PE handler parses the section table, image base,
   and (this fork) the COFF machine field for the arch hint.
2. **Density scan** — prologue scan (GPU/numpy) cuts N shards with equal
   *function counts*, not equal bytes.
3. **Parallel phase** — N idalib subprocesses, private zeroed-out copies,
   Capstone recursive descent per shard (CS_MODE_32 for 32-bit PEs,
   CS_MODE_64 for 64-bit) → per-shard JSON.
4. **Merge (single-threaded by design)** — one IDA instance applies all
   boundaries, runs `auto_wait()` for cross-shard xrefs, saves
   `~/.spectrida/output\<name>_parallel.i64`. Cores napping during this
   phase is physics, not a bug.

Reference point (upstream hardware, 5800X3D): a 189-function PE in ~6 s
with 4 workers. Yours will vary — measure, don't trust.

## Step 4 — Work the TUI

| Key | Action |
|-----|--------|
| `N` | AI-name selected function (streams live) |
| `E` | AI-explain selected function (structured: purpose/behavior/IO/confidence) |
| `B` | Batch-name every `sub_*` |
| `R` | Rename manually (persists to the `.i64`) |
| `D` | Toggle Hex-Rays pseudocode |
| `C` | Callers/callees chain |
| `O` | AI overview of the binary |
| `/` | Fuzzy search · `?` help · `Q` quit |

## Step 5 — Or script it

```python
import asyncio
from spectrida.api import open_i64

async def main():
    async with open_i64(r"%USERPROFILE%\.spectrida\output\target_parallel.i64") as db:
        funcs = await db.list_functions()
        print(f"{len(funcs)} functions")

        # free + deterministic first: demangle before spending tokens
        mangled = [f["name"] for f in funcs if f["name"].startswith("?")]
        print(await db.demangle(mangled))

        await db.batch_name(limit=100, rename=True)
        await db.export("target_names.idc", fmt="idc", named_only=True)

asyncio.run(main())
```

Apply names back in any IDA install: **File → Script file → target_names.idc**.

## Practical advice

- **Demangle before AI naming.** It's free and deterministic; only genuinely
  stripped leftovers are worth model tokens.
- **Naming accuracy:** the model reads *disassembly + call-chain context*
  (not pseudocode). Generic helpers land well; domain-specific logic is a
  coin flip. Rename what's wrong — it persists.
- **32-bit x86 PEs** are supported in this fork (CS_MODE_32). Upstream
  silently misdecoded them; if you ever compare against upstream results,
  that's why they differ.
- **phantomrt** (emulate/fuzz/live-trace) is alpha. Treat `crash` verdicts
  as leads and `needs_state` as an honest shrug, not a bug.

## Agent loop (bounded autonomous naming)

Two MCP tools run a budget-capped naming pass over the binary:

| Tool | Purpose |
|------|---------|
| `agent_run` | Start a bounded pass: explain unnamed functions, auto-apply high-confidence names, queue the rest. Returns `run_id` immediately. |
| `agent_status` | Poll a run; when done, returns the full draft report (coverage delta, budget spend, human queue). |

Guardrails: hard caps (default 200 LLM calls / 100 renames / 30 min),
convergence stop (coverage delta < 2% over 3 iterations), medium-confidence
names only apply when the decompilation verifier confirms them (today it
is a stub, so they queue for you). Every run report and naming-pattern
record the agent writes to the OKF workspace is a **draft** until you
approve it. Set `SPECTRIDA_OKF_ROOT` (or `[workspace] okf_root` in
`~/.spectrida/config.toml`) to enable workspace records.
