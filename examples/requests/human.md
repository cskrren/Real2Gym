# Human video → robot interaction

Use $real2sim-prompt to run Real2Gym steps 1 and 2.

- Source actor: human.
- Input: /absolute/path/demo.mp4 (single view).
- Target: dual FR3 + Franka Hand.
- Robot asset path: /absolute/path/robot-assets.
- Output: /absolute/path/runs/human-demo.

Initialize the first frame using MoGe-3. Build meshes primarily from RGB, assisted by first-frame geometry and at most ten later sparse RGB time indices. Retarget object-relative human actions to the selected hardware, review interaction keyframes and validate the complete task in native MuJoCo. Transfer the resulting motion to Blender, refine foreground/background appearance and deliver frame-mapped Real/Blender/MuJoCo RGB and native evidence. Preserve task logic and disclose required action adaptations; do not invent unobserved real views.
