# Shot List 设计规则

当前 skill 的核心不再是“每格 panel 怎么写”，而是“shot list 如何体现导演意图”。

## 每个 shot 都必须回答

- 这个镜头为什么存在
- 它负责推进什么信息
- 它在节奏上处于什么位置
- 它和前后镜头怎样衔接

## 每个 shot 至少包含

- `shot_id`
- `shot_role`
- `shot_size`
- `camera_angle`
- `camera_motion`
- `blocking`
- `action_beat`
- `performance_beat`
- `dialogue_or_voiceover`
- `mood_beat`
- `lighting_note`
- `why_this_shot_exists`

## 合格标准

- 镜头职责明确
- 景别与角度有变化
- blocking 可读
- 动作或表演推进成立
- 与人物关系、tone、空间逻辑一致

## 判废条件

以下 shot 需要重写：

- 只是重复前一个镜头
- 没有导演存在理由
- 只有美感，没有叙事功能
- 会破坏空间或人物连续性
- 不能帮助模型理解人物关系、空间路径或节奏
