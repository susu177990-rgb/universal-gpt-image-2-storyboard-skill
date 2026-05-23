from pipeline_common import dump_json, load_input


def validate_payload(input_data):
    project_info = input_data.get("project_info", {})
    story_request = input_data.get("story_request", {})
    assets = input_data.get("provided_assets", [])

    missing = []
    blockers = []
    risk_points = []

    if not project_info.get("input_mode"):
        missing.append("project_info.input_mode")
    if not project_info.get("output_purpose"):
        missing.append("project_info.output_purpose")
    if not project_info.get("generation_mode"):
        missing.append("project_info.generation_mode")

    if not story_request.get("story_framework", "").strip():
        missing.append("story_request.story_framework")
        blockers.append("缺少核心故事，无法判断这一段到底要拍什么。")
    if not story_request.get("main_action", "").strip():
        missing.append("story_request.main_action")
        blockers.append("缺少主动作，无法拆分导演层面的动作推进。")
    if not story_request.get("scene_description", "").strip():
        missing.append("story_request.scene_description")
        blockers.append("缺少场景描述，无法建立空间关系。")

    input_mode = project_info.get("input_mode")
    if input_mode in {"asset_driven", "mixed"} and not assets:
        missing.append("provided_assets")
        blockers.append("当前输入模式依赖素材，但没有提供素材列表。")
    if project_info.get("output_language") not in {"", None, "zh-CN"}:
        risk_points.append("输出语言不是 zh-CN，可能与全中文目标冲突。")
    if project_info.get("generation_mode") != "generate_image":
        risk_points.append("当前 generation_mode 不是 generate_image，将不符合提示词与图片同时输出的要求。")
    if input_mode == "text_only" and not story_request.get("visual_goal", "").strip():
        risk_points.append("纯文本模式未提供视觉目标，将更多依赖自动推断。")

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
