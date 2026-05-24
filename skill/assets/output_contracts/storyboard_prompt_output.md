# 最终输出契约

本文件定义此 skill 的最终输出结构。

## 最低输出字段

1. **storyboard_request**
   - 标准化导演输入与推断字段
2. **asset_lock_map**
   - 素材锁定结果与导演锚点
3. **preproduction_board_plan**
   - 完整预制作导演板结构
4. **master_prompt_markdown**
   - Markdown 格式的最终中文提示词
5. **generated_image_url**
   - 执行生图成功时返回图片链接
6. **image_error**
   - 执行失败或未接入真实执行器时返回结构化错误

## `preproduction_board_plan` 最低结构

应至少包含：

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
- `inferred_fields`

## `master_prompt_markdown` 要求

如果输出为完整预制作导演板，则提示词必须表达：

- 顶部概念区
- 角色参考区
- 场景与美术区
- 顶视机位阻挡区
- shot list 主区
- 灯光 / 摄影 / 色彩 / 声音 / mood 区

如果输出为 `clean_reference_board`，则提示词必须表达：

- 分镜格数和排布
- 每格主体、动作、空间关系
- 连续性约束
- 禁止文字和 UI 装饰

## 禁止事项

- 不允许只返回大段文学性描述
- 不允许只返回镜头列表而没有完整渲染指令
- 不允许跳过 `preproduction_board_plan` 直接给结果
- 不允许把 Markdown 提示词和图片结果做成二选一
