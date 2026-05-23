from pipeline_common import dump_json, load_input, normalize_input_mode, normalize_output_purpose, resolve_assets


def validate_payload(input_data):
    project_info = input_data.get("project_info", {})
    story_request = input_data.get("story_request", {})
    assets = resolve_assets(input_data)

    missing = []
    blockers = []
    risk_points = []

    input_mode = normalize_input_mode(project_info.get("input_mode")) or "mixed"

    if not project_info.get("input_mode"):
        missing.append("project_info.input_mode")
    if not normalize_output_purpose(project_info.get("output_purpose")):
        missing.append("project_info.output_purpose")

    story_framework = story_request.get("story_framework", "").strip()
    if not story_framework:
        missing.append("story_request.story_framework")
        blockers.append("缺少核心故事，无法判断这一段要拍什么。")

    if input_mode in {"asset_driven", "mixed"} and not assets:
        missing.append("provided_assets")
        blockers.append("当前为素材与文本混合模式，请至少上传 1 张参考图。")

    if input_mode == "text_only" and not assets and len(story_framework) < 8:
        risk_points.append("纯文本模式且故事描述较短，导演规划将更多依赖自动推断。")

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
