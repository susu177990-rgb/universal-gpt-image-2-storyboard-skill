from pipeline_common import (
    build_title,
    dump_json,
    load_input,
    normalize_aspect_ratio,
    normalize_board_density,
    normalize_camera_preference,
    normalize_generation_mode,
    normalize_image_quality,
    normalize_inference_tolerance,
    normalize_input_mode,
    normalize_output_purpose,
    normalize_production_context,
    normalize_render_detail_level,
    normalize_style_goal,
)


def build_storyboard_request(payload):
    project_info = payload.get("project_info", {})
    story_request = payload.get("story_request", {})
    optional_parameters = payload.get("optional_parameters", {})

    assumptions = []
    if not story_request.get("scene_description", "").strip():
        assumptions.append("未填写场景描述，将优先从场景素材推断空间结构与时间气质。")
    if not story_request.get("performance_focus", "").strip():
        assumptions.append("未填写表演重点，将结合角色素材与核心故事推断表演方向。")
    if not story_request.get("relationship_dynamic", "").strip():
        assumptions.append("未填写人物关系，将依据故事内容推断互动氛围。")
    if not story_request.get("tone_keywords", "").strip():
        assumptions.append("未填写基调关键词，将依据故事与风格素材推断 tone。")
    if not story_request.get("production_context", "").strip():
        assumptions.append("未填写制作语境，将默认按通用电影短片预制作板处理。")
    if not optional_parameters.get("shot_count_hint"):
        assumptions.append("未指定总镜头数，系统将按故事复杂度自动确定。")

    return {
        "title": build_title(story_request.get("story_framework", ""), project_info.get("title")),
        "input_mode": normalize_input_mode(project_info.get("input_mode")) or "mixed",
        "output_purpose": normalize_output_purpose(project_info.get("output_purpose")) or "review_or_pitch",
        "generation_mode": normalize_generation_mode(project_info.get("generation_mode")),
        "story_framework": story_request.get("story_framework", "").strip(),
        "main_action": story_request.get("main_action", "").strip(),
        "scene_description": story_request.get("scene_description", "").strip(),
        "performance_focus": story_request.get("performance_focus", "").strip(),
        "relationship_dynamic": story_request.get("relationship_dynamic", "").strip(),
        "tone_keywords": story_request.get("tone_keywords", "").strip(),
        "production_context": normalize_production_context(story_request.get("production_context")),
        "aspect_ratio": normalize_aspect_ratio(optional_parameters.get("aspect_ratio")),
        "image_quality": normalize_image_quality(optional_parameters.get("image_quality")),
        "board_type_hint": optional_parameters.get("board_type_hint"),
        "shot_count_hint": optional_parameters.get("shot_count_hint"),
        "panel_count_hint": optional_parameters.get("panel_count_hint"),
        "duration_hint_seconds": optional_parameters.get("duration_hint_seconds"),
        "camera_movement_preference": normalize_camera_preference(optional_parameters.get("camera_movement_preference")),
        "style_goal": normalize_style_goal(optional_parameters.get("style_goal")),
        "board_density": normalize_board_density(optional_parameters.get("board_density")),
        "render_detail_level": normalize_render_detail_level(optional_parameters.get("render_detail_level")),
        "inference_tolerance": normalize_inference_tolerance(optional_parameters.get("inference_tolerance")),
        "allow_minor_inference": optional_parameters.get("allow_minor_inference", True),
        "assumptions": assumptions,
    }


def main():
    payload = load_input()
    dump_json({"storyboard_request": build_storyboard_request(payload)})


if __name__ == "__main__":
    main()
