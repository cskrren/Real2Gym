![Real2Gym: real videos, Blender reconstruction, MuJoCo execution and scene augmentation](assets/real2gym-overview.png)

**From human or robot videos to reconstructed scenes, executable actions, and validated simulation variants.**

*Conceptual illustration. [Image provenance](assets/README.md).*

[Get started](#get-started) · [Pipeline](docs/guides/pipeline.md) · [Examples](examples/README.md) · [中文](docs/README.zh-CN.md) · [Citation](#citation)

Real2Gym uses **GPT6 Astra** to coordinate scene reconstruction, action adaptation and feedback-driven refinement across **Blender and MuJoCo**.

## Highlights

- **Human & robot demonstrations** — single-view or multi-view videos, with motion retargeting to selected robot hardware.
- **Aligned scenes and actions** — reconstruct objects, robots and cameras; review interaction keyframes and correct mismatches.
- **Physics-validated execution** — run native MuJoCo interactions and bind task results to the model and trajectory used.
- **Validated scene augmentation** — vary geometry, target placement, table height, backgrounds and appearance; adapt actions and revalidate each variant.

## Three steps

| Step | What happens | Deliverables |
| --- | --- | --- |
| **1. Reconstruct** | Initialize geometry, build complete objects and align the scene to video | Blender scene, robot and cameras |
| **2. Execute** | Recover or retarget motion, refine contacts and verify the complete task | MuJoCo model, native trajectory, **Real / Blender / MuJoCo RGB** comparisons |
| **3. Augment** | Combine mechanical changes with appearance variations and test execution | Validated scene family with parameter changes and run evidence |

[Full pipeline](docs/guides/pipeline.md) · [Hardware selection](skills/real2sim-prompt/references/target-robot-selection.md) · [Evidence validation](docs/guides/validation.md)

## Get started

```bash
git clone https://github.com/cskrren/Real2Gym.git
cd Real2Gym
conda create -n real2gym python=3.11 -y
conda activate real2gym
python -m pip install -r requirements-validation.txt
```

The environment above installs the evidence-validator dependencies.

Install the complete [`skills/real2sim-prompt`](skills/real2sim-prompt/SKILL.md) directory in your agent's skill location. For Codex, use `~/.codex/skills/real2sim-prompt`; the invocation remains **`$real2sim-prompt`**.

Prepare Blender, MuJoCo, geometry models and robot assets using the [setup guide](docs/guides/getting-started.md), then provide your video and target hardware:

```text
Use $real2sim-prompt to run Real2Gym steps 1 and 2.
Input: /absolute/path/demo.mp4
Source actor: human
Target robot: dual FR3 + Franka Hand
Output: /absolute/path/runs/demo
Deliver the reconstructed scene, native execution evidence,
and frame-matched Real / Blender / MuJoCo RGB comparisons.
```

For step 3, start from an accepted scene and specify augmentation and retry budgets. [Robot, human and augmentation examples →](examples/README.md)

**Current release:** v5.2 workflow skill and evidence validators. Scene construction and control remain agent-driven with task-specific code; a one-command solver, Gymnasium API and training engine are not yet included. [Validation scope](docs/guides/validation.md)

## Citation

Please cite Real2Gym and record the exact tag or commit used:

```bibtex
@software{real2gym,
  author = {{Real2Gym Contributors}},
  title = {{Real2Gym: Real-World Videos to Executable Robot Simulations}},
  year = {2026},
  url = {https://github.com/cskrren/Real2Gym}
}
```

[CITATION.cff](CITATION.cff) · [Contributing](CONTRIBUTING.md) · [Repository guide](docs/guides/repository.md)

*Repository license and formal author list are pending confirmation. [Licensing and attribution](docs/guides/licensing.md).*
