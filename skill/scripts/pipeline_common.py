import json
import re
import sys
from typing import Any, Dict, List, Optional


ROLE_META = {
    "Character": {
        "priority": 100,
        "must_keep_defaults": ["人物身份", "脸部特征", "发型", "体型"],
        "must_avoid_defaults": ["背景环境", "无关路人", "场景文字"],
        "positive_prefix": "锁定角色身份",
        "negative_prefix": "禁止继承无关人物或背景",
    },
    "Scene": {
        "priority": 90,
        "must_keep_defaults": ["空间结构", "环境布局", "主要光向"],
        "must_avoid_defaults": ["场景内无关人物身份", "不相关风格污染"],
        "positive_prefix": "锁定场景结构",
        "negative_prefix": "禁止把场景中的人物当主角",
    },
    "Product": {
        "priority": 80,
        "must_keep_defaults": ["产品外形", "比例", "材质", "品牌识别点"],
        "must_avoid_defaults": ["遮挡产品主体", "错误比例"],
        "positive_prefix": "锁定产品识别度",
        "negative_prefix": "禁止产品变形或被遮挡",
    },
    "Prop": {
        "priority": 75,
        "must_keep_defaults": ["道具外形", "尺寸关系", "交互位置"],
        "must_avoid_defaults": ["道具消失", "道具变成角色"],
        "positive_prefix": "锁定道具形态",
        "negative_prefix": "禁止道具串位或消失",
    },
    "Costume": {
        "priority": 70,
        "must_keep_defaults": ["服装版型", "纹样", "材质", "颜色"],
        "must_avoid_defaults": ["模特脸", "模特体型", "模特表情"],
        "positive_prefix": "只锁定服装",
        "negative_prefix": "禁止继承服装模特身份",
    },
    "Motion": {
        "priority": 65,
        "must_keep_defaults": ["动作方向", "重心变化", "关键姿态"],
        "must_avoid_defaults": ["运动参考人物身份", "运动参考背景"],
        "positive_prefix": "锁定动作节奏",
        "negative_prefix": "禁止继承动作参考的身份与背景",
    },
    "Lighting": {
        "priority": 60,
        "must_keep_defaults": ["光向", "色温", "阴影逻辑"],
        "must_avoid_defaults": ["改变场景结构", "覆盖角色身份"],
        "positive_prefix": "锁定光照逻辑",
        "negative_prefix": "禁止光照参考篡改空间结构",
    },
    "Layout": {
        "priority": 55,
        "must_keep_defaults": ["构图关系", "主体排布", "画面重心"],
        "must_avoid_defaults": ["覆盖角色身份", "覆盖场景内容"],
        "positive_prefix": "锁定构图布局",
        "negative_prefix": "禁止布局参考改写角色和场景",
    },
    "Style": {
        "priority": 50,
        "must_keep_defaults": ["色彩倾向", "质感", "媒介风格"],
        "must_avoid_defaults": ["风格图中的人物", "风格图中的具体地点"],
        "positive_prefix": "只提取风格处理",
        "negative_prefix": "禁止继承风格图内容物",
    },
    "PreviousFrame": {
        "priority": 110,
        "must_keep_defaults": ["上一帧角色状态", "机位方向", "道具状态", "光线状态"],
        "must_avoid_defaults": ["无故跳切", "重置角色位置"],
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

ROLE_HINTS = {
    "Character": ["character", "角色", "人物", "人脸", "主角", "演员", "肖像", "face"],
    "Scene": ["scene", "场景", "环境", "房间", "街道", "空间", "内景", "外景", "background"],
    "Prop": ["prop", "道具", "武器", "家具", "物件", "工具", "sword", "gun"],
    "Product": ["product", "产品", "瓶子", "血清", "包装", "logo", "device", "vial"],
    "Costume": ["costume", "服装", "衣服", "盔甲", "穿搭", "outfit", "armor"],
    "Style": ["style", "风格", "调色", "色彩", "质感", "aesthetic", "palette"],
    "Lighting": ["lighting", "光照", "打光", "阴影", "色温", "rim light"],
    "Motion": ["motion", "运动", "动作", "pose", "姿态", "跑", "挥拳", "walk"],
    "PreviousFrame": ["previous", "上一帧", "前一帧", "continuity"],
    "Layout": ["layout", "布局", "构图", "排版", "framing"],
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
    "generate_image": "generate_image",
    "直接执行生图": "generate_image",
}

OUTPUT_LANGUAGE_ALIASES = {
    "zh-CN": "zh-CN",
    "简体中文": "zh-CN",
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
        return "generate_image"
    return GENERATION_MODE_ALIASES.get(str(value).strip(), "generate_image")


def normalize_output_language(value: Optional[str]) -> str:
    if value is None:
        return "zh-CN"
    return OUTPUT_LANGUAGE_ALIASES.get(str(value).strip(), "zh-CN")


def normalize_aspect_ratio(value: Optional[str]) -> str:
    if value is None:
        return "16:9"
    cleaned = str(value).strip()
    return ASPECT_RATIO_ALIASES.get(cleaned, cleaned if cleaned in ASPECT_RATIO_ALIASES.values() else "16:9")


IMAGE_QUALITY_ALIASES = {
    "1K": "1K",
    "2K": "2K",
    "4K": "4K",
    "1k": "1K",
    "2k": "2K",
    "4k": "4K",
    "1K 标准": "1K",
    "2K 高清": "2K",
    "4K 超清": "4K",
    "1080p": "1K",
    "1440p": "2K",
    "2160p": "4K",
}


def normalize_image_quality(value: Optional[str]) -> str:
    if value is None:
        return "2K"
    cleaned = str(value).strip()
    return IMAGE_QUALITY_ALIASES.get(cleaned, cleaned if cleaned in {"1K", "2K", "4K"} else "2K")


def normalize_board_type_hint(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    cleaned = str(value).strip()
    return BOARD_TYPE_MAP.get(cleaned, cleaned)

BOARD_KEYWORDS = {
    "action_progression_board": ["挥拳", "奔跑", "打斗", "动作", "追逐", "跳", "冲刺", "出击", "fight", "run"],
    "spatial_establishing_board": ["空间", "环境", "入口", "外到内", "实验室", "场景介绍", "establish", "location"],
    "transition_board": ["变身", "转场", "变化", "镜中", "before", "after", "transform", "switch"],
    "emotion_performance_board": ["情绪", "表情", "眼神", "哭", "悲伤", "愤怒", "performance", "emotion"],
    "continuous_shot_board": ["一镜到底", "连续", "跟拍", "推镜", "dolly", "tracking"],
    "multi_shot_board": ["对话", "反打", "多机位", "多角度", "shot reverse", "dialogue"],
    "product_interaction_board": ["产品", "拿起", "展示", "观察", "使用", "瓶子", "serum", "product"],
}

PANEL_TEMPLATES = {
    "action_progression_board": [
        ("中景", "平视中景", "画面中央", "起始姿态", "身体蓄势", "主体与出拳方向", "展示动作起点"),
        ("中远景", "轻微侧前方机位", "画面偏左", "蓄力阶段", "肩背紧绷", "角色与镜头距离变化", "展示动作中段"),
        ("近景", "朝镜头推进", "画面中央偏前景", "动作爆发", "表情发力", "拳头与面部前后层次", "展示动作高点"),
        ("特写", "极近距离正前方", "前景占满", "冲击成立", "攻击性表情", "拳头与镜头接触感", "展示稳定尾帧"),
    ],
    "spatial_establishing_board": [
        ("大全景", "高位远景", "环境占主导", "外部建立", "无表演重点", "外部地理锚点", "建立地点"),
        ("远景", "朝入口推进", "画面中央", "进入阈值", "人物作为尺度参照", "入口与内部关系", "建立空间关系"),
        ("全景", "进入内部后的平视镜头", "画面偏中", "内部展开", "主体开始介入空间", "核心结构区", "建立主体位置"),
        ("中景", "聚焦核心区域", "画面重心收拢", "重点揭示", "人物视线或动作引导", "目标区域", "展示机位变化"),
    ],
    "transition_board": [
        ("中景", "稳定机位", "主体居中", "前状态", "正常状态", "转场前的空间基线", "展示动作起点"),
        ("近景", "聚焦触发点", "触发物居中", "触发阶段", "注意力集中", "触发机制", "展示转场中间态"),
        ("近景", "稳定近景", "主体半身", "中间变化", "情绪或形态异常", "变化边界", "展示转场中间态"),
        ("中景", "回到基准构图", "主体与镜中关系稳定", "后状态", "结果确认", "新状态空间关系", "展示稳定尾帧"),
    ],
    "emotion_performance_board": [
        ("近景", "平视近景", "脸部居中", "情绪起点", "中性表情", "面部与背景关系", "展示动作起点"),
        ("特写", "轻微推近", "眼神区域居中", "触发注意", "细微眼神变化", "视线目标", "展示表情变化"),
        ("特写", "稳定特写", "面部偏前景", "情绪积累", "呼吸和肌肉变化", "光线在面部的分布", "展示动作中段"),
        ("特写", "极近距离", "关键表情占主导", "情绪高点", "最强表演瞬间", "眼神与嘴角变化", "展示动作高点"),
    ],
    "continuous_shot_board": [
        ("全景", "起始稳定机位", "主体与空间同现", "起点建立", "动作准备", "空间路径起点", "建立地点"),
        ("中景", "跟拍推进", "主体偏中", "持续运动", "步态或身体转向", "空间路径中段", "展示动作中段"),
        ("中近景", "运动中轻微转向", "主体靠前景", "关键推进", "状态变化出现", "空间节点", "展示机位变化"),
        ("中景", "运动减速或停点", "主体回到画面核心", "收束停点", "情绪或目标确认", "空间终点", "展示稳定尾帧"),
    ],
    "multi_shot_board": [
        ("全景", "建立镜头", "多主体同框", "关系建立", "站位与方向明确", "空间轴线", "建立空间关系"),
        ("中近景", "角色 A 视角", "主体偏左", "A 发言或动作", "A 的情绪重点", "A 相对 B 的位置", "建立主体朝向"),
        ("中近景", "角色 B 反打", "主体偏右", "B 反应或动作", "B 的情绪重点", "B 相对 A 的位置", "展示表情变化"),
        ("特写", "关键细节或反应镜头", "关键物或脸部居中", "收束重点", "情绪或信息落点", "轴线不变", "展示机位变化"),
    ],
    "product_interaction_board": [
        ("中景", "平视建立镜头", "人物与产品同框", "发现产品", "注意力转移到产品", "角色与产品位置关系", "建立空间关系"),
        ("近景", "手部靠近机位", "产品在前景", "接近产品", "手部动作明确", "桌面或支撑面", "展示道具交互"),
        ("特写", "微距或近距离机位", "产品居中", "接触与使用", "细节观察", "产品与手的比例", "展示产品特征"),
        ("特写", "带人物反应的展示镜头", "产品前景、人物背景", "最终展示", "人物反应确认", "产品与人物关系", "展示稳定尾帧"),
    ],
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


def normalize_role(role_tag: Optional[str]) -> Optional[str]:
    if not role_tag:
        return None
    normalized = ROLE_ALIASES.get(str(role_tag).strip().lower())
    if normalized:
        return normalized
    if role_tag in ROLE_META:
        return role_tag
    return None


def split_terms(raw_value: Any) -> List[str]:
    if raw_value is None:
        return []
    if isinstance(raw_value, list):
        values = raw_value
    else:
        values = re.split(r"[，,、；;|\n]+", str(raw_value))
    cleaned = []
    for item in values:
        value = str(item).strip()
        if value and value not in cleaned:
            cleaned.append(value)
    return cleaned


def infer_role_from_text(text: str) -> str:
    lowered = text.lower()
    scores: Dict[str, int] = {role: 0 for role in ROLE_HINTS}
    for role, hints in ROLE_HINTS.items():
        for hint in hints:
            if hint.lower() in lowered:
                scores[role] += 1
    best_role = max(scores, key=scores.get)
    if scores[best_role] == 0:
        return "Style"
    return best_role


def resolve_assets(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, list):
        assets = payload
    elif isinstance(payload, dict):
        assets = payload.get("provided_assets") or payload.get("assets") or []
    else:
        assets = []

    resolved: List[Dict[str, Any]] = []
    for index, asset in enumerate(assets, start=1):
        if isinstance(asset, str):
            asset = {"asset_id": f"asset_{index}", "description": asset}
        role = normalize_role(asset.get("role_tag"))
        text_blob = " ".join(
            [
                str(asset.get("asset_id", "")),
                str(asset.get("description", "")),
                str(asset.get("must_keep", "")),
                str(asset.get("must_avoid", "")),
                str(asset.get("asset_url", "")),
            ]
        )
        if not role:
            role = infer_role_from_text(text_blob)
        resolved.append({**asset, "resolved_role": role})
    return resolved


def build_title(story_framework: str, explicit_title: Optional[str]) -> str:
    if explicit_title and explicit_title.strip():
        return explicit_title.strip()
    clipped = story_framework.strip()
    if not clipped:
        return "未命名故事板"
    return clipped[:24]


def choose_output_format(output_purpose: str) -> str:
    if output_purpose == "model_reference":
        return "clean_reference_board"
    return "six_zone_pitch_sheet"


def choose_board_type(storyboard_request: Dict[str, Any]) -> str:
    hint = normalize_board_type_hint(storyboard_request.get("board_type_hint"))
    if hint in BOARD_TYPE_MAP.values():
        return hint
    if hint in BOARD_TYPE_MAP:
        return BOARD_TYPE_MAP[hint]

    text_blob = " ".join(
        [
            storyboard_request.get("story_framework", ""),
            storyboard_request.get("main_action", ""),
            storyboard_request.get("scene_description", ""),
            storyboard_request.get("visual_goal", ""),
        ]
    ).lower()
    scores: Dict[str, int] = {board_type: 0 for board_type in BOARD_KEYWORDS}
    for board_type, keywords in BOARD_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text_blob:
                scores[board_type] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "action_progression_board"


def choose_panel_count(board_type: str, requested_count: Optional[int]) -> int:
    if requested_count:
        return max(1, min(int(requested_count), 12))
    defaults = {
        "spatial_establishing_board": 4,
        "product_interaction_board": 4,
        "transition_board": 4,
        "emotion_performance_board": 4,
        "continuous_shot_board": 4,
        "multi_shot_board": 4,
        "action_progression_board": 4,
    }
    return defaults.get(board_type, 4)


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
