<p align="right">
  <strong>Language / 语言：</strong>
  <a href="#中文">中文</a> ·
  <a href="#english">English</a>
</p>

<a id="中文"></a>

# universal-storyboard-skill

通用故事板设计与生成技能。把结构化表单和参考素材，转成**素材锁定明确、导演规划清晰、可直接执行**的分镜方案与提示词。

核心思路不是堆砌华丽提示词，而是走一条稳定链路：

```text
表单输入 → 素材锁定 → 导演规划 → 渲染器选择 → 提示词生成 → 质检 → 输出
```

---

## 适用场景

- 基于角色、场景、产品、服装等参考图，规划多格分镜
- 需要区分「给人审核 / 提案」与「给下游模型参考」两种输出形态
- 强调素材职责隔离（例如：服装图只锁服装，不继承模特身份）
- 动作推进、空间建立、转场、情绪表演、产品交互、连续镜头、多机位等常见分镜类型

---

## 核心能力

| 能力 | 说明 |
|------|------|
| 素材锁定 | 为每个素材分配唯一职责，明确必须继承与禁止继承 |
| 导演规划 | 自动选择分镜类型、格数、机位策略、连续性规则 |
| 双渲染器 | `six_zone_pitch_sheet`（6 区提案板）或 `clean_reference_board`（纯净参考板） |
| 结构化输出 | 同时返回中间对象、Markdown 提示词、图片结果或结构化错误 |
| 全中文 | 默认中文用户体验与中文提示词 |

---

## 目录结构

```text
universal-storyboard-skill/
├── README.md                 # 本文件
├── interface/                # 输入输出 JSON Schema
│   ├── input.json
│   └── output.json
└── skill/
    ├── SKILL.md              # Agent 入口：触发条件、读取顺序、禁止事项
    ├── workflow.md           # 内部主流程
    ├── references/           # 规则与方法（架构、输入、素材、分镜、质检等）
    ├── assets/               # 板式蓝图、风格指南、输出契约模板
    ├── examples/             # 7 个请求示例 + 好坏输出对比
    └── scripts/              # 可重复的 Python 辅助流水线
```

**单一真相源原则：**

- `SKILL.md` — 入口路由，不重复完整方法论
- `workflow.md` — 唯一主流程
- `interface/*.json` — 输入输出契约
- `references/*.md` — 推理规则
- `assets/board_blueprints/*.md` — 具体板式模板
- `scripts/*.py` — 确定性辅助处理

---

## 快速开始

### 作为 Agent Skill 使用

安装或引用本 skill 后，Agent 会按 `skill/SKILL.md` 执行：

1. 读取架构与工作流
2. 校验表单输入
3. 完成素材锁定与导演规划
4. 按输出目的选择渲染器
5. 生成 Markdown 提示词并自检

触发关键词示例：故事板、分镜、storyboard、素材锁定、导演规划、6 区提案板、参考板。

### 作为流水线脚本使用

Python 3 环境，无需额外依赖。

```bash
# 从 JSON 文件运行
python skill/scripts/run_storyboard_pipeline.py path/to/input.json

# 从 stdin 运行
cat path/to/input.json | python skill/scripts/run_storyboard_pipeline.py

# 运行冒烟测试
python skill/scripts/smoke_test_pipeline.py
```

输出为 JSON，包含 `storyboard_request`、`asset_lock_map`、`storyboard_plan`、`master_prompt_markdown` 等字段。

---

## 输入说明

输入契约见 [`interface/input.json`](interface/input.json)，中文说明见 [`skill/references/02_input_requirements.md`](skill/references/02_input_requirements.md)。

### 最小必填

| 字段 | 说明 |
|------|------|
| `project_info.input_mode` | `asset_driven` / `text_only` / `mixed` |
| `project_info.output_purpose` | `review_or_pitch`（给人看）或 `model_reference`（给模型） |
| `project_info.generation_mode` | 当前固定为 `generate_image` |
| `story_request.story_framework` | 一句话核心故事 |
| `story_request.main_action` | 谁或什么在做什么 |
| `story_request.scene_description` | 环境、空间、光线 |
| `provided_assets` | 素材列表；纯文本模式可为空数组 |

### 素材角色（`role_tag`）

`Character` · `Scene` · `Prop` · `Product` · `Costume` · `Style` · `Lighting` · `Motion` · `PreviousFrame` · `Layout`

每个素材建议填写：

- `must_keep` — 必须继承（如脸型、产品造型、空间布局）
- `must_avoid` — 禁止继承（如模特脸、风格图中的人物、背景文字）

### 可选参数

- `board_type_hint` — 分镜类型偏好
- `aspect_ratio` — 画幅（默认 `16:9`）
- `panel_count_hint` — 镜头格数（1–12）
- `duration_hint_seconds` — 时长参考
- `camera_movement_preference` — 机位偏好
- `style_goal` — 风格目标
- `allow_minor_inference` — 是否允许自动补全次要细节（默认 `true`）

---

## 输出说明

输出契约见 [`interface/output.json`](interface/output.json)。

| 字段 | 说明 |
|------|------|
| `storyboard_request` | 标准化后的用户目标与约束 |
| `asset_lock_map` | 每个素材的职责、继承与禁止项 |
| `storyboard_plan` | 分镜类型、格数、机位、连续性规则、每格功能 |
| `master_prompt_markdown` | 最终可执行的 Markdown 提示词 |
| `generation_mode` | 执行模式，当前为 `generate_image` |
| `generated_image_url` | 分镜图链接（成功时） |
| `image_error` | 结构化错误（失败或未接入执行器时） |

**注意：** 提示词与图片不是二选一。即使生图失败，也必须保留 Markdown 提示词和结构化错误信息。

---

## 中间对象（写提示词前必须形成）

在生成最终提示词之前，内部必须先明确三个对象：

1. **`storyboard_request`** — 用户要什么
2. **`asset_lock_map`** — 每个素材管什么、禁止什么
3. **`storyboard_plan`** — 分镜类型、格数、每格功能、连续性风险

若三者任一不清晰，不得直接写最终大提示词。

---

## 分镜类型

详见 [`skill/references/05_board_types.md`](skill/references/05_board_types.md)。

| 类型 | 适用场景 |
|------|----------|
| `continuous_shot_board` | 一镜到底、跟拍、连续推拉摇移 |
| `multi_shot_board` | 同场景多机位、对话反打、景别切换 |
| `spatial_establishing_board` | 地点建立、外到内、空间关系说明 |
| `action_progression_board` | 动作分阶段推进 |
| `transition_board` | 场景或状态转场 |
| `emotion_performance_board` | 情绪与表演重点 |
| `product_interaction_board` | 产品展示与交互 |

未指定时，系统会根据故事请求与素材自动选择。

---

## 输出形态（渲染器）

| 渲染器 | 用途 | 规范 |
|--------|------|------|
| `six_zone_pitch_sheet` | 提案、汇报、人工审核 | 头栏 + 锁定区 + 运镜区 + 关键帧区 + 分镜网格 + 技术尾栏 |
| `clean_reference_board` | 图像转视频、下游视觉模型 | 纯图像分镜，无说明文字与 UI 装饰 |

选择规则：

- `output_purpose = review_or_pitch` → 默认 6 区提案板
- `output_purpose = model_reference` → 纯净参考板

渲染器只负责呈现，不改动导演规划本身。

---

## 示例

`skill/examples/` 目录包含完整请求示例：

| 文件 | 场景 |
|------|------|
| `01_simple_request.md` | 简单请求（宇航员月面行走） |
| `02_multi_asset_request.md` | 多素材混合 |
| `03_action_progression_request.md` | 动作推进 |
| `04_spatial_establishing_request.md` | 空间建立 |
| `05_product_interaction_request.md` | 产品交互 |
| `06_transition_request.md` | 转场 |
| `07_bad_vs_good_outputs.md` | 好坏输出对比 |

---

## 辅助脚本

| 脚本 | 作用 |
|------|------|
| `run_storyboard_pipeline.py` | 端到端流水线：校验 → 锁定 → 规划 → 渲染 |
| `validate_storyboard_request.py` | 输入校验 |
| `compress_user_brief.py` | 构建 `storyboard_request` |
| `classify_asset_roles.py` | 构建 `asset_lock_map` |
| `plan_storyboard.py` | 构建 `storyboard_plan` |
| `render_storyboard_output.py` | 渲染 Markdown 提示词 |
| `evaluate_panel_coverage.py` | 评估分镜格覆盖度 |
| `smoke_test_pipeline.py` | 流水线冒烟测试 |

---

## 架构分层

```text
用户表单输入
    ↓
输入契约层          interface/input.json
    ↓
理解与锁定层        storyboard_request + asset_lock_map
    ↓
导演规划层          storyboard_plan
    ↓
渲染器层            six_zone_pitch_sheet / clean_reference_board
    ↓
执行器层            generate_image（可选）
    ↓
结构化输出 / 图片结果
```

完整说明见 [`skill/references/00_architecture.md`](skill/references/00_architecture.md)。

---

## 设计原则

- **单次表单直入**：内部阶段化处理，必要时最少澄清（每次最多补问 1–2 项）
- **素材强锁定**：防止风格图、服装图、场景图串位继承无关身份
- **导演式规划**：每格有独立视觉功能，避免重复「漂亮图」
- **具体可执行**：用景别、机位、动作阶段、空间锚点替代抽象形容词
- **省 token**：按需加载 reference 与 blueprint，不在入口重复全部规则

## 明确不做的事

- 不把 6 区提案板当作唯一正确输出
- 不默认继承参考图中的无关人物身份
- 不在没有执行器时静默省略图片错误
- 不维护旧版 `/start → /assets → /prompt → /storyboard` 多轮命令流

---

## 延伸阅读

- Agent 入口：[`skill/SKILL.md`](skill/SKILL.md)
- 工作流：[`skill/workflow.md`](skill/workflow.md)
- 质检清单：[`skill/references/09_quality_control.md`](skill/references/09_quality_control.md)
- 失败案例：[`skill/references/10_failure_cases.md`](skill/references/10_failure_cases.md)

<p align="right"><a href="#中文">↑ 回到顶部</a> · <a href="#english">English ↓</a></p>

---

<a id="english"></a>

# universal-storyboard-skill

A universal storyboard design and generation skill. It turns structured form inputs and reference assets into **asset-locked, director-planned, execution-ready** storyboard plans and prompts.

The goal is not to stack flashy prompt words, but to follow a stable pipeline:

```text
Form Input → Asset Locking → Director Planning → Renderer Selection → Prompt Generation → QA → Output
```

---

## Use Cases

- Plan multi-panel storyboards from reference images (character, scene, product, costume, etc.)
- Distinguish between **human review / pitch** and **downstream model reference** output modes
- Enforce asset role isolation (e.g., a costume image locks clothing only — not the model's identity)
- Support common board types: action progression, spatial establishing, transitions, emotion/performance, product interaction, continuous shots, multi-camera setups

---

## Core Capabilities

| Capability | Description |
|------------|-------------|
| Asset locking | Assign a unique role to each asset; define what must be inherited and what must not |
| Director planning | Auto-select board type, panel count, camera strategy, and continuity rules |
| Dual renderers | `six_zone_pitch_sheet` (6-zone pitch board) or `clean_reference_board` (clean reference board) |
| Structured output | Return intermediate objects, Markdown prompts, image results, or structured errors together |
| Chinese-first UX | Default Chinese user experience and Chinese prompts |

---

## Directory Structure

```text
universal-storyboard-skill/
├── README.md                 # This file
├── interface/                # Input/output JSON Schema
│   ├── input.json
│   └── output.json
└── skill/
    ├── SKILL.md              # Agent entry: triggers, read order, constraints
    ├── workflow.md           # Internal main workflow
    ├── references/           # Rules and methods (architecture, input, assets, boards, QA, etc.)
    ├── assets/               # Board blueprints, style guides, output contract templates
    ├── examples/             # 7 request examples + good vs bad output comparison
    └── scripts/              # Repeatable Python helper pipeline
```

**Single source of truth:**

- `SKILL.md` — Entry routing only; does not duplicate the full methodology
- `workflow.md` — The one main workflow
- `interface/*.json` — Input/output contracts
- `references/*.md` — Reasoning rules
- `assets/board_blueprints/*.md` — Concrete board templates
- `scripts/*.py` — Deterministic helper processing

---

## Quick Start

### As an Agent Skill

After installing or referencing this skill, the agent follows `skill/SKILL.md`:

1. Read architecture and workflow
2. Validate form input
3. Complete asset locking and director planning
4. Select renderer based on output purpose
5. Generate Markdown prompts and self-check

Trigger keywords: storyboard, 分镜, asset locking, director planning, six-zone pitch board, reference board.

### As a Pipeline Script

Python 3 required. No extra dependencies.

```bash
# Run from a JSON file
python skill/scripts/run_storyboard_pipeline.py path/to/input.json

# Run from stdin
cat path/to/input.json | python skill/scripts/run_storyboard_pipeline.py

# Run smoke tests
python skill/scripts/smoke_test_pipeline.py
```

Output is JSON with fields such as `storyboard_request`, `asset_lock_map`, `storyboard_plan`, and `master_prompt_markdown`.

---

## Input

Contract: [`interface/input.json`](interface/input.json). Details: [`skill/references/02_input_requirements.md`](skill/references/02_input_requirements.md).

### Minimum Required Fields

| Field | Description |
|-------|-------------|
| `project_info.input_mode` | `asset_driven` / `text_only` / `mixed` |
| `project_info.output_purpose` | `review_or_pitch` (for humans) or `model_reference` (for models) |
| `project_info.generation_mode` | Currently fixed to `generate_image` |
| `story_request.story_framework` | One-sentence core story |
| `story_request.main_action` | Who or what is doing what |
| `story_request.scene_description` | Environment, space, lighting |
| `provided_assets` | Asset list; may be empty in text-only mode |

### Asset Roles (`role_tag`)

`Character` · `Scene` · `Prop` · `Product` · `Costume` · `Style` · `Lighting` · `Motion` · `PreviousFrame` · `Layout`

Recommended per asset:

- `must_keep` — Must inherit (e.g., face shape, product form, spatial layout)
- `must_avoid` — Must not inherit (e.g., model face, people in style refs, background text)

### Optional Parameters

- `board_type_hint` — Preferred board type
- `aspect_ratio` — Aspect ratio (default `16:9`)
- `panel_count_hint` — Panel count (1–12)
- `duration_hint_seconds` — Duration reference
- `camera_movement_preference` — Camera preference
- `style_goal` — Style target
- `allow_minor_inference` — Allow auto-filling minor details (default `true`)

---

## Output

Contract: [`interface/output.json`](interface/output.json).

| Field | Description |
|-------|-------------|
| `storyboard_request` | Normalized user goals and constraints |
| `asset_lock_map` | Per-asset roles, inherit rules, and avoid rules |
| `storyboard_plan` | Board type, panel count, camera, continuity rules, per-panel function |
| `master_prompt_markdown` | Final executable Markdown prompt |
| `generation_mode` | Execution mode; currently `generate_image` |
| `generated_image_url` | Storyboard image URL on success |
| `image_error` | Structured error on failure or when no executor is connected |

**Note:** Prompts and images are not mutually exclusive. Even if image generation fails, Markdown prompts and structured errors must still be returned.

---

## Intermediate Objects (Required Before Final Prompt)

Before writing the final prompt, three objects must be clear internally:

1. **`storyboard_request`** — What the user wants
2. **`asset_lock_map`** — What each asset controls and what it must not leak
3. **`storyboard_plan`** — Board type, panel count, per-panel function, continuity risks

If any of these is unclear, do not write the final large prompt directly.

---

## Board Types

See [`skill/references/05_board_types.md`](skill/references/05_board_types.md).

| Type | Best For |
|------|----------|
| `continuous_shot_board` | One-shot, follow cam, continuous dolly/pan/tilt |
| `multi_shot_board` | Multi-camera in one scene, shot-reverse-shot, coverage changes |
| `spatial_establishing_board` | Location establishing, exterior-to-interior, spatial relationships |
| `action_progression_board` | Staged action progression |
| `transition_board` | Scene or state transitions |
| `emotion_performance_board` | Emotion and performance focus |
| `product_interaction_board` | Product showcase and interaction |

If unspecified, the system auto-selects based on story request and assets.

---

## Output Formats (Renderers)

| Renderer | Purpose | Spec |
|----------|---------|------|
| `six_zone_pitch_sheet` | Pitch, review, human approval | Header + lock zone + camera zone + keyframe zone + panel grid + technical footer |
| `clean_reference_board` | Image-to-video, downstream visual models | Pure image panels, no labels or UI chrome |

Selection rules:

- `output_purpose = review_or_pitch` → default 6-zone pitch board
- `output_purpose = model_reference` → clean reference board

Renderers handle presentation only; they do not change director planning.

---

## Examples

Full request examples live in `skill/examples/`:

| File | Scenario |
|------|----------|
| `01_simple_request.md` | Simple request (astronaut walking on the Moon) |
| `02_multi_asset_request.md` | Multi-asset mixed input |
| `03_action_progression_request.md` | Action progression |
| `04_spatial_establishing_request.md` | Spatial establishing |
| `05_product_interaction_request.md` | Product interaction |
| `06_transition_request.md` | Transition |
| `07_bad_vs_good_outputs.md` | Good vs bad output comparison |

---

## Helper Scripts

| Script | Purpose |
|--------|---------|
| `run_storyboard_pipeline.py` | End-to-end pipeline: validate → lock → plan → render |
| `validate_storyboard_request.py` | Input validation |
| `compress_user_brief.py` | Build `storyboard_request` |
| `classify_asset_roles.py` | Build `asset_lock_map` |
| `plan_storyboard.py` | Build `storyboard_plan` |
| `render_storyboard_output.py` | Render Markdown prompt |
| `evaluate_panel_coverage.py` | Evaluate panel coverage |
| `smoke_test_pipeline.py` | Pipeline smoke test |

---

## Architecture Layers

```text
User Form Input
    ↓
Input Contract Layer       interface/input.json
    ↓
Understanding & Lock Layer storyboard_request + asset_lock_map
    ↓
Director Planning Layer    storyboard_plan
    ↓
Renderer Layer             six_zone_pitch_sheet / clean_reference_board
    ↓
Executor Layer             generate_image (optional)
    ↓
Structured Output / Image Result
```

Full details: [`skill/references/00_architecture.md`](skill/references/00_architecture.md).

---

## Design Principles

- **Single-form entry**: Internal staged processing; minimal clarification when needed (max 1–2 questions per round)
- **Strong asset locking**: Prevent style/costume/scene refs from leaking unrelated identities
- **Director-style planning**: Each panel has a distinct visual function; avoid duplicate "pretty frames"
- **Concrete and executable**: Use shot size, camera position, action stage, and spatial anchors instead of vague adjectives
- **Token-efficient**: Load references and blueprints on demand; do not duplicate all rules at entry

## Explicit Non-Goals

- Do not treat the 6-zone pitch board as the only valid output
- Do not default-inherit unrelated identities from reference images
- Do not silently omit image errors when no executor is connected
- Do not maintain the legacy `/start → /assets → /prompt → /storyboard` multi-turn command flow

---

## Further Reading

- Agent entry: [`skill/SKILL.md`](skill/SKILL.md)
- Workflow: [`skill/workflow.md`](skill/workflow.md)
- QA checklist: [`skill/references/09_quality_control.md`](skill/references/09_quality_control.md)
- Failure cases: [`skill/references/10_failure_cases.md`](skill/references/10_failure_cases.md)

<p align="right"><a href="#english">↑ Back to top</a> · <a href="#中文">中文 ↑</a></p>
