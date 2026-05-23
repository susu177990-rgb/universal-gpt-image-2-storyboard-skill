# 示例 01：简单请求（宇航员在月球行走）

## 输入

- 输入模式：素材与文本混合
- 输出目的：给人审核 / 提案
- 主动作：宇航员在月球表面行走
- 场景描述：高反差月面，强烈顶侧光，深黑天空
- 素材：
  - `astronaut_ref`：角色
  - `moon_surface_ref`：场景

## 中间结果重点

### `asset_lock_map`

- `astronaut_ref`
  - 必须继承：头盔结构、宇航服轮廓、体型比例
  - 禁止继承：角色图背景
- `moon_surface_ref`
  - 必须继承：坑洞地形、灰尘质感、光照方向
  - 禁止继承：无关人物或设备

### `storyboard_plan`

- 分镜类型：`continuous_shot_board`
- 输出形态：`six_zone_pitch_sheet`
- 格数：4
- 机位策略：侧向跟拍 + 落脚特写

## 预期输出

- 同时返回：
  - `master_prompt_markdown`
  - `generated_image_url`

### Markdown 提示词片段

````md
# 月面行走

## 素材锁定

- `astronaut_ref` 锁定角色身份、宇航服轮廓和头盔结构
- `moon_surface_ref` 锁定月面地形、灰尘质感和强烈光向

## 导演规划摘要

- 分镜类型：`continuous_shot_board`
- 格数：4
- 连续性重点：角色步态、脚印延续、光照方向稳定

## 最终渲染提示词

```text
请生成一张全中文 6 区故事板提案板。
主分镜按 4 格连续展示宇航员行走过程：起步、悬浮中段、落脚瞬间、脚印结果。
保持宇航服身份一致，保持月面地形和光照方向一致。
```
````

### 图片结果

- `generated_image_url`：应返回月面行走故事板图片链接
