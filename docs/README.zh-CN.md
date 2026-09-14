# Real2Gym

**Real-World Videos to Executable Robot Simulations**

![Real2Gym 框架介绍](../assets/real2gym-overview.png)

*AI 生成的概念介绍图：人手或单机械臂示范、对应的 Blender 与 MuJoCo 场景，以及背景替换、桌高和微波炉位置增强；不作为实验结果证据。*

Real2Gym 将真实机器人或人手操作视频重建为 Blender 场景，在 MuJoCo 中恢复并验证交互动作，再生成有物理执行证据的增强环境。GPT6 Astra 负责观察、编写与修改场景/控制代码、调用工具、复核反馈；Blender 和 MuJoCo 分别提供视觉与原生物理证据。

## 三步流程

1. **重建场景**：单视角首帧用 MoGe-3，多视角首帧用 Pi3X；RGB 主导完整物体 mesh，首帧点云辅助几何，最多十个后续稀疏 RGB 时间索引补全表面。导入 URDF/MJCF，完成相机、对象与机器人初态对齐。
2. **执行动作**：发现真实交互事件、恢复或重定向动作、逐关键帧五问、MuJoCo 原生执行与完整回归；回传 Blender 后优化前后景材质、纹理和灯光，交付 Real / Blender / MuJoCo RGB。
3. **生成增强环境**：有限单项探测后随机选择1–3项机械修改，失败则缩幅重试；对原场景及通过的机械场景加入纹理、干扰物、完整背景与适度灯光，形成 `(1+N)×(1+M)` 候选，逐项原生复验。

## 如何使用

克隆仓库，按[上手指南](guides/getting-started.md)安装验证依赖，并将完整 `skills/real2sim-prompt` 目录安装到 agent 的技能目录。Codex 默认路径为 `~/.codex/skills/real2sim-prompt`；调用名称继续使用 `$real2sim-prompt`。

提供视频路径、robot/human 输入类型、目标硬件、可用标定/状态、任务范围及输出路径。参考[请求模板](../examples/README.md)。Blender、MuJoCo、几何模型和机器人资产需另行准备；安装 skill 不等于安装完整运行环境。

本仓库当前发布 **v5.2 的执行规范与验收工具**，不是已经封装的一键视频求解器。场景、动作适配及指标生产仍依赖具体任务代码；统一缓存调度器、Gymnasium API 和策略训练引擎未实现。支持硬件选型不等于所有组合或任务都已成功。

查看[完整流程](guides/pipeline.md)、[验收与边界](guides/validation.md)、[目录结构](guides/repository.md)和[英文首页的引用方式](../README.md#citation)。许可证与正式作者名单仍待确认；历史经验保留在 `docs/history/`，不替代当前规则。
