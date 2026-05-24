from pipeline_common import dump_json, load_input, normalize_input_mode, normalize_output_purpose, resolve_assets


def validate_payload(input_data):
    project_info = input_data.get("project_info", {})
    story_request = input_data.get("story_request", {})
    assets = resolve_assets(input_data)

    missing = []
    blockers = []
    risk_points = []

    input_mode = normalize_input_mode(project_info.get("input_mode")) or "mixed"
    output_purpose = normalize_output_purpose(project_info.get("output_purpose"))

    if not project_info.get("input_mode"):
        missing.append("project_info.input_mode")
    if not output_purpose:
        missing.append("project_info.output_purpose")
        blockers.append("缺少输出形态，无法确定是完整导演板还是纯图参考板。")

    story_framework = story_request.get("story_framework", "").strip()
    if not story_framework:
        missing.append("story_request.story_framework")
        blockers.append("缺少核心故事，无法进行导演推断。")

    if input_mode in {"asset_driven", "mixed"} and not assets:
        missing.append("provided_assets")
        blockers.append("当前是素材与文本混合模式，请至少提供一项素材。")

    if not story_request.get("performance_focus", "").strip():
        risk_points.append("未填写表演重点，将由系统强推断。")
    if not story_request.get("relationship_dynamic", "").strip():
        risk_points.append("未填写人物关系，将由系统强推断互动张力。")
    if not story_request.get("tone_keywords", "").strip():
        risk_points.append("未填写基调关键词，将由系统强推断 tone。")
    if input_mode == "text_only" and not assets:
        risk_points.append("纯文本模式下所有角色、空间与灯光锚点都将由导演推断补足。")

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
