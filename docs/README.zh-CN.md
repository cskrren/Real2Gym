![Real2Gym 框架介绍](../assets/real2gym-overview.png)

**从人手或机器人视频，构建场景、执行动作，再生成有验证证据的仿真变体。**

*概念介绍图。[图片来源](../assets/README.md)。*

Real2Gym 由 **GPT6 Astra** 协调 **Blender 场景重建、MuJoCo 动作执行与反馈迭代**。

## 核心能力

- **人手与机器人输入**：支持单视角、多视角视频，并将动作重定向到选定硬件。
- **场景与动作对齐**：重建物体、机器人和相机，逐交互关键帧复核并修正。
- **原生物理验证**：在 MuJoCo 执行任务，将结果与对应模型、轨迹及证据关联。
- **可执行场景增强**：调整几何、目标位置、桌高、背景和外观，适配动作后逐场景复验。

## 三步流程

| 步骤 | 工作 | 输出 |
| --- | --- | --- |
| **1. 重建** | 几何初始化、完整物体建模、与视频对齐 | Blender 场景、机器人与相机 |
| **2. 执行** | 动作恢复／重定向、接触调整、完整物理回归 | MuJoCo 模型、原生轨迹、**Real / Blender / MuJoCo RGB** 对照 |
| **3. 增强** | 组合机械变化与外观变化，逐项验证 | 带参数差异及运行证据的仿真场景集合 |

[详细流程](guides/pipeline.md) · [硬件选择](../skills/real2sim-prompt/references/target-robot-selection.md) · [验收说明](guides/validation.md)

## 快速使用

克隆 [Real2Gym](https://github.com/cskrren/Real2Gym)，将完整 `skills/real2sim-prompt` 目录安装到 agent 技能目录。Codex 默认位置为 `~/.codex/skills/real2sim-prompt`，调用名称为 **`$real2sim-prompt`**。

使用 Conda 创建 `real2gym` 环境（Python 3.11），命令见[英文快速开始](../README.md#get-started)。按[环境准备指南](guides/getting-started.md)配置 Blender、MuJoCo、几何模型和机器人资产，然后向 agent 提供视频路径、输入类型、目标硬件和输出目录。[示例请求](../examples/README.md)

当前发布 **v5.2 执行 skill 与验收工具**；建模和控制仍由 agent 结合场景代码完成，尚未包含一键求解器、Gymnasium API 或训练引擎。

[引用方式](../README.md#citation) · [目录结构](guides/repository.md) · [贡献说明](../CONTRIBUTING.md)

*仓库许可证和正式作者名单待确认，详见[许可与署名](guides/licensing.md)。*
