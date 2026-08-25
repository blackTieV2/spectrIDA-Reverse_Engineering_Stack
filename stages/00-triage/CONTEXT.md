# Stage 00-triage — contract

**Purpose:** Understand the request, classify risk, select mode, identify the target, decide whether recon is required.

**Hard rule:** No implementation. Output: triage note in `output/`.

**Read before acting:** root `AGENTS.md` → `PROJECT_STATUS.md` → this file.

**Tools:** see `_config/tool-profiles.yaml` (`triage` profile).

**Output:** `stages/00-triage/output/` only.

**Stop conditions:** scope exceeded; live state contradicts the task packet;
execution hold becomes active; approval missing for a consequential step.
