# Hardware previews

These are existing local MuJoCo model renders, copied without modification for the README hardware selector. The image names, hashes and original gallery metadata are retained in [manifest.json](manifest.json). No new physical task was executed for this gallery.

| Preview | Asset basis |
| --- | --- |
| Dual FR3 + Franka Hand | Menagerie FR3 with standard Franka/Panda Hand meshes and structure; a visualization assembly |
| Dual FR3 + Wuji Hand | FR3 with Wuji official left/right hand descriptions; simulated adapter |
| Dual FR3 + Sharpa Wave | FR3 with Menagerie Sharpa Wave left/right hand models; simulated adapter |
| ALOHA 2 | Existing ALOHA 2 model with its grippers and wrist-camera structure |
| G1 + Dex3-1 | Unitree `xr_teleoperate` G1 29DoF / hand14 assembly |
| H1-2 + stock five-finger hands | Unitree `xr_teleoperate/assets/h1_2/h1_2.xml`; not labelled Dex5-1 |

Model sources: [MuJoCo Menagerie](https://github.com/google-deepmind/mujoco_menagerie), [Wuji hand descriptions](https://github.com/wuji-technology/wuji-hand-description), [Unitree xr_teleoperate](https://github.com/unitreerobotics/xr_teleoperate). The source models retain their upstream terms. The images show configurations, not proof of official adapter compatibility, free-standing balance, or task success. Adapter geometry and exact hardware versions must be checked for the selected task. See the [hardware selection specification](../../skills/real2sim-prompt/references/target-robot-selection.md).
