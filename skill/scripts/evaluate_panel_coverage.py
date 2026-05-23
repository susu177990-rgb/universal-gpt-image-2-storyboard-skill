from pipeline_common import dump_json, load_input


def main():
    input_data = load_input()
    panels = input_data.get("panels") or input_data.get("storyboard_plan", {}).get("panels", [])
    board_type = input_data.get("board_type") or input_data.get("storyboard_plan", {}).get("board_type", "")

    missing_fields = []
    duplicate_or_weak = []
    recommendations = []
    functions_seen = set()

    for index, panel in enumerate(panels, start=1):
        required_keys = ["shot_size", "camera", "subject_position", "action", "performance", "function"]
        for key in required_keys:
            value = panel.get(key)
            if not value or (isinstance(value, str) and not value.strip()):
                missing_fields.append(f"第 {index} 格缺少字段：{key}")

        function = str(panel.get("function", "")).strip()
        if function in functions_seen:
            duplicate_or_weak.append(f"第 {index} 格与前文重复，导演功能未拉开：{function}")
        if function:
            functions_seen.add(function)

    if len(panels) < 2:
        recommendations.append("当前格数过少，建议至少包含起点与结果两个阶段。")
    if "transition" in str(board_type) and len(panels) < 3:
        recommendations.append("转场型分镜至少应包含前状态、变化中间态和后状态。")
    if "product" in str(board_type) and len(panels) < 3:
        recommendations.append("产品交互型分镜至少应包含发现、接触和展示三个阶段。")

    dump_json(
        {
            "coverage_pass": len(missing_fields) == 0 and len(duplicate_or_weak) == 0,
            "missing_fields": missing_fields,
            "duplicate_or_weak_panels": duplicate_or_weak,
            "recommendations": recommendations,
            "board_type_detected": board_type or "未识别",
        }
    )


if __name__ == "__main__":
    main()
