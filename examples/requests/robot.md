# Robot video → executable simulation

Use $real2sim-prompt to run Real2Gym steps 1 and 2.

- Source actor: robot.
- Source videos: /absolute/path/front.mp4 and /absolute/path/wrist.mp4.
- Hardware: FR3 + Franka Hand; use /absolute/path/robot.urdf and its meshes.
- Calibration and joint-state paths: supply if available; otherwise record them as unavailable.
- Output: /absolute/path/runs/robot-demo.

Reuse trustworthy state and calibration. Initialize the scene from available views, review real interaction keyframes, execute native MuJoCo contacts and regress the final model. Deliver models, native evidence and Real/Blender/MuJoCo RGB for the available views with source-frame mapping. State exact-reproduction limits and any adapted trajectory. Do not start step 3 in this request.
