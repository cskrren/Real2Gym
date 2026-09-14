# Repository organization

- Root README and Chinese overview explain Real2Gym to new users.
- `docs/guides/` holds setup, pipeline, evidence and licensing information.
- `examples/requests/` contains human-readable invocation templates.
- `assets/` holds illustrative framework artwork and its prompt/provenance; illustrations are not experiment results.
- `skills/real2sim-prompt/` remains an independently copyable skill. Its name, internal paths and v5.2 execution contracts are retained.
- `tests/` verifies evidence checks using synthetic data. CI runs those tests; it does not launch scene reconstruction.
- `docs/history/` archives earlier release narratives and obsolete illustrations. Their thresholds and iteration rules must not override current instructions.
- `Real2Sim Prompt.md` is the legacy readable mirror, not a separate implementation.

The GitHub repository URL remains `cskrren/Real2Gym`. Real2Gym is the public framework name. The GitHub repository has been renamed to Real2Gym; the local checkout directory may retain its previous name. No new release tag is implied by this layout change.

Place local runs outside the tracked source tree or in ignored `runs/`/`outputs/`. Exclude credentials, private footage, bulky meshes, model weights and generated video. Distributable assets need source and license records. A future packaged CLI or Gymnasium integration should be added only when implemented and tested.
