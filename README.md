# Universal Storyboard Skill | 通用导演故事板

中文 | [English](#english)

`Universal Storyboard Skill` 是一个偏导演工作流的故事板 skill。不是只给你几张灵感图，而是把你直接发送的故事需求和参考素材整理成一张完整的预制作导演板——先输出可审阅的 Markdown 提示词，再在你确认后进入生图。

## 适合搜索的关键词

storyboard, director board, pre-production board, cinematic storyboard, storyboard skill, 故事板, 导演板, 预制作板, AI storyboard, visual planning, shot list, blocking, 分镜设计, 视觉效果板, director-level storyboard, asset-locked storyboard.

## 这个 Skill 能做什么

- 把零散故事需求整理成完整的预制作导演板。
- 先出可审阅提示词，你确认后再生图——不走"一上来就浪费生成次数"的流程。
- 强素材锁定：风格素材锁质感不锁内容、服装素材锁服装不继承模特身份。
- 导演推断明确落在结果里：核心故事是唯一必填字段，其余强推断并回写。
- 产出 `cinematic_preproduction_board` 或 `clean_reference_board`。

## 为什么不是普通分镜工具

普通分镜工具往往"直接拼 prompt 出图"。这个 skill：

- 素材锁定 + 导演推断先跑完，再写最终提示词。
- 内部必须形成三个中间对象（`storyboard_request`、`asset_lock_map`、`preproduction_board_plan`）才允许写出最终输出。
- 先 Markdown 审阅、后确认生图，适合提案、沟通和有质量要求的场景。

## 支持的场景

- 导演提案板
- 客户汇报视觉板
- 角色、服装、场景都有参考素材的锁定型故事板
- 需要"像工作板"结果的导演沟通
- 先做创意和结构确认、再生图的工作流

## 安装

```bash
npx skills add susu177990-rgb/universal-gpt-image-2-storyboard-skill
```

Fork 版本：

```bash
npx skills add <YOUR_GITHUB_USERNAME>/universal-storyboard-skill
```

## 使用示例

### 标准两步流程

```text
/start
[发送故事需求和参考素材]
/board
[审阅提示词]
/image
```

### 只想重整提示词

```text
/prompt
```

## 常用命令

| 命令 | 作用 |
|---|---|
| `/start` | 介绍两步用法、输入要求和结果形态 |
| `/board` | 生成完整导演板 Markdown 提示词 |
| `/prompt` | 只输出或重整导演板提示词文本 |
| `/image` | 在已有提示词基础上执行确认生图 |
| `/help` | 查看帮助 |

## 内部主链

```text
用户发送需求和素材
  →
素材锁定与导演锚点提取
  →
故事字段强推断
  →
preproduction_board_plan
  →
Markdown 提示词
  →
等待确认生图
  →
图片结果 / 明确错误信息
```

## 核心中间结果

- `storyboard_request`：用户目标与输入约束的标准化结果
- `asset_lock_map`：每个素材负责什么、禁止继承什么
- `preproduction_board_plan`：完整导演板结构、shot list、blocking、lighting 与风险控制

这三个结果决定最后导演板长什么样，也决定为什么它比"直接拼 prompt 出图"更稳。

## 项目结构

```text
universal-storyboard-skill/
├── SKILL.md
├── README.md
├── optimized_system_prompt.md
├── workflow.md
├── assets/
├── examples/
├── references/
└── scripts/
```

## 设计上的硬规则

- 核心故事是唯一必填叙事字段。
- 关系、表演、tone、场景可以强推断，但必须回写到推断字段。
- 风格素材锁质感，不锁内容。
- 服装素材锁服装，不继承模特身份。
- 输出结果必须像预制作导演板，而不是普通分镜格子。
- 首轮必须先输出完整提示词；只有用户确认后才继续生图。

---

## English

`Universal Storyboard Skill` builds a full pre-production director board instead of a loose inspiration sheet. It first produces reviewable markdown prompts, then waits for confirmation before image generation.

## Search Keywords

storyboard, director board, pre-production board, cinematic storyboard, AI storyboard, visual planning, shot list, blocking, asset-locked storyboard, 故事板, 导演板, 预制作板.

## What It Does

- Turns scattered story requirements into a complete pre-production board.
- Two-step flow: review markdown prompts first, then generate images on confirmation.
- Strong asset locking: style refs lock look, costume refs lock costume, neither inherits source identity.
- Director inference is explicit: story is the only required field; the rest is strongly inferred and written back.
- Outputs `cinematic_preproduction_board` or `clean_reference_board`.

## Install

```bash
npx skills add susu177990-rgb/universal-gpt-image-2-storyboard-skill
```

For forks:

```bash
npx skills add <YOUR_GITHUB_USERNAME>/universal-storyboard-skill
```

## Fast Path

```text
/start -> send story/assets -> /board -> review -> /image
```

## Core Rule

The output must look like a pre-production director board, not a loose storyboard grid. Asset locking and director inference come before final prompt writing.

## License / 许可

仓库内如有单独许可文件，以仓库实际文件为准。