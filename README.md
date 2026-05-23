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
