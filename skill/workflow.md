# 通用故事板技能工作流

本文件定义此 skill 的唯一主流程。

这不是旧版的多轮斜杠命令系统，而是“单次表单直入，内部阶段化处理，必要时最少澄清”的工作流。

## 主流程

```text
表单输入
  ->
输入校验
  ->
素材锁定
  ->
导演规划
  ->
渲染器选择
  ->
提示词生成
  ->
质检
  ->
仅返回方案 / 执行生图
```

## 阶段 1：输入校验

目标：

- 确认是否具备最小设计条件
- 能推断的就推断，不能推断的才补问

必须确认：

- 用户要拍什么（核心故事，含主体与动作）
- 输出形态（带文字导演故事板 / 无文字分镜宫格图）
- 混合模式下是否提供了参考素材

可推断、不要求用户单独填写：

- 主动作：默认与核心故事一体
- 场景描述：优先场景参考图，否则导演推断
- 表演重点：优先角色/产品等参考图 + 故事推断

如果缺少关键输入：

- 使用 `assets/output_contracts/compact_user_request_form.md`
- 每次最多补问 1 到 2 项

## 阶段 2：素材锁定与字段推断

目标：

- 为每个素材分配唯一职责，产出 `asset_lock_map`
- 在素材锁定完成后，补全 `main_action`、`scene_description`、`performance_focus`
- 推断规则见 `scripts/infer_story_fields.py` 与 `references/02_input_requirements.md`

最低要求：

- 明确哪些素材锁定身份
- 明确哪些素材只锁定服装、场景、风格、光照、运动
- 明确每个素材禁止继承什么

输出示意：

```text
角色图 A：锁定脸部、体型、发型
服装图 B：只锁定服装，不继承模特身份
风格图 C：只锁定色彩与质感，不继承场景和人物
```

## 阶段 3：导演规划

目标：

- 产出 `preproduction_board_plan`

必须决定：

- `concept_block`
- `tone_and_mood`
- `visual_direction`
- `character_bible`
- `set_and_environment`
- `blocking_plan`
- `shot_list`
- `camera_language_summary`
- `scene_rhythm_summary`
- `lighting_and_sound`
- `risk_controls`

如果还没形成这些字段，不能直接写最终提示词。

## 阶段 4：渲染器选择

规则：

- 人工审核、汇报、提案：默认 `cinematic_preproduction_board`
- 图像转视频、模型参考：使用 `clean_reference_board`

渲染器只负责呈现，不改导演规划本身。

## 阶段 5：提示词生成

目标：

- 将 `preproduction_board_plan` 转成最终可执行提示词

要求：

- 全中文
- 具体、可视化、可执行
- 明确素材继承和禁止继承
- 不堆抽象形容词

## 阶段 6：质检

生成前必须确认：

- 用户目标是否被正确翻译成画面
- 素材角色有没有串位
- 每格是否有独立功能
- 是否存在重复漂亮图
- 是否已经选对渲染器

## 阶段 7：结果交付

至少返回：

- `storyboard_request`
- `asset_lock_map`
- `preproduction_board_plan`
- `master_prompt_markdown`
- `generated_image_url`
- `image_error`

## 明确废弃

以下旧设计不再作为主流程：

- `/start -> /assets -> /prompt -> /storyboard`
- 先写英文提示词再转换输出
- 默认轻量分镜板即唯一输出形态
- 在没有执行器时声称自动生图
- 把提示词和图片做成互斥输出
