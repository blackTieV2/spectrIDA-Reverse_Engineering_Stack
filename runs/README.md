# runs/

Runtime (thread) memory: one directory per controlled run, copied from
`_template/`. Runtime state exists so an interrupted agent can resume safely.
It is NOT durable project truth — promote deliberately, never automatically.

`.gitignore`-worthy contents (logs, scratch) stay out of commits; run-state
and task packets may be committed when they carry evidence.
