# 示例 02：多素材请求（霓虹武士与发光瓶子）

## 输入

- 输入模式：素材与文本混合
- 输出目的：给人审核 / 提案
- 主动作：武士坐在酒吧里，拿起发光瓶子饮用
- 素材：
  - `face_ref`：角色
  - `bar_ref`：场景
  - `armor_ref`：服装
  - `bottle_ref`：产品
  - `neon_style_ref`：风格

## 中间结果重点

### `asset_lock_map`

- `face_ref` 只负责人物身份
- `armor_ref` 只负责盔甲，不继承模特脸
- `bottle_ref` 负责瓶子外形、比例、发光特征
- `neon_style_ref` 只负责青紫霓虹质感，不继承具体人物和街景

### `storyboard_plan`

- 分镜类型：`product_interaction_board`
- 输出形态：`six_zone_pitch_sheet`
- 格数：4
- 风险控制：产品不可被手完全遮挡；风格图不得污染场景内容

## 预期输出

### Markdown 提示词片段

````md
# 霓虹武士饮酒

## 素材锁定

- `face_ref` 锁定脸部与发型
- `armor_ref` 只锁定服装，不锁定模特身份
- `bottle_ref` 锁定瓶子造型、玻璃质感和发光颜色
- `neon_style_ref` 只锁定霓虹色彩与潮湿金属质感

## 导演规划摘要

- 分镜类型：`product_interaction_board`
- 格数：4
- 重点：人物身份稳定、瓶子持续可见、酒吧氛围统一
````

### 图片结果

- `generated_image_url`：应返回霓虹酒吧故事板图片链接
