# universal-storyboard-skill

通用故事板设计与生成技能。它的默认目标不是轻量分镜板，而是**完整预制作导演板**：把结构化表单和参考素材转成可直接用于提案、导演沟通和生图执行的电影级视觉规划板。

## 当前定位

- 全中文
- 单次表单直入
- 强素材锁定
- 强导演推断
- 默认输出完整预制作导演板
- 同时产出 Markdown 提示词与图片结果

## 主链

```text
表单输入
  ->
素材锁定与导演锚点提取
  ->
故事字段强推断
  ->
preproduction_board_plan
  ->
Markdown 提示词
  ->
图片结果 / 结构化错误
```

## 核心中间模型

- `storyboard_request`
  - 用户目标、推断字段、关系、tone、制作语境
- `asset_lock_map`
  - 每个素材的职责、继承规则、导演锚点
- `preproduction_board_plan`
  - 概念区、角色区、场景区、blocking、shot list、灯光与声音、风险控制

## 默认输出

### 1. `cinematic_preproduction_board`

完整预制作导演板，至少包含：

- 概念区
- 角色参考区
- 场景与美术区
- 顶视机位阻挡区
- shot list 主区
- 灯光 / 摄影 / 色彩 / 声音 / mood 区

### 2. `clean_reference_board`

纯图像参考板，用于下游视觉模型：

- 无标题
- 无说明框
- 无参数栏
- 只保留图像叙事

## 输入契约

见 [interface/input.json](/Users/griffith/Desktop/AI/skills/universal-storyboard-skill/interface/input.json)

最重要的输入字段：

- `story_request.story_framework`
- `story_request.scene_description`
- `story_request.performance_focus`
- `story_request.relationship_dynamic`
- `story_request.tone_keywords`
- `story_request.production_context`
- `optional_parameters.shot_count_hint`
- `optional_parameters.board_density`
- `optional_parameters.render_detail_level`
- `optional_parameters.inference_tolerance`

## 输出契约

见 [interface/output.json](/Users/griffith/Desktop/AI/skills/universal-storyboard-skill/interface/output.json)

核心输出字段：

- `master_prompt_markdown`
- `generated_image_url`

内部能力主产物：

- `storyboard_request`
- `asset_lock_map`
- `preproduction_board_plan`

## 关键脚本

- [run_storyboard_pipeline.py](/Users/griffith/Desktop/AI/skills/universal-storyboard-skill/skill/scripts/run_storyboard_pipeline.py)
- [classify_asset_roles.py](/Users/griffith/Desktop/AI/skills/universal-storyboard-skill/skill/scripts/classify_asset_roles.py)
- [infer_story_fields.py](/Users/griffith/Desktop/AI/skills/universal-storyboard-skill/skill/scripts/infer_story_fields.py)
- [plan_preproduction_board.py](/Users/griffith/Desktop/AI/skills/universal-storyboard-skill/skill/scripts/plan_preproduction_board.py)
- [render_storyboard_output.py](/Users/griffith/Desktop/AI/skills/universal-storyboard-skill/skill/scripts/render_storyboard_output.py)
- [smoke_test_pipeline.py](/Users/griffith/Desktop/AI/skills/universal-storyboard-skill/skill/scripts/smoke_test_pipeline.py)

## 设计原则

- 核心故事是唯一必填叙事字段
- 关系、tone、表演、场景允许强推断，但必须回写到 `inferred_fields`
- 风格素材只影响质感，不污染内容物
- 服装素材只锁服装，不继承模特身份
- 输出必须像导演工作板，而不是几格普通分镜图
