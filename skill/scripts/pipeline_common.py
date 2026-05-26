import json
import re
import sys
from typing import Any, Dict, List, Optional


ROLE_META = {
    "Character": {
        "priority": 100,
        "must_keep_defaults": ["人物身份", "脸部特征", "发型", "体型"],
        "must_avoid_defaults": ["背景环境", "无关路人", "场景文字"],
        "identity_defaults": ["脸型轮廓稳定", "发型一致", "年龄感稳定", "体型比例一致"],
        "performance_defaults": ["表情弹性明确", "眼神变化可读", "姿态符合角色气质"],
        "positive_prefix": "锁定角色身份",
        "negative_prefix": "禁止继承无关人物或背景",
    },
    "Scene": {
        "priority": 90,
        "must_keep_defaults": ["空间结构", "环境布局", "主要光向"],
        "must_avoid_defaults": ["场景内无关人物身份", "不相关风格污染"],
        "environment_defaults": ["空间层次清晰", "功能区明确", "生活化物件自然分布"],
        "lighting_defaults": ["主光方向明确", "空间内动机光源清楚", "昼夜气质一致"],
        "positive_prefix": "锁定场景结构",
        "negative_prefix": "禁止把场景中的人物当主角",
    },
    "Product": {
        "priority": 80,
        "must_keep_defaults": ["产品外形", "比例", "材质", "品牌识别点"],
        "must_avoid_defaults": ["遮挡产品主体", "错误比例"],
        "prop_defaults": ["产品轮廓稳定", "关键细节清晰", "交互路径明确"],
        "positive_prefix": "锁定产品识别度",
        "negative_prefix": "禁止产品变形或被遮挡",
    },
    "Prop": {
        "priority": 75,
        "must_keep_defaults": ["道具外形", "尺寸关系", "交互位置"],
        "must_avoid_defaults": ["道具消失", "道具变成角色"],
        "prop_defaults": ["道具形态稳定", "与主体的比例清晰", "使用方式可见"],
        "positive_prefix": "锁定道具形态",
        "negative_prefix": "禁止道具串位或消失",
    },
    "Costume": {
        "priority": 70,
        "must_keep_defaults": ["服装版型", "纹样", "材质", "颜色"],
        "must_avoid_defaults": ["模特脸", "模特体型", "模特表情"],
        "identity_defaults": ["服装轮廓清晰", "色彩关系统一", "材质逻辑稳定"],
        "positive_prefix": "只锁定服装",
        "negative_prefix": "禁止继承服装模特身份",
    },
    "Motion": {
        "priority": 65,
        "must_keep_defaults": ["动作方向", "重心变化", "关键姿态"],
        "must_avoid_defaults": ["运动参考人物身份", "运动参考背景"],
        "performance_defaults": ["动作起承转合明确", "重心变化清晰", "节奏可分段"],
        "positive_prefix": "锁定动作节奏",
        "negative_prefix": "禁止继承动作参考的身份与背景",
    },
    "Lighting": {
        "priority": 60,
        "must_keep_defaults": ["光向", "色温", "阴影逻辑"],
        "must_avoid_defaults": ["改变场景结构", "覆盖角色身份"],
        "lighting_defaults": ["主光方向稳定", "色温与反差有明确倾向", "动机光源真实"],
        "positive_prefix": "锁定光照逻辑",
        "negative_prefix": "禁止光照参考篡改空间结构",
    },
    "Layout": {
        "priority": 55,
        "must_keep_defaults": ["构图关系", "主体排布", "画面重心"],
        "must_avoid_defaults": ["覆盖角色身份", "覆盖场景内容"],
        "environment_defaults": ["画面重心明确", "空间阅读顺序清晰", "主体相对关系可控"],
        "positive_prefix": "锁定构图布局",
        "negative_prefix": "禁止布局参考改写角色和场景",
    },
    "Style": {
        "priority": 50,
        "must_keep_defaults": ["色彩倾向", "质感", "媒介风格"],
        "must_avoid_defaults": ["风格图中的人物", "风格图中的具体地点"],
        "style_defaults": ["整体调色统一", "媒介质感明确", "风格不污染内容层"],
        "positive_prefix": "只提取风格处理",
        "negative_prefix": "禁止继承风格图内容物",
    },
    "PreviousFrame": {
        "priority": 110,
        "must_keep_defaults": ["上一帧角色状态", "机位方向", "道具状态", "光线状态"],
        "must_avoid_defaults": ["无故跳切", "重置角色位置"],
        "identity_defaults": ["角色外观连续", "姿态状态连续"],
        "environment_defaults": ["空间方向连续", "镜头轴线连续"],
        "lighting_defaults": ["主光方向连续", "色温与曝光连续"],
        "prop_defaults": ["道具状态连续", "持握关系连续"],
        "positive_prefix": "强制保持上一帧连续性",
        "negative_prefix": "禁止忽略上一帧连续性",
    },
}

ROLE_ALIASES = {
    "character": "Character",
    "角色": "Character",
    "scene": "Scene",
    "场景": "Scene",
    "prop": "Prop",
    "道具": "Prop",
    "product": "Product",
    "产品": "Product",
    "costume": "Costume",
    "服装": "Costume",
    "style": "Style",
    "风格": "Style",
    "lighting": "Lighting",
    "光照": "Lighting",
    "motion": "Motion",
    "动作": "Motion",
    "运动": "Motion",
    "previousframe": "PreviousFrame",
    "上一帧": "PreviousFrame",
    "layout": "Layout",
    "布局": "Layout",
}

BOARD_TYPE_MAP = {
    "Action Progression": "action_progression_board",
    "Spatial Establishing": "spatial_establishing_board",
    "Transition": "transition_board",
    "Emotion Performance": "emotion_performance_board",
    "Continuous Shot": "continuous_shot_board",
    "Multi-Shot": "multi_shot_board",
    "Product Interaction": "product_interaction_board",
    "动作推进": "action_progression_board",
    "空间建立": "spatial_establishing_board",
    "转场": "transition_board",
    "情绪表演": "emotion_performance_board",
    "连续镜头": "continuous_shot_board",
    "多机位": "multi_shot_board",
    "产品交互": "product_interaction_board",
}

INPUT_MODE_ALIASES = {
    "asset_driven": "asset_driven",
    "text_only": "text_only",
    "mixed": "mixed",
    "主要依赖素材": "asset_driven",
    "纯文本创作": "text_only",
    "素材与文本混合": "mixed",
}

OUTPUT_PURPOSE_ALIASES = {
    "review_or_pitch": "review_or_pitch",
    "model_reference": "model_reference",
    "给人审核 / 提案": "review_or_pitch",
    "给模型参考": "model_reference",
    "带文字导演故事板": "review_or_pitch",
    "无文字分镜宫格图": "model_reference",
}

GENERATION_MODE_ALIASES = {
    "await_confirmation": "await_confirmation",
    "generate_image": "generate_image",
    "先输出提示词，等待确认生图": "await_confirmation",
    "等待确认生图": "await_confirmation",
    "确认生图": "generate_image",
    "直接执行生图": "generate_image",
}

ASPECT_RATIO_ALIASES = {
    "16:9": "16:9",
    "9:16": "9:16",
    "1:1": "1:1",
    "4:3": "4:3",
    "2.35:1": "2.35:1",
    "16:9 横屏": "16:9",
    "9:16 竖屏": "9:16",
    "1:1 方形": "1:1",
    "4:3 传统": "4:3",
    "2.35:1 电影宽银幕": "2.35:1",
}

IMAGE_QUALITY_ALIASES = {
    "1K": "1K",
    "2K": "2K",
    "4K": "4K",
    "1K 标准": "1K",
    "2K 高清": "2K",
    "4K 超清": "4K",
}

CAMERA_PREFERENCE_ALIASES = {
    "自动推断": "",
    "固定机位": "固定机位",
    "推镜头": "推镜头",
    "拉镜头": "拉镜头",
    "摇摄": "摇摄",
    "跟拍": "跟拍",
    "环绕拍摄": "环绕拍摄",
    "手持纪实": "手持纪实",
}

STYLE_GOAL_ALIASES = {
    "自动推断": "",
    "电影写实": "电影写实",
    "胶片纪实": "胶片纪实",
    "赛博朋克霓虹": "赛博朋克霓虹",
    "低饱和冷调": "低饱和冷调",
    "高饱和广告片": "高饱和广告片",
    "暖色复古": "暖色复古",
    "黑白胶片": "黑白胶片",
    "黑白线稿模式": "黑白线稿模式",
    "黑白线稿": "黑白线稿模式",
    "水彩插画": "水彩插画",
    "赛璐璐动画": "赛璐璐动画",
    "3D 游戏 CG": "3D 游戏 CG",
    "纪录片手持": "纪录片手持",
}

PRODUCTION_CONTEXT_ALIASES = {
    "短片": "短片",
    "广告": "广告",
    "情景喜剧": "情景喜剧",
    "剧情片": "剧情片",
    "流媒体短内容": "流媒体短内容",
}

BOARD_DENSITY_ALIASES = {
    "高": "high",
    "中": "medium",
    "低": "low",
    "信息丰富": "high",
    "平衡": "medium",
    "极简": "low",
}

RENDER_DETAIL_LEVEL_ALIASES = {
    "高": "high",
    "中": "medium",
    "低": "low",
}

INFERENCE_TOLERANCE_ALIASES = {
    "强": "strong",
    "中": "medium",
    "弱": "weak",
}

BOARD_TYPE_KEYWORDS = {
    "action_progression_board": ["挥拳", "奔跑", "打斗", "动作", "追逐", "跳", "冲刺", "fight", "run"],
    "spatial_establishing_board": ["空间", "环境", "入口", "实验室", "场景介绍", "location", "room"],
    "transition_board": ["变身", "转场", "变化", "镜中", "before", "after", "transform", "switch"],
    "emotion_performance_board": ["情绪", "表情", "眼神", "哭", "悲伤", "愤怒", "performance", "emotion"],
    "continuous_shot_board": ["一镜到底", "连续", "跟拍", "推镜", "tracking", "continuous"],
    "multi_shot_board": ["对话", "反打", "多机位", "对峙", "shot reverse", "dialogue"],
    "product_interaction_board": ["产品", "拿起", "展示", "观察", "使用", "瓶子", "product", "serum"],
}

SHOT_ROLE_LIBRARY = {
    "action_progression_board": ["建立", "推进", "高潮", "收束"],
    "spatial_establishing_board": ["建立", "桥接", "推进", "收束"],
    "transition_board": ["建立", "桥接", "高潮", "收束"],
    "emotion_performance_board": ["建立", "推进", "反应", "收束"],
    "continuous_shot_board": ["建立", "推进", "高潮", "收束"],
    "multi_shot_board": ["建立", "推进", "反应", "收束"],
    "product_interaction_board": ["建立", "推进", "细节", "收束"],
}


def dump_json(data: Dict[str, Any]) -> None:
    json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def load_input() -> Any:
    if len(sys.argv) > 1 and sys.argv[1] not in {"--help", "-h"}:
        try:
            return json.loads(sys.argv[1])
        except json.JSONDecodeError:
            with open(sys.argv[1], "r", encoding="utf-8") as handle:
                return json.load(handle)
    return json.load(sys.stdin)


def split_terms(raw_value: Any) -> List[str]:
    if raw_value is None:
        return []
    if isinstance(raw_value, list):
        values = raw_value
    else:
        values = re.split(r"[，,、；;|\n]+", str(raw_value))
    cleaned: List[str] = []
    for item in values:
        value = str(item).strip()
        if value and value not in cleaned:
            cleaned.append(value)
    return cleaned


def normalize_role(role_tag: Optional[str]) -> Optional[str]:
    if not role_tag:
        return None
    role = str(role_tag).strip()
    if role in ROLE_META:
        return role
    return ROLE_ALIASES.get(role.lower())


def normalize_input_mode(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return INPUT_MODE_ALIASES.get(str(value).strip())


def normalize_output_purpose(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return OUTPUT_PURPOSE_ALIASES.get(str(value).strip())


def normalize_generation_mode(value: Optional[str]) -> str:
    if value is None:
        return "await_confirmation"
    return GENERATION_MODE_ALIASES.get(str(value).strip(), "await_confirmation")


def normalize_aspect_ratio(value: Optional[str]) -> str:
    if value is None:
        return "16:9"
    return ASPECT_RATIO_ALIASES.get(str(value).strip(), "16:9")


def normalize_image_quality(value: Optional[str]) -> str:
    if value is None:
        return "2K"
    return IMAGE_QUALITY_ALIASES.get(str(value).strip(), "2K")


def normalize_camera_preference(value: Optional[str]) -> str:
    if value is None:
        return ""
    return CAMERA_PREFERENCE_ALIASES.get(str(value).strip(), str(value).strip())


def normalize_style_goal(value: Optional[str]) -> str:
    if value is None:
        return ""
    return STYLE_GOAL_ALIASES.get(str(value).strip(), str(value).strip())


def normalize_production_context(value: Optional[str]) -> str:
    if value is None:
        return ""
    return PRODUCTION_CONTEXT_ALIASES.get(str(value).strip(), str(value).strip())


def normalize_board_density(value: Optional[str]) -> str:
    if value is None:
        return "high"
    return BOARD_DENSITY_ALIASES.get(str(value).strip(), "high")


def normalize_render_detail_level(value: Optional[str]) -> str:
    if value is None:
        return "high"
    return RENDER_DETAIL_LEVEL_ALIASES.get(str(value).strip(), "high")


def normalize_inference_tolerance(value: Optional[str]) -> str:
    if value is None:
        return "strong"
    return INFERENCE_TOLERANCE_ALIASES.get(str(value).strip(), "strong")


def resolve_assets(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, dict):
        assets = payload.get("provided_assets") or payload.get("assets") or []
    elif isinstance(payload, list):
        assets = payload
    else:
        assets = []

    resolved: List[Dict[str, Any]] = []
    for index, asset in enumerate(assets, start=1):
        if isinstance(asset, str):
            asset = {"asset_id": f"asset_{index}", "description": asset}
        resolved_role = normalize_role(asset.get("role_tag")) or infer_role_from_text(
            " ".join(
                [
                    str(asset.get("asset_id", "")),
                    str(asset.get("description", "")),
                    str(asset.get("must_keep", "")),
                    str(asset.get("must_avoid", "")),
                ]
            )
        )
        resolved.append({**asset, "resolved_role": resolved_role})
    return resolved


def infer_role_from_text(text: str) -> str:
    lowered = text.lower()
    if any(token in lowered for token in ["人脸", "演员", "主角", "角色", "face", "portrait"]):
        return "Character"
    if any(token in lowered for token in ["房间", "客厅", "街道", "实验室", "场景", "scene"]):
        return "Scene"
    if any(token in lowered for token in ["瓶", "产品", "包装", "product", "serum"]):
        return "Product"
    if any(token in lowered for token in ["衣服", "盔甲", "服装", "costume", "outfit"]):
        return "Costume"
    if any(token in lowered for token in ["动作", "姿态", "pose", "motion"]):
        return "Motion"
    if any(token in lowered for token in ["光", "lighting", "阴影"]):
        return "Lighting"
    if any(token in lowered for token in ["布局", "构图", "layout"]):
        return "Layout"
    if any(token in lowered for token in ["风格", "调色", "style", "palette"]):
        return "Style"
    if any(token in lowered for token in ["上一帧", "previous"]):
        return "PreviousFrame"
    return "Prop"


def build_title(story_framework: str, explicit_title: Optional[str]) -> str:
    if explicit_title and explicit_title.strip():
        return explicit_title.strip()
    story = (story_framework or "").strip()
    return story[:28] if story else "未命名视觉规划板"


def choose_output_format(output_purpose: str) -> str:
    if output_purpose == "model_reference":
        return "clean_reference_board"
    return "cinematic_preproduction_board"


def choose_board_type(storyboard_request: Dict[str, Any]) -> str:
    hint = storyboard_request.get("board_type_hint")
    if hint:
        mapped = BOARD_TYPE_MAP.get(hint)
        if mapped:
            return mapped
    text_blob = " ".join(
        [
            storyboard_request.get("story_framework", ""),
            storyboard_request.get("main_action", ""),
            storyboard_request.get("scene_description", ""),
            storyboard_request.get("performance_focus", ""),
            storyboard_request.get("relationship_dynamic", ""),
        ]
    ).lower()
    scores: Dict[str, int] = {key: 0 for key in BOARD_TYPE_KEYWORDS}
    for board_type, keywords in BOARD_TYPE_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text_blob:
                scores[board_type] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "action_progression_board"


def choose_panel_count(board_type: str, requested_count: Optional[int]) -> int:
    if requested_count:
        return max(4, min(int(requested_count), 12))
    return 8


def choose_shot_count(board_type: str, requested_count: Optional[int]) -> int:
    if requested_count:
        return max(4, min(int(requested_count), 12))
    defaults = {
        "multi_shot_board": 8,
        "continuous_shot_board": 8,
        "action_progression_board": 8,
        "spatial_establishing_board": 6,
        "transition_board": 8,
        "emotion_performance_board": 6,
        "product_interaction_board": 6,
    }
    return defaults.get(board_type, 8)


def derive_subject_label(asset_lock_map: Dict[str, Any]) -> str:
    for asset in asset_lock_map.get("assets", []):
        if asset.get("resolved_role") == "Character":
            return asset.get("asset_id") or "角色主体"
    for asset in asset_lock_map.get("assets", []):
        if asset.get("resolved_role") == "Product":
            return asset.get("asset_id") or "产品主体"
    return "主体"


def markdown_bullet_list(items: List[str], fallback: str = "无") -> str:
    if not items:
        return f"- {fallback}"
    return "\n".join(f"- {item}" for item in items)
