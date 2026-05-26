from classify_asset_roles import build_asset_lock_map
from compress_user_brief import build_storyboard_request
from infer_story_fields import enrich_storyboard_request
from pipeline_common import dump_json, load_input, resolve_assets
from plan_preproduction_board import build_preproduction_board_plan
from render_storyboard_output import (
    render_asset_section,
    render_board_plan_section,
    render_prompt_body,
    render_request_section,
)
from validate_storyboard_request import validate_payload


def main() -> None:
    payload = load_input()
    validation = validate_payload(payload)
    storyboard_request = build_storyboard_request(payload)
    asset_lock_map = build_asset_lock_map(resolve_assets(payload))
    storyboard_request = enrich_storyboard_request(
        storyboard_request,
        asset_lock_map,
        payload.get("story_request", {}),
    )
    preproduction_board_plan = build_preproduction_board_plan(storyboard_request, asset_lock_map)
    generation_mode = storyboard_request.get("generation_mode", "await_confirmation")
    generation_confirmed = generation_mode == "generate_image"
    image_generation_status = "awaiting_confirmation"
    if generation_confirmed:
        image_generation_status = "failed" if payload.get("image_error") else "ready"
    master_prompt_markdown = "\n".join(
        [
            f"# {storyboard_request.get('title') or '未命名预制作导演板'}",
            "",
            render_request_section(storyboard_request),
            "",
            render_asset_section(asset_lock_map),
            "",
            render_board_plan_section(preproduction_board_plan),
            "",
            "## 最终渲染提示词",
            "",
            "```text",
            render_prompt_body(storyboard_request, asset_lock_map, preproduction_board_plan),
            "```",
        ]
    )

    dump_json(
        {
            "validation": validation,
            "storyboard_request": storyboard_request,
            "asset_lock_map": asset_lock_map,
            "preproduction_board_plan": preproduction_board_plan,
            "master_prompt_markdown": master_prompt_markdown,
            "image_generation_status": image_generation_status,
            "confirmation_action": None
            if generation_confirmed
            else {
                "label": "确认生图",
                "generation_mode": "generate_image",
                "uses_prompt_field": "master_prompt_markdown",
            },
            "generated_image_url": payload.get("generated_image_url") if generation_confirmed else None,
            "image_error": payload.get("image_error") if generation_confirmed else None,
        }
    )


if __name__ == "__main__":
    main()
