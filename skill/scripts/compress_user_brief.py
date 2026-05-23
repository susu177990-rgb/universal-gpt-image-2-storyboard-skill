from pipeline_common import (
    build_title,
    dump_json,
    load_input,
    normalize_aspect_ratio,
    normalize_board_type_hint,
    normalize_camera_preference,
    normalize_image_quality,
    normalize_input_mode,
    normalize_output_purpose,
)


def build_storyboard_request(payload):
    project_info = payload.get("project_info", {})
    story_request = payload.get("story_request", {})
    optional_parameters = payload.get("optional_parameters", {})
    assumptions = []

    story_framework = story_request.get("story_framework", "").strip()
    if not optional_parameters.get("aspect_ratio"):
        assumptions.append("未指定画幅比例，默认使用 16:9。")
    if not optional_parameters.get("image_quality"):
        assumptions.append("未指定输出画质，默认使用 2K。")
    if not optional_parameters.get("board_type_hint"):
        assumptions.append("未指定分镜类型偏好，将根据故事与素材自动判断。")
    camera_pref = normalize_camera_preference(optional_parameters.get("camera_movement_preference"))
    if not camera_pref:
        assumptions.append("未指定机位偏好，将根据分镜类型自动选择机位策略。")

    return {
        "title": build_title(story_framework, project_info.get("title")),
        "input_mode": normalize_input_mode(project_info.get("input_mode")) or "mixed",
        "output_purpose": normalize_output_purpose(project_info.get("output_purpose")) or "review_or_pitch",
        "generation_mode": "generate_image",
        "output_language": "zh-CN",
        "story_framework": story_framework,
        "main_action": story_request.get("main_action", "").strip(),
        "scene_description": story_request.get("scene_description", "").strip(),
        "visual_goal": story_request.get("visual_goal", "").strip(),
        "aspect_ratio": normalize_aspect_ratio(optional_parameters.get("aspect_ratio")),
        "image_quality": normalize_image_quality(optional_parameters.get("image_quality")),
        "board_type_hint": normalize_board_type_hint(optional_parameters.get("board_type_hint")),
        "panel_count_hint": optional_parameters.get("panel_count_hint"),
        "duration_hint_seconds": optional_parameters.get("duration_hint_seconds"),
        "camera_movement_preference": camera_pref,
        "style_goal": optional_parameters.get("style_goal", "").strip(),
        "allow_minor_inference": optional_parameters.get("allow_minor_inference", True),
        "assumptions": assumptions,
    }


def main():
    payload = load_input()
    dump_json({"storyboard_request": build_storyboard_request(payload)})


if __name__ == "__main__":
    main()
