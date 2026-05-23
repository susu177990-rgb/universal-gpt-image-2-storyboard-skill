# 通用故事板技能目标架构

本文件定义此 skill 的唯一目标架构。后续所有规范、脚本、输入输出和渲染模板都必须服从这个分层，不允许再出现“一份文件同时扮演产品协议、推理内核、渲染模板、执行器说明”的混合写法。

## 设计目标

- 全中文用户体验
- 单次表单输入即可完成主流程
- 内部推理分层清晰，便于扩展
- 默认省 token，只在必要时加载细节
- 对素材有强锁定能力，对分镜有导演式规划能力

## 总体分层

```text
用户表单输入
    ->
输入契约层
    ->
理解与锁定层
    ->
导演规划层
    ->
渲染器层
    ->
执行器层
    ->
结构化输出 / 图片结果
```

## 1. 输入契约层

职责：

- 定义前端允许提交什么
- 定义哪些字段必填，哪些字段可推断
- 定义素材的最小描述粒度

唯一真相源：

- `interface/input.json`
- `references/02_input_requirements.md`

这一层只回答“收到什么”，不回答“怎么想”。

## 2. 理解与锁定层

职责：

- 判断用户的表演重点
- 将素材分类为明确角色
- 提取素材中的身份锚点、场景锚点、道具锚点、风格锚点
- 声明必须继承与禁止继承的元素

核心产物：

- `storyboard_request`
- `asset_lock_map`

唯一真相源：

- `references/03_asset_classification.md`
- `references/04_storyboard_design_logic.md`

这一层只回答“用户到底要什么、素材到底各管什么”，不直接写最终提示词。

## 3. 导演规划层

职责：

- 选择 board type
- 决定 panel 数量
- 给每个 panel 分配明确视觉功能
- 规划时间推进、空间关系、机位与表演重点
- 输出连续性风险与规避策略

核心产物：

- `storyboard_plan`

推荐字段：

- `board_type`
- `output_format`
- `panel_count`
- `camera_strategy`
- `continuity_rules`
- `panels[]`
- `risk_controls[]`

唯一真相源：

- `references/04_storyboard_design_logic.md`
- `references/05_board_types.md`
- `references/06_panel_design_rules.md`
- `references/09_quality_control.md`

这一层是 skill 的智能核心。真正的“导演思维”应主要发生在这里。

## 4. 渲染器层

职责：

- 把 `storyboard_plan` 转成某种具体输出形式

当前允许的渲染器：

- `six_zone_pitch_sheet`
  - 用于提案、汇报、人工审核
  - 输出带头栏、锁定区、运镜区、关键帧区、分镜网格、技术尾栏的完整展示板
- `clean_reference_board`
  - 用于图像转视频或下游视觉模型
  - 输出纯图像分镜，不带说明文字和 UI 装饰

对应规范：

- `references/07_prompt_writing_rules.md`
- `references/08_video_model_adaptation.md`
- `assets/board_blueprints/`

这一层只回答“怎么呈现”，不改动导演规划本身。

## 5. 执行器层

职责：

- 决定是否实际发起生图

当前允许的执行模式：

- `generate_image`
  - 返回结构化分镜方案、Markdown 提示词，并执行生图

注意：

- 如果没有真正可用的图像生成执行器，也必须保留 Markdown 提示词与结构化错误，不得静默缺失
- 执行器是可选层，不是 skill 本体

## 6. 输出层

最少应支持以下结果：

- `storyboard_request`
- `asset_lock_map`
- `storyboard_plan`
- `master_prompt_markdown`
- `generation_mode`
- `generated_image_url`
- `image_error`

唯一真相源：

- `interface/output.json`
- `assets/output_contracts/storyboard_prompt_output.md`

## 单一真相源规则

- `SKILL.md` 只负责入口路由、触发条件、读取顺序、禁止事项
- `workflow.md` 只负责内部执行流程
- `interface/*.json` 只负责输入输出契约
- `references/*.md` 只负责规则与方法
- `assets/board_blueprints/*.md` 只负责具体板式模板
- `scripts/*.py` 只负责可重复、确定性的辅助处理

## 反模式

以下写法以后都视为架构退化：

- 在 `SKILL.md` 里重复完整方法论
- 同时维护 One-Shot 和多轮斜杠命令两套主流程
- 在输入 schema 之外偷偷要求额外关键字段
- 在导演规划层还没稳定前，直接硬写最终大 prompt
- 在没有执行器代码时声称“会自动调用模型”

## 当前重构方向

本次重构以以下顺序推进：

1. 统一主流程为“表单直入，内部阶段化处理，必要时最少澄清”
2. 全部改为中文说明
3. 建立 `storyboard_request -> asset_lock_map -> storyboard_plan -> renderer_output` 的稳定中间层
4. 让 6 区提案板从“唯一真理”降级为“默认渲染器”
5. 让输入表单真正覆盖素材锁定、输出目的、连续性和执行模式
