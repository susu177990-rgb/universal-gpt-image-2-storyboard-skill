# 最终输出契约

本文件定义此 skill 的最终输出结构。

## 最低输出字段

1. **storyboard_plan**
   - 导演规划的结构化结果
2. **master_prompt_markdown**
   - Markdown 格式的最终中文提示词
3. **generation_mode**
   - 当前固定为 `generate_image`
4. **generated_image_url**
   - 执行生图成功时返回图片链接
5. **image_error**
   - 执行失败或未接入真实执行器时返回结构化错误

## `storyboard_plan` 最低结构

应至少包含：

- `board_type`
- `output_format`
- `panel_count`
- `camera_strategy`
- `continuity_rules`
- `panels`
- `risk_controls`

## `master_prompt_markdown` 要求

如果输出为 `six_zone_pitch_sheet`，则提示词必须表达：

- 头部信息栏
- 锁定栏
- 机位与运动规划区
- 关键帧辅助区
- 主分镜网格
- 技术尾栏

如果输出为 `clean_reference_board`，则提示词必须表达：

- 分镜格数和排布
- 每格主体、动作、空间关系
- 连续性约束
- 禁止文字和 UI 装饰

## 禁止事项

- 不允许只返回大段文学性描述
- 不允许只返回镜头列表而没有完整渲染指令
- 不允许跳过 `storyboard_plan` 直接给结果
- 不允许把 Markdown 提示词和图片结果做成二选一
