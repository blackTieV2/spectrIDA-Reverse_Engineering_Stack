# Stage 05-qa — contract

**Purpose:** Validate the deliverable against acceptance criteria.

**Hard rule:** QA is not a second build phase — remediation only if explicitly permitted.

**Read before acting:** root `AGENTS.md` → `PROJECT_STATUS.md` → this file.

**Tools:** see `_config/tool-profiles.yaml` (`qa` profile).

**Output:** `stages/05-qa/output/` only.

**Stop conditions:** scope exceeded; live state contradicts the task packet;
execution hold becomes active; approval missing for a consequential step.
