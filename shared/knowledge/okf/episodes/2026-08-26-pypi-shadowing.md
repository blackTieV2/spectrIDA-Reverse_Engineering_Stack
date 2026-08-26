---
id: ep-2026-08-26-001
title: PyPI upstream shadows the fork during first live acceptance
date: 2026-08-26
status: draft
---

# Episode: `pip install spectrida` installed upstream, not the fork

## What happened

First live-acceptance run: the user followed quickstart Step 1
(`pip install spectrida`) inside the freshly cloned fork. PyPI hosts the
*upstream* package (0.4.0), so the TUI that launched was upstream's —
no marker column, no E key. The missing ✖/▶/? column in the screenshot
was the tell; DemoBackend returns all three canned flags correctly.

## Root cause

Doc bug: Step 1 assumed `pip install spectrida` resolves to the local
project. It does not — the name is taken on PyPI by upstream.

## Fix

Quickstart Step 1 rewritten: uninstall any PyPI copy, `pip install -e .`
from the clone, and a visual verification rule ("no markers = you
installed from PyPI"). Commit 56cef0b.

## Lesson

**Name shadowing is an acceptance-gate hazard for any fork of a
published package.** The verification step must check for a feature the
upstream lacks — version strings alone can coincide.
