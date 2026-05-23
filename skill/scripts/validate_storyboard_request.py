from pipeline_common import dump_json, load_input, normalize_input_mode, normalize_output_purpose


def validate_payload(input_data):
    project_info = input_data.get("project_info", {})
    story_request = input_data.get("story_request", {})
    assets = input_data.get("provided_assets", [])

    missing = []
    blockers = []
    risk_points = []

    input_mode = normalize_input_mode(project_info.get("input_mode")) or "mixed"

    if not project_info.get("input_mode"):
        missing.append("project_info.input_mode")
    if not normalize_output_purpose(project_info.get("output_purpose")):
        missing.append("project_info.output_purpose")

    if not story_request.get("story_framework", "").strip():
        missing.append("story_request.story_framework")
        blockers.append("缺少核心故事，无法判断这一段到底要拍什么。")
    if not story_request.get("main_action", "").strip():
        missing.append("story_request.main_action")
        blockers.append("缺少主动作，无法拆分导演层面的动作推进。")
    if not story_request.get("scene_description", "").strip():
        missing.append("story_request.scene_description")
        blockers.append("缺少场景描述，无法建立空间关系。")

    if input_mode in {"asset_driven", "mixed"} and not assets:
        missing.append("provided_assets")
        blockers.append("当前为素材与文本混合模式，请至少上传 1 张参考图。")

    if input_mode == "text_only" and not story_request.get("visual_goal", "").strip():
        risk_points.append("纯文本模式未提供视觉目标，将更多依赖故事描述自动推断画面重点。")
    elif not story_request.get("visual_goal", "").strip():
        risk_points.append("未提供视觉目标，系统将更多依赖故事描述与素材推断重点。")

    return {
        "is_ready": len(blockers) == 0,
        "missing_required_info": missing,
        "potential_blockers": blockers,
        "risk_points": risk_points,
        "recommended_next_action": "continue" if len(blockers) == 0 else "ask_missing_info",
    }


def main():
    input_data = load_input()
    dump_json(validate_payload(input_data))


if __name__ == "__main__":
    main()
