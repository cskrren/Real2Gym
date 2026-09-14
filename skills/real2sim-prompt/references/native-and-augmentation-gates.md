# 原生关联与第三步验收（v5.2）

本版实现文件/版本关联与结构检查，不建立跨任务动作接口。依赖 Python、NumPy、Pillow；同一技能目录下的 `scripts/evidence_checks.py` 是两个验收器共享模块，安装时复制完整技能目录。

## 1. 按任务范围判定原生证据要求

现有 `review_gate.json` 增加：

- `task_scope`: `static_scene` / `motion_preview` / `native_execution` / `augmentation`。
- `scope_basis`: 对应用户要求的简短记录，不能为了通过改写为预览。
- `physics_required`: 必须显式为布尔值，前两种范围为false，后两种为true；缺失/矛盾均拒绝。
- `native_evidence`: 必须物理执行的交付范围需要下述证据块。

`review`、`physics` 检查任务范围但不要求尚未执行的原生结果；`deliver` 对需要物理执行的范围检查完整关联。第一、二步原有五问覆盖与视觉门槛仍保留。

```
python scripts/check_review_gate.py /path/review_gate.json --stage deliver
python scripts/check_augmentation_gate.py /path/augmentation_gate.json
```

第二个命令是第三步专用检查，不调用真实对齐五问、不要求配对Real RGB。两者失败均非零退出；缺旧字段时报告证据不足，不静默沿用旧pass。

## 2. 文件引用与原生记录

所有文件引用统一为 `{"path":"相对验收JSON的路径","sha256":"实际文件SHA256"}`。嵌套记录中的引用也相对顶层验收JSON；不是相对嵌套JSON。内容变更必须更新生产/验证记录，不为让哈希匹配补造证据。

`native_evidence` 包含：

| 字段 | 内容 |
| --- | --- |
| `inputs` | model、control、initial_state、sim_config、criteria、scenario、producer各一份文件引用；assets为引用列表，明确空列表也必须记录 |
| `run` | 实际执行时输出的运行记录引用 |
| `trajectory` | NPZ引用，包含有限二维 `qpos[T,nq]` 和严格递增的 `time_s[T]`，至少两个状态 |
| `result` | 基于该轨迹和判据生成的评估结果引用 |

第一、二步交付还要求inputs.review_scene引用当前review_gate中的scene_path/scene_sha256，并纳入inputs摘要，防止新Blender工程沿用旧物理证据。第三步以current_config绑定场景参数。

model是实际加载模型；control应包含所有影响执行的控制参数/控制输入及相应代码来源，producer绑定执行程序版本。sim_config记录步长、求解器、随机种子、运行时版本等；assets列出模型实际引用的网格等依赖。scenario记录当前候选参数。生产端负责完整枚举依赖；校验器验证所列文件，不声称自动解析任意URDF/MJCF的完整依赖闭包。

用 `Evidence(root).inputs(inputs)` 计算 `inputs_sha256`：对上述实际内容哈希做规范化摘要，忽略机器路径差异。运行前核对并保存inputs，执行结束后记录轨迹哈希；生产端需确保期间输入未变。`run`与`result`必须同为当前 `candidate_id`、同一个非空 `run_id`、同一 `inputs_sha256` 和 `trajectory_sha256`。run还要求 `mode="native"`、`completed=true`、`frame_count=T`。

criteria文件含 `rules`，例如：

```json
{"rules":{"task_success":{"op":"eq","value":true},"linear_speed_m_s":{"op":"le","value":0.01},"stable_duration_s":{"op":"ge","value":0.5}}}
```

仅是格式示例，数值不是通用默认；必须按本轮任务补齐角速度、持续窗口、几何/接触等判据。规则支持数值le/ge/eq或布尔eq，必须显式要求task_success=true。result含 `status="pass"`、`criteria_sha256` 和按规则名称提供的 `metrics`。校验器拒绝缺项、非有限值、超限和版本不一致，不只读取pass字符串。

**能力边界**：指标仍由场景对应的评估程序计算；该检查器不重新模拟、不从qpos独立重建力、不鉴定伪造来源或人为填错的指标。生产程序与评估依据要可追溯，必要时独立复跑；文件关联通过不能替代合理的任务判据、真实图像审核或物理真实性判断。

## 3. 第三步独立记录

`augmentation_gate.json`必须有task_scope=augmentation、physics_required=true、scope_basis和candidate_id，并包含：

- `parent_config / current_config`: 文件引用，内容含candidate_id及非空parameters字典。当前配置ID对应本次候选；父ID不同。参数结构一致，新增字段需先明确迁移，不自动忽略。
- `kind`: mechanical / appearance。原基线走原生验收，不伪装成空修改的增强候选。
- `declared_changes`: 以 `/mechanical/cup_x` 等叶路径为键，值为 `{"before":旧值,"after":新值}`；数组作为整体叶值，键不含 `/`。程序比较父子真实参数差异，拒绝未声明或声明不符。appearance仅允许 `/appearance/` 和 `/environment/` 下的变化；机械/控制适配改变需新建mechanical候选。
- `parent_native / native_evidence`: 同一原生证据格式，分别绑定父/子config为inputs.scenario，二者都通过。不得引用另一个父场景的裸通过标记。
- `display_inputs`: scene、render_config、producer文件引用及assets列表；用 `Evidence(root).display(...)` 得到显示版本摘要。
- `scene_audit`: 文件引用，内容必须绑定candidate_id、子场景inputs_sha256及display_inputs_sha256；checks包含support、mounting、display_collision_alignment，每项需status=pass、observation及实际evidence文件引用。显示/碰撞无需逐顶点相等，但实际审核需覆盖空腔、接触面、尺寸、安装和支撑。
- `required_media`: 明确要求的view/frame/renderer列表；每个帧视角需要blender和mujoco两端，不可通过删掉一端补齐覆盖。
- `media`: 对应每个要求项，含view/frame/renderer、file图像引用、camera配置引用、validation记录引用。重复、缺失或额外项拒绝。Pillow实际读取并验证图片结构。

每张图的validation记录绑定candidate_id、trajectory_sha256、display_inputs_sha256、media_sha256、camera_sha256、view、frame、renderer及dimensions=[宽,高]；含decoded=true、frame_identity_verified=true与validator程序文件引用。帧映射与两种相机约定应包含在camera文件中。验证程序实际检查后才写这些字段，不能自动填充。当前第三步脚本检查关键帧图像及这些身份记录；视频仍按既有完整解码/时间/帧身份规范另行检查，不声称该脚本已直接解码视频。

支撑、安装、显示/碰撞关系和渲染帧来源的语义依赖场景审计/导出程序；本脚本检查其证据存在、身份、覆盖及明确结论，不是通用几何求解器。它不以对真实原背景的相似度作为增强通过条件。

## 4. 接入和回归

先让场景执行/评估/渲染程序在实际生产时生成记录，再调用验收器；仅更改JSON状态不构成接入。旧结果保留原判据和旧证据状态，缺原始运行绑定时标记未迁移，不能事后凭目录猜测run来源。

仓库 `tests/test_evidence_gates.py` 使用隔离的合成数据检查正常关联和拒绝路径。测试通过只证明验证逻辑行为，不证明合成轨迹执行了真实任务，也不重新认证历史12个场景。执行：`python -m unittest discover -s tests -v`。
