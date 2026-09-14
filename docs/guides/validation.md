# Validation and evidence

Run from the repository root with `requirements-validation.txt` installed:

```bash
python skills/real2sim-prompt/scripts/check_review_gate.py /path/to/review_gate.json --stage review
python skills/real2sim-prompt/scripts/check_review_gate.py /path/to/review_gate.json --stage physics
python skills/real2sim-prompt/scripts/check_review_gate.py /path/to/review_gate.json --stage deliver
python skills/real2sim-prompt/scripts/check_augmentation_gate.py /path/to/augmentation_gate.json
```

These are validators, not reconstruction/execution commands. They emit JSON and return a nonzero status on rejection. `review` and `physics` check the applicable pre-execution records; `deliver` additionally requires native evidence when task scope requires it.

## What is implemented

- Five-question frame/view coverage, feedback closure and scene identity checks.
- Explicit `task_scope` and `physics_required` consistency.
- Native input, run, trajectory and result associations using hashes and run IDs.
- Finite NPZ state trajectories with strictly increasing timestamps and matching counts.
- Declared task metric comparisons, rather than trusting only a pass string.
- Augmentation parent-child parameter deltas and mechanical/appearance distinctions.
- Support/mounting and display/collision audit evidence binding.
- Required Blender/MuJoCo keyframe images, actual image decoding and provenance receipts.

## What must be produced elsewhere

Scene execution and evaluation programs must compute real metrics and write authentic records. The checks do not independently rerun MuJoCo, derive contact forces from qpos, prove an audit statement, detect all deliberately forged evidence, or recover omitted dependencies. Third-step video decoding remains a separate delivery check; its validator directly decodes keyframe images only.

Keep linear speed (m/s), angular speed (rad/s) and stable duration (s) separate. Select and disclose task-appropriate tolerances; contact penetration must distinguish ordinary solver tolerance from task-obstructing geometry. A hash match cannot repair an inappropriate acceptance criterion.

See [complete record contracts](../../skills/real2sim-prompt/references/native-and-augmentation-gates.md), [visual gates](../../skills/real2sim-prompt/references/execution-gates.md) and [metrics/cache specification](../../skills/real2sim-prompt/references/metrics-diversity-cache.md).

## Regression tests

```bash
python -m unittest discover -s tests -v
```

Fixtures are synthetic and test both valid associations and rejection paths. They are not runnable reconstruction examples or evidence of native task completion. No missing fields should be filled with fabricated success to migrate historical results.
