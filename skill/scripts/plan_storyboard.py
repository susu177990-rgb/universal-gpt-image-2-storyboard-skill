import copy
import json
import sys
from typing import Any, Dict, List

from pipeline_common import (
    PANEL_TEMPLATES,
    build_title,
    choose_board_type,
    choose_output_format,
    choose_panel_count,
    derive_subject_label,
    dump_json,
    load_input,
    normalize_input_mode,
    normalize_output_purpose,
    resolve_assets,
)


CAMERA_DEFAULTS = {
    "action_progression_board": "固定主机位，围绕动作爆发方向做近中远景推进。",
    "spatial_establishing_board": "从外到内推进，先建立空间再收拢到核心区域。",
    "transition_board": "以稳定基准构图记录变化，突出触发点和中间态。",
    "emotion_performance_board": "以近景和特写为主，微推近捕捉表情变化。",
    "continuous_shot_board": "保持运动连续，不随意切轴或重置主体位置。",
    "multi_shot_board": "明确轴线与反打关系，用景别变化承载叙事重点。",
    "product_interaction_board": "优先保证产品可见，再安排人物反应与微距细节。",
}

BOARD_REASONS = {
    "action_progression_board": "需求重点在动作节拍和身体发力过程，适合按起手、蓄力、爆发、收尾拆分。",
    "spatial_establishing_board": "需求重点在空间关系和环境揭示，适合从外到内建立地点逻辑。",
    "transition_board": "需求重点在状态变化，必须显示触发点和中间态，避免直接跳变。",
    "emotion_performance_board": "需求重点在表情和微表演，需要用近景和特写拆出情绪递进。",
    "continuous_shot_board": "需求强调连续推进和同一机位逻辑，适合用一镜到底式分镜规划。",
    "multi_shot_board": "需求包含多角度或对话反打，需要用切镜来分配叙事信息。",
    "product_interaction_board": "需求重点是产品或道具的识别与交互，需要确保产品清晰可见。",
}


def build_continuity_rules(asset_lock_map: Dict[str, Any], output_format: str) -> List[str]:
    rules: List[str] = []
    roles = [asset.get("resolved_role") for asset in asset_lock_map.get("assets", [])]
    if "PreviousFrame" in roles:
        rules.append("上一帧连续性优先级最高，角色状态、机位方向、道具状态不得无故重置。")
    if "Character" in roles:
        rules.append("角色身份必须稳定，脸部特征、发型、体型和服装逻辑保持一致。")
    if "Scene" in roles:
        rules.append("场景结构和主要光向保持连续，空间左右关系不得随意翻转。")
    if "Product" in roles or "Prop" in roles:
        rules.append("产品或道具的外形、尺寸和交互点在各格之间保持一致。")
    if output_format == "clean_reference_board":
        rules.append("纯净参考板禁止标题、编号说明框、字幕或其他 UI 文本元素。")
    else:
        rules.append("6 区提案板允许信息分区，但主分镜网格仍必须以画面叙事为核心。")
    if not rules:
        rules.append("主体、空间和动作方向保持基本连续，不无故跳切。")
    return rules


def build_risk_controls(board_type: str, asset_lock_map: Dict[str, Any]) -> List[str]:
    controls = [
        "生成前先核对素材职责，避免把服装图、风格图或场景图中的人物误当主角。",
        "每格必须承担独立导演功能，禁止重复漂亮图。",
    ]
    roles = [asset.get("resolved_role") for asset in asset_lock_map.get("assets", [])]
    if "Style" in roles:
        controls.append("风格素材只提取色彩和质感，不继承其中的具体角色与场景。")
    if "Product" in roles:
        controls.append("产品交互镜头中始终保持产品可见，避免手或身体完全遮挡。")
    if board_type == "transition_board":
        controls.append("转场型分镜必须包含中间态，禁止从前状态直接跳到后状态。")
    return controls


def build_panels(board_type: str, panel_count: int, subject_label: str, scene_description: str) -> List[Dict[str, Any]]:
    template = PANEL_TEMPLATES.get(board_type, PANEL_TEMPLATES["action_progression_board"])
    panels: List[Dict[str, Any]] = []
    while len(panels) < panel_count:
        panels.extend(copy.deepcopy(template))
    panels = panels[:panel_count]

    structured_panels: List[Dict[str, Any]] = []
    for index, raw_panel in enumerate(panels, start=1):
        shot_size, camera, subject_position, action, performance, spatial_anchor, function = raw_panel
        structured_panels.append(
            {
                "index": index,
                "shot_size": shot_size,
                "camera": camera,
                "subject_position": subject_position,
                "action": action,
                "performance": performance,
                "spatial_anchor": spatial_anchor if spatial_anchor else scene_description,
                "function": function,
                "why_this_panel": f"第 {index} 格负责{function}，围绕{subject_label}推进当前段落。",
            }
        )
    return structured_panels


def main() -> None:
    payload = load_input()
    storyboard_request = payload.get("storyboard_request")
    if not storyboard_request:
        project_info = payload.get("project_info", {})
        story_request = payload.get("story_request", {})
        optional_parameters = payload.get("optional_parameters", {})
        storyboard_request = {
            "title": build_title(story_request.get("story_framework", ""), project_info.get("title")),
            "input_mode": normalize_input_mode(project_info.get("input_mode")) or "mixed",
            "output_purpose": normalize_output_purpose(project_info.get("output_purpose")) or "review_or_pitch",
            "generation_mode": "generate_image",
            "output_language": "zh-CN",
            "story_framework": story_request.get("story_framework", ""),
            "main_action": story_request.get("main_action", ""),
            "scene_description": story_request.get("scene_description", ""),
            "visual_goal": story_request.get("visual_goal", ""),
            "aspect_ratio": optional_parameters.get("aspect_ratio", "16:9"),
            "image_quality": optional_parameters.get("image_quality", "2K"),
            "board_type_hint": optional_parameters.get("board_type_hint"),
            "panel_count_hint": optional_parameters.get("panel_count_hint"),
            "duration_hint_seconds": optional_parameters.get("duration_hint_seconds"),
            "camera_movement_preference": optional_parameters.get("camera_movement_preference", ""),
            "style_goal": optional_parameters.get("style_goal", ""),
            "allow_minor_inference": optional_parameters.get("allow_minor_inference", True),
        }

    asset_lock_map = payload.get("asset_lock_map")
    if not asset_lock_map:
        from classify_asset_roles import build_asset_lock_map  # local import for script use

        asset_lock_map = build_asset_lock_map(resolve_assets(payload))

    board_type = choose_board_type(storyboard_request)
    output_format = choose_output_format(storyboard_request.get("output_purpose", "review_or_pitch"))
    panel_count = choose_panel_count(board_type, storyboard_request.get("panel_count_hint"))
    subject_label = derive_subject_label(asset_lock_map)
    camera_strategy = (
        storyboard_request.get("camera_movement_preference")
        or CAMERA_DEFAULTS.get(board_type, "使用稳定且可读的机位策略推进叙事。")
    )
    continuity_rules = build_continuity_rules(asset_lock_map, output_format)
    panels = build_panels(board_type, panel_count, subject_label, storyboard_request.get("scene_description", ""))
    risk_controls = build_risk_controls(board_type, asset_lock_map)

    storyboard_plan = {
        "title": storyboard_request.get("title"),
        "board_type": board_type,
        "board_type_reason": BOARD_REASONS.get(board_type, "根据当前需求自动选择的分镜类型。"),
        "output_format": output_format,
        "panel_count": panel_count,
        "panel_count_reason": f"当前需求适合用 {panel_count} 格表达主要推进，不额外凑格。",
        "camera_strategy": camera_strategy,
        "continuity_rules": continuity_rules,
        "panels": panels,
        "risk_controls": risk_controls,
    }
    dump_json({"storyboard_plan": storyboard_plan})


if __name__ == "__main__":
    main()
