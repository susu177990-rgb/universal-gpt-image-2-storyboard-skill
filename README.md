<p align="right">
  <strong>语言 / Language:</strong>
  <a href="#中文">中文</a> ·
  <a href="#english">English</a>
</p>

<a id="中文"></a>

# universal-storyboard-skill

这是一个偏导演工作流的故事板 skill。它不是只给你几张灵感图，而是把表单输入、故事信息和参考素材整理成一张完整的预制作导演板，先输出可审阅的 Markdown 提示词，再在你确认后进入生图。

## 它适合做什么

- 把零散的故事需求整理成完整故事板
- 给导演、提案、客户沟通准备预制作视觉板
- 在生成图片前先把故事结构、镜头区、角色区、场景区理顺
- 让素材锁定和导演推断一起工作，而不是互相打架

## 你会拿到什么

- `cinematic_preproduction_board`
- `clean_reference_board`
- `master_prompt_markdown`
- `awaiting_confirmation` 的确认式生图流程

## 功能亮点

- 先出可审阅提示词，再确认生图
- 强素材锁定，适合多参考输入
- 导演板结构完整，不是零散拼图
- 适合提案、沟通和后续执行
- 把导演推断显式落到结构化字段里

## Installation / 安装

如果你作为本地 skill 使用，可放进 Codex skills 目录：

```bash
$ cp -R "universal-storyboard-skill" ~/.codex/skills/universal-storyboard-skill
```

## Usage / 用法

这个 skill 的使用方式：

它默认分两步走：

1. 先根据表单和素材生成完整导演板提示词
2. 用户确认后，再正式出图

这很适合对质量有要求、又不想一上来就浪费生成次数的场景。

```text
$ 请根据这些故事信息和参考素材先生成完整导演板提示词，确认后再出图。
```

## 最重要的定位

它更像“导演的工作板生成器”，而不是“普通几格分镜图生成器”。

## 输入重点

输入契约在 [interface/input.json](./interface/input.json)。

最重要的字段：

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

## 输出重点

输出契约在 [interface/output.json](./interface/output.json)。

核心字段：

- `master_prompt_markdown`
- `image_generation_status`
- `confirmation_action`
- `generated_image_url`

默认第一轮只填 `Prompt 输出`，并把 `image_generation_status` 标记为 `awaiting_confirmation`。确认之后才继续出图。

## 内部主链

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
等待确认生图
  ->
图片结果 / 结构化错误
```

## 它最适合的场景

- 需要一张完整导演板，而不是几个随意参考图
- 先做创意和结构确认，再生图
- 角色、服装、风格、场景都有参考素材，需要锁得比较稳
- 提案、客户汇报、导演沟通需要“像工作板”的结果

## 核心中间结果

- `storyboard_request`
- `asset_lock_map`
- `preproduction_board_plan`

这三个结果决定最后导演板长什么样，也决定为什么它比“直接拼 prompt 出图”更稳。

## 仓库里的关键文件

- [skill/SKILL.md](./skill/SKILL.md)
- [skill/workflow.md](./skill/workflow.md)
- [skill/scripts/run_storyboard_pipeline.py](./skill/scripts/run_storyboard_pipeline.py)
- [skill/scripts/classify_asset_roles.py](./skill/scripts/classify_asset_roles.py)
- [skill/scripts/infer_story_fields.py](./skill/scripts/infer_story_fields.py)
- [skill/scripts/plan_preproduction_board.py](./skill/scripts/plan_preproduction_board.py)
- [skill/scripts/render_storyboard_output.py](./skill/scripts/render_storyboard_output.py)
- [skill/scripts/smoke_test_pipeline.py](./skill/scripts/smoke_test_pipeline.py)

## 设计上的硬规则

- 核心故事是唯一必填叙事字段
- 关系、表演、tone、场景可以强推断，但必须回写到推断字段
- 风格素材锁质感，不锁内容
- 服装素材锁服装，不继承模特身份
- 输出结果必须像预制作导演板，而不是普通分镜格子

## 仓库结构

```text
.
├── README.md
├── interface/
│   ├── input.json
│   └── output.json
├── optimized_system_prompt.md
└── skill/
    ├── SKILL.md
    ├── assets/
    ├── examples/
    ├── references/
    ├── scripts/
    └── workflow.md
```

---

<a id="english"></a>

## English

`universal-storyboard-skill` builds a full pre-production storyboard board instead of a loose inspiration sheet. It first produces reviewable markdown prompts, then waits for confirmation before image generation.

## Best for

- director boards
- client proposals
- structured visual planning
- asset-locked storyboard generation

## Main outputs

- `cinematic_preproduction_board`
- `clean_reference_board`
- `master_prompt_markdown`
- confirmation-based image generation flow

## License / 许可

仓库内如有单独许可文件，以仓库实际文件为准；当前 README 不额外重定义许可。
