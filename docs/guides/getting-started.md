# Getting started

Real2Gym is operated by a tool-using agent. Installing the skill gives the agent the workflow and acceptance rules; it does not install Blender, download weights or generate a controller automatically.

## 1. Prepare the validation environment

From the repository root, create a Conda environment and install `requirements-validation.txt`. Python 3.11 is the CI target. NumPy and Pillow are sufficient for the included validators/tests; they are not the full reconstruction dependencies.

```bash
conda create -n real2gym python=3.11 -y
conda activate real2gym
python -m pip install -r requirements-validation.txt
python -m unittest discover -s tests -v
```

## 2. Install the skill

Copy the entire `skills/real2sim-prompt` directory to the agent's skill location. With Codex the default is `~/.codex/skills/real2sim-prompt`. Check an existing installation before replacement. The references and scripts must remain together. Invoke `$real2sim-prompt`; Real2Gym is the framework brand, not a new skill identifier.

Other tool-using agents can read the entrypoint and referenced files, but their integration is not tested by this repository. GPT6 Astra is the intended orchestration model for this workflow, not an included local dependency or a simulator.

## 3. Prepare external execution tools

| Component | Role | Required when |
| --- | --- | --- |
| Blender | Complete meshes, robot visuals, cameras, motion preview and final RGB | Scene reconstruction and visual delivery |
| MuJoCo Python runtime | Native rigid-body/contact execution and RGB | Steps 2 and 3 with physics |
| MoGe-3 | First-frame geometry initialization | Single-view input |
| Pi3X | Joint camera/point-cloud initialization | Multi-view input |
| Segmentation/vision tools | Visible instance masks and shared semantic IDs | As required by scene ambiguity |
| Robot URDF/MJCF and meshes | Dimensions, joint chain, limits and end-effector mounting | Every target robot |
| Video decoding/encoding tools, e.g. FFmpeg | Frame extraction, media export and verification | Video inputs/outputs |
| Texture/background assets | Appearance reconstruction or augmentation | As selected for the task |

Configure these using their upstream instructions and record actual versions, model checkpoints and asset sources in the run. Model inference may need a separate GPU host; estimate resources before execution. No fixed hardware/runtime claim is made here. Keep credentials outside the repository. See the detailed [geometry](../../skills/real2sim-prompt/references/geometry-initialization.md), [robot](../../skills/real2sim-prompt/references/target-robot-selection.md) and [MuJoCo](../../skills/real2sim-prompt/references/mujoco.md) references.

## 4. Supply a bounded request

Give the agent source paths, robot/human actor type, the target robot, available views/calibration/state, desired steps and a separate output directory. Start with [robot](../../examples/requests/robot.md) or [human](../../examples/requests/human.md) templates. Missing calibration must be recorded as estimated, not measured. Use only source views that exist.

For a new scene, request steps 1 and 2 first. Request [step 3](../../examples/requests/augmentation.md) against an accepted scene and specify N/M and retry budgets. Templates are natural-language instructions, not a machine-readable configuration parser.

## 5. Review the delivery

Expect the accepted Blender/MuJoCo models, source/simulation frame map, interaction keyframes and five-question reviews, native trajectory/result evidence, and requested media. An adapted human-to-robot action should disclose trajectory changes. Inspect the real execution-speed video separately from event-aligned playback.

Run the [validators](validation.md) only on records written by the actual producers. Do not generate missing pass flags to make a legacy run pass. A command returning success validates its documented checks, not the entire physical truth of a scene.
