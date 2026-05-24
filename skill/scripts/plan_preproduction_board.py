from typing import Any, Dict, List

from pipeline_common import (
    SHOT_ROLE_LIBRARY,
    choose_board_type,
    choose_output_format,
    choose_shot_count,
    derive_subject_label,
    dump_json,
    load_input,
)


BOARD_REASONS = {
    "action_progression_board": "需求重点在动作节拍与身体发力过程，适合按动作阶段拆出完整导演板。",
    "spatial_establishing_board": "需求重点在环境揭示与空间路径，适合建立明确的空间视觉板。",
    "transition_board": "需求重点在状态变化，必须可视化触发点与中间态。",
    "emotion_performance_board": "需求重点在表情与人物反应，适合以近景与特写组织导演板。",
    "continuous_shot_board": "需求强调连续推进，适合以统一空间和机位逻辑组织导演板。",
    "multi_shot_board": "需求涉及对话、反打或多角度切换，适合完整镜头设计意图表达。",
    "product_interaction_board": "需求重点是产品识别与互动路径，适合商业提案式导演板。",
}


CAMERA_LANGUAGE = {
    "action_progression_board": "由稳定中景逐步压近到动作高点，利用景别推进力量感。",
    "spatial_establishing_board": "从外部客观建立到内部重点区域收拢，强调空间导航性。",
    "transition_board": "以稳定基准构图记录变化，关键时刻局部压近强调转化边界。",
    "emotion_performance_board": "由客观观察进入亲密特写，用微推近捕捉情绪递进。",
    "continuous_shot_board": "保持统一机位逻辑，以连续运动和视线引导形成沉浸感。",
    "multi_shot_board": "建立镜头后用反打、近景和细节切镜组织信息与节奏。",
    "product_interaction_board": "先建立人物与产品关系，再逐步切入交互点和产品特写。",
}


SCENE_RHYTHM = {
    "action_progression_board": "起势建立 -> 动作推进 -> 高点爆发 -> 结果收束",
    "spatial_establishing_board": "外部建立 -> 入口桥接 -> 内部展开 -> 核心揭示",
    "transition_board": "前状态建立 -> 触发发生 -> 中间态加深 -> 新状态稳定",
    "emotion_performance_board": "情绪起点 -> 微反应 -> 情绪推进 -> 表演收束",
    "continuous_shot_board": "空间起点 -> 连续推进 -> 情绪或动作高点 -> 落点停住",
    "multi_shot_board": "关系建立 -> 来回推进 -> 关键反应 -> 情绪或信息收束",
    "product_interaction_board": "发现产品 -> 产生兴趣 -> 接触/使用 -> 展示与反应收束",
}


def build_concept_block(request: Dict[str, Any], board_type: str) -> Dict[str, Any]:
    return {
        "title": request.get("title"),
        "subtitle": request.get("production_context") or "通用电影预制作板",
        "logline": request.get("story_framework"),
        "genre": request.get("production_context") or "通用电影短片",
        "runtime_hint": f"{request.get('duration_hint_seconds') or 30} 秒参考段落",
        "setting": request.get("scene_description"),
        "board_type": board_type,
    }


def build_tone_and_mood(request: Dict[str, Any]) -> Dict[str, Any]:
    tags = [item.strip() for item in str(request.get("tone_keywords") or "").replace("，", ",").split(",") if item.strip()]
    if not tags:
        tags = ["真实生活感", "电影化", "情绪明确", "节奏可读"]
    return {
        "tags": tags,
        "relationship_dynamic": request.get("relationship_dynamic") or "按核心故事推断人物关系张力",
        "performance_focus": request.get("performance_focus"),
        "board_density": request.get("board_density", "high"),
    }


def build_visual_direction(request: Dict[str, Any], asset_lock_map: Dict[str, Any]) -> Dict[str, Any]:
    lighting = []
    style = []
    environment = []
    for asset in asset_lock_map.get("assets", []):
        anchors = asset.get("anchors", {})
        lighting.extend(anchors.get("lighting_anchors", []))
        style.extend(anchors.get("style_anchors", []))
        environment.extend(anchors.get("environment_anchors", []))
    return {
        "aspect_ratio": request.get("aspect_ratio"),
        "image_quality": request.get("image_quality"),
        "style_goal": request.get("style_goal") or "自动推断",
        "lighting_direction": lighting[:4] or ["主光方向清晰", "动机光源真实"],
        "environment_texture": environment[:4] or ["空间层次明确", "生活化细节存在"],
        "style_references": style[:4] or ["色彩与质感跟随故事与素材推断"],
        "render_detail_level": request.get("render_detail_level", "high"),
    }


def build_character_bible(asset_lock_map: Dict[str, Any]) -> List[Dict[str, Any]]:
    characters = []
    for asset in asset_lock_map.get("assets", []):
        if asset.get("resolved_role") not in {"Character", "Costume"}:
            continue
        anchors = asset.get("anchors", {})
        characters.append(
            {
                "asset_id": asset.get("asset_id"),
                "role": asset.get("resolved_role"),
                "identity_anchors": anchors.get("identity_anchors", []),
                "performance_anchors": anchors.get("performance_anchors", []),
                "must_keep": asset.get("must_keep", []),
                "must_avoid": asset.get("must_avoid", []),
            }
        )
    return characters


def build_set_and_environment(asset_lock_map: Dict[str, Any], request: Dict[str, Any]) -> Dict[str, Any]:
    scene_assets = [asset for asset in asset_lock_map.get("assets", []) if asset.get("resolved_role") == "Scene"]
    prop_assets = [
        asset for asset in asset_lock_map.get("assets", []) if asset.get("resolved_role") in {"Prop", "Product", "Layout"}
    ]
    return {
        "scene_summary": request.get("scene_description"),
        "space_zones": [asset.get("asset_id") for asset in scene_assets] or ["按故事推断主要空间功能区"],
        "hero_props": [asset.get("asset_id") for asset in prop_assets] or ["按故事推断关键道具"],
        "livability_notes": ["保持生活化痕迹", "空间要可拍摄且有层次"],
    }


def build_blocking_plan(board_type: str, request: Dict[str, Any], asset_lock_map: Dict[str, Any]) -> Dict[str, Any]:
    subject = derive_subject_label(asset_lock_map)
    return {
        "top_view_logic": f"以 {subject} 为核心组织空间视线与镜头方向，遵守 {board_type} 的基本调度逻辑。",
        "talent_movement": request.get("relationship_dynamic") or "根据故事推断人物相对站位与动线",
        "camera_positions": [f"机位 {i:02d}" for i in range(1, 5)],
        "camera_paths": ["主要机位围绕主体推进", "必要时通过侧向或顶视机位说明空间关系"],
    }


def build_shot_list(board_type: str, shot_count: int, request: Dict[str, Any], asset_lock_map: Dict[str, Any]) -> List[Dict[str, Any]]:
    roles = SHOT_ROLE_LIBRARY.get(board_type, SHOT_ROLE_LIBRARY["action_progression_board"])
    shots = []
    for index in range(shot_count):
        shot_role = roles[min(index, len(roles) - 1)]
        shots.append(
            {
                "shot_id": f"{index + 1:02d}",
                "shot_role": shot_role,
                "shot_size": ["双人远景", "中景", "近景", "特写", "微距", "大全景"][index % 6],
                "camera_angle": ["平视", "轻低角度", "轻高角度", "过肩", "正面", "侧面"][index % 6],
                "camera_motion": request.get("camera_movement_preference") or ["静态", "轻推近", "静态", "手持", "微距停顿", "跟拍"][index % 6],
                "blocking": f"围绕 {derive_subject_label(asset_lock_map)} 组织第 {index + 1} 个镜头的人物站位、视线方向和空间关系。",
                "action_beat": f"第 {index + 1} 个动作节拍，服务于「{request.get('main_action')}」的推进。",
                "performance_beat": f"第 {index + 1} 个表演重点，围绕「{request.get('performance_focus')}」展开。",
                "dialogue_or_voiceover": "—",
                "mood_beat": request.get("tone_keywords") or "按故事节奏推断情绪推进",
                "lighting_note": "保持主光方向与色温连续，必要时用动机光源强化情绪。",
                "why_this_shot_exists": f"该镜头负责{shot_role}，用来推进整体节奏与导演意图。",
            }
        )
    return shots


def build_lighting_and_sound(request: Dict[str, Any], asset_lock_map: Dict[str, Any]) -> Dict[str, Any]:
    lighting = []
    for asset in asset_lock_map.get("assets", []):
        lighting.extend(asset.get("anchors", {}).get("lighting_anchors", []))
    return {
        "lighting_plan": lighting[:5] or ["主光方向清楚", "动机光源真实", "色温统一"],
        "cinematography_notes": [
            request.get("style_goal") or "跟随故事自动推断镜头质感",
            "保持人物肤色与材质层次",
            "避免无意义花哨参数堆砌",
        ],
        "sound_texture": [
            "保留空间环境音",
            "音乐服务情绪与节奏，不抢戏",
            "关键动作或互动应有声音落点",
        ],
    }


def build_risk_controls(board_type: str, asset_lock_map: Dict[str, Any]) -> List[str]:
    controls = [
        "角色身份锚点与服装锚点必须分离，禁止服装模特污染主角身份。",
        "风格素材只影响质感与调色，不得污染场景内容和人物身份。",
        "机位阻挡区、shot list 与场景逻辑必须一致，不能互相打架。",
    ]
    if board_type == "transition_board":
        controls.append("转场镜头必须有中间态，不能直接从前状态跳到后状态。")
    if board_type == "product_interaction_board":
        controls.append("产品在关键镜头中始终可见，交互路径和比例必须稳定。")
    return controls


def build_inferred_fields(request: Dict[str, Any]) -> Dict[str, Any]:
    return request.get("inferred_fields", {})


def build_preproduction_board_plan(request: Dict[str, Any], asset_lock_map: Dict[str, Any]) -> Dict[str, Any]:
    board_type = choose_board_type(request)
    shot_count = choose_shot_count(board_type, request.get("shot_count_hint"))
    return {
        "board_type": board_type,
        "board_type_reason": BOARD_REASONS.get(board_type, "根据当前故事与素材自动选择的板型。"),
        "output_format": choose_output_format(request.get("output_purpose", "review_or_pitch")),
        "concept_block": build_concept_block(request, board_type),
        "tone_and_mood": build_tone_and_mood(request),
        "visual_direction": build_visual_direction(request, asset_lock_map),
        "character_bible": build_character_bible(asset_lock_map),
        "set_and_environment": build_set_and_environment(asset_lock_map, request),
        "blocking_plan": build_blocking_plan(board_type, request, asset_lock_map),
        "shot_list": build_shot_list(board_type, shot_count, request, asset_lock_map),
        "camera_language_summary": CAMERA_LANGUAGE.get(board_type, "镜头语言跟随故事自动组织。"),
        "scene_rhythm_summary": SCENE_RHYTHM.get(board_type, "按故事节奏自动组织段落推进。"),
        "lighting_and_sound": build_lighting_and_sound(request, asset_lock_map),
        "risk_controls": build_risk_controls(board_type, asset_lock_map),
        "inferred_fields": build_inferred_fields(request),
    }


def main():
    payload = load_input()
    request = payload.get("storyboard_request", {})
    asset_lock_map = payload.get("asset_lock_map", {})
    dump_json({"preproduction_board_plan": build_preproduction_board_plan(request, asset_lock_map)})


if __name__ == "__main__":
    main()
