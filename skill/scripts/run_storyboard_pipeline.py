from pipeline_common import dump_json, load_input, resolve_assets

from classify_asset_roles import build_asset_lock_map
from compress_user_brief import build_storyboard_request
from infer_story_fields import enrich_storyboard_request
from plan_storyboard import build_continuity_rules, build_panels, build_risk_controls, BOARD_REASONS, CAMERA_DEFAULTS
from pipeline_common import choose_board_type, choose_output_format, choose_panel_count, derive_subject_label
from render_storyboard_output import render_asset_section, render_plan_section, render_prompt_body, render_story_section
from validate_storyboard_request import validate_payload


def main() -> None:
    payload = load_input()
    validation = validate_payload(payload)

    storyboard_request = build_storyboard_request(payload)
    resolved_assets = resolve_assets(payload)
    asset_lock_map = build_asset_lock_map(resolved_assets)
    storyboard_request = enrich_storyboard_request(
        storyboard_request,
        asset_lock_map,
        payload.get("story_request", {}),
    )

    board_type = choose_board_type(storyboard_request)
    output_format = choose_output_format(storyboard_request.get("output_purpose", "review_or_pitch"))
    panel_count = choose_panel_count(board_type, storyboard_request.get("panel_count_hint"))
    subject_label = derive_subject_label(asset_lock_map)

    storyboard_plan = {
        "title": storyboard_request.get("title"),
        "board_type": board_type,
        "board_type_reason": BOARD_REASONS.get(board_type, "根据当前需求自动选择的分镜类型。"),
        "output_format": output_format,
        "panel_count": panel_count,
        "panel_count_reason": f"当前需求适合用 {panel_count} 格表达主要推进，不额外凑格。",
        "camera_strategy": storyboard_request.get("camera_movement_preference") or CAMERA_DEFAULTS.get(board_type),
        "continuity_rules": build_continuity_rules(asset_lock_map, output_format),
        "panels": build_panels(board_type, panel_count, subject_label, storyboard_request.get("scene_description", "")),
        "risk_controls": build_risk_controls(board_type, asset_lock_map),
    }

    prompt_body = render_prompt_body(storyboard_request, asset_lock_map, storyboard_plan)
    master_prompt_markdown = "\n".join(
        [
            f"# {storyboard_request.get('title') or '未命名故事板'}",
            "",
            f"- 输出形态：`{storyboard_plan.get('output_format')}`",
            f"- 图片执行：`{storyboard_request.get('generation_mode', 'generate_image')}`",
            "",
            render_asset_section(asset_lock_map),
            "",
            render_story_section(storyboard_request),
            "",
            render_plan_section(storyboard_plan, storyboard_request),
            "",
            "## 最终渲染提示词",
            "",
            "```text",
            prompt_body,
            "```",
        ]
    )

    generated_image_url = payload.get("generated_image_url")
    image_error = payload.get("image_error")
    if storyboard_request.get("generation_mode") == "generate_image" and not generated_image_url and not image_error:
        image_error = {
            "code": "image_not_generated",
            "message": "已完成提示词和分镜规划，但当前输入没有附带图片结果。接入真实执行器后应在此返回图片链接。",
        }

    dump_json(
        {
            "validation": validation,
            "storyboard_request": storyboard_request,
            "asset_lock_map": asset_lock_map,
            "storyboard_plan": storyboard_plan,
            "master_prompt_markdown": master_prompt_markdown,
            "generation_mode": storyboard_request.get("generation_mode", "generate_image"),
            "generated_image_url": generated_image_url,
            "image_error": image_error,
        }
    )


if __name__ == "__main__":
    main()
