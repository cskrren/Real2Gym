# 逐轮反馈与阶段门槛（v5.2）

执行建模、修改、复现任务时读取；历史结果比较不触发新一轮建模。

## 当前候选记录

沿用现有目录；每个候选持有一个 `review_gate.json`，字段如下：

- `candidate_id / iteration / scene_path / scene_sha256`：本次磁盘工程身份。基线 iteration=0，后续持续累计修正，不设上限。
- `views`：输入中的所有有效相机 ID。
- `required_frames`：需要完整五问的帧集合，默认只含真实事件 representative 去重集，不用仓库参考帧代替。另记 event_keyframes、context_frames、additional_required_frames；若明确要求后两类完整五问才并入 required_frames，报告仍分开统计。邻域只记在 neighborhood_checks 和 issue.checked_window 中，不自动加入 required_frames。
- `scene_audit`：`status / evidence`，在五问前完成连接、尺度、空腔、初态和全序列低成本几何/跳变审计。显示与碰撞差异、盲区明确记录。
- `records`：每个必需 frame × view 一条，含 `frame / view / image_path / image_sha256 / reviewed / questions`。
- `questions`：`largest_difference / camera_alignment / relative_object_alignment / penetration_and_contact / reconstruction_fidelity`。每问有 `status / observation / blocking`；观察问题①可用 observed，其余 pass / pass_with_notes / fail / review / not_evaluated。未看过的图不标 reviewed=true。
- `issues`：`id / question / frames / views / observation / expected / proposed_parameters / status / blocking / evidence`。状态 open / unresolved / regressed / resolved / accepted_by_user。关闭项需关联当前 records 的键 `frame:view`、前后窗口 `checked_window` 和一句 `resolution`。用户接受需保存原话与范围。
- `changed_parameters / addressed_issue_ids / selection_reason`：每次修正至少明确一个原问题；记录前后指标以及未改善项。记录可由程序生成，但视觉结论必须来自实际检查。
- `physics`：进入第二步后记录 mode、证据与 status；无法通过视觉门槛时保留 not_started_alignment_gate。

路径相对于该 JSON 所在目录；工程与图像使用 SHA-256。截图拼板可由多个 frame:view 共用同一图，但必须逐项检查。任何设置或轨迹改变使对应图像/评测失效时，先更新工程哈希再补图和复核。静态未变项可共享证据；不能继承其他视角或未观察帧的结论。

## 调用与返回

```
python scripts/check_review_gate.py /absolute/candidate/review_gate.json --stage review
python scripts/check_review_gate.py /absolute/candidate/review_gate.json --stage physics
python scripts/check_review_gate.py /absolute/candidate/review_gate.json --stage deliver
```

review 检查记录、文件哈希、全部帧视角覆盖及问题关联；允许存在失败结论，以便记录诚实的失败候选。physics 额外要求相机、相对位置、几何与所有 blocking 项已关闭；deliver 同样要求这些门槛，按显式task_scope判定原生要求，并校验模型/控制/初态/轨迹/结果关联及实际指标，不接受仅physics.status=pass。拒绝返回非零退出码和明确问题列表。失败报告可正常交付，但必须显式标 failed_delivery 并保留拒绝结果，不能伪造 gate pass。

没有脚本可以判断模型是否真的看了图或是否作出合理视觉判断。禁止为获得退出码 0 自动写 pass、把 blocking 清零、删 required_frames、缩小 views 或在无用户认可时填 accepted_by_user。

## 每轮真正执行的顺序

1. 在当前候选查看全部新图/失效图，生成逐帧五问；记录问题优先级。
2. 运行 review 门槛。缺项先补齐；问题按源时间/相机→相对位置→几何/接触→外观处理。
3. 选明确问题形成下一候选，记录参数及预期；开始验证后占用一次修正。环境错误和同候选复验另记，不重置次数。
4. 新图中复核关键帧；对已触发问题检查前后邻域的受影响项至稳定，记录 neighborhood_checks，补新增模拟事件/异常，逐问题关闭或保留；再运行 review 和 physics 门槛。
5. physics 门槛失败时继续第一步修正；通过后才能进行完整原生执行。失败物理状态回传 Blender 后重新复核受到影响的相机/相对位置、接触和动作结果。
6. 有可执行方案时继续修正；实际阻塞或用户停止时保留最佳候选与失败证据。不得临时改阈值或将诊断替换为成功。

## URDF 与等效描述

输入记录必须区分：原始 vendor URDF/Xacro、从它生成的 URDF、通用 MJCF 等效描述、视觉估计。记录实际加载文件及版本。只存在 MJCF 时不得宣称加载了 URDF；传感器、夹爪与底座安装变换若不在描述里，仍是待标定量。通用硬件描述与网格可在 fresh_start 使用，旧场景的底座、手眼和拟合轨迹不可复用。

## MoGe-3 / Pi3X 实例初始化

用户采用语义实例初始化时，initial_alignment.mode="instance_first"，并关联实例清单及哈希；字段和顺序见[首帧初始化](geometry-initialization.md)。review 允许诚实记录 pending 的 mask/mesh，检查现有证据哈希和视角覆盖。进入 physics/deliver 时还要求清单审核、可见区域分配、实例身份/几何、可见 mask、实际 mesh，以及机器人描述/结构/对齐证据齐全。纯数据校验不判断语义是否合理，也不替代实际输入视角与所用多帧的图像复核。

## 静态阶段的用户接受与下一步边界

用户明确确认第一步完成时，另存 `phase_acceptance.json`：stage=static_initialization、status=accepted_by_user、候选与 scene_sha256、配置/源索引依据、原话、接受范围、已知偏差、进入动作后需重开的条件。不能把“第一步完成”解释为已有动作或原生物理成功。

用户接受的非关键背景外观/局部身份歧义作为范围内非阻塞偏差，结束静态返工。严格证据检查曾因缺 mask/unknown 拒绝时，保留原始结果；记录 `strict_evidence_result` 与 `user_accepted_scope`，不能伪造 mask、把 unknown 改成测量 pass，或将程序退出码改成成功。现有校验器只表达严格证据门槛，不完整表达用户接受范围；两种状态并列报告。用户接受后可以准备动作、局部运动与接触诊断；任务相关相机、交互物体和每个新事件的五问/原生物理要求仍需独立满足。

后续运动进入该背景的接触范围、显露重要遮挡区域，或改变共享相机/尺度时，只重开受影响项。相机/交互目标的阻塞错误、缺失物理结果不能被背景接受范围豁免。

## v5.2 原生证据与第三步

所有范围显式记录task_scope、physics_required和scope_basis；格式、依赖及迁移说明见[原生与增强验收](native-and-augmentation-gates.md)。第三步使用独立check_augmentation_gate.py，不套用真实RGB对齐覆盖。
