from pipeline_common import dump_json, load_input


def main():
    input_data = load_input()
    shots = input_data.get("shot_list") or input_data.get("preproduction_board_plan", {}).get("shot_list", [])
    board_type = input_data.get("board_type") or input_data.get("preproduction_board_plan", {}).get("board_type", "")

    missing_fields = []
    duplicate_roles = []
    recommendations = []
    seen_roles = []

    for index, shot in enumerate(shots, start=1):
        required_keys = [
            "shot_id",
            "shot_role",
            "shot_size",
            "camera_angle",
            "camera_motion",
            "blocking",
            "action_beat",
            "performance_beat",
            "why_this_shot_exists",
        ]
        for key in required_keys:
            value = shot.get(key)
            if not value or (isinstance(value, str) and not value.strip()):
                missing_fields.append(f"Shot {index:02d} 缺少字段：{key}")

        role = shot.get("shot_role")
        if role:
            seen_roles.append(role)

    if seen_roles.count("建立") > 2:
        duplicate_roles.append("建立类镜头过多，可能导致节奏拖慢。")
    if board_type == "product_interaction_board" and "细节" not in seen_roles:
        recommendations.append("产品交互型导演板建议至少包含一个细节镜头。")
    if board_type == "transition_board" and len(shots) < 4:
        recommendations.append("转场型导演板建议至少 4 个镜头，覆盖前状态、触发、中间态、后状态。")
    if len(shots) < 4:
        recommendations.append("完整预制作导演板通常至少需要 4 个镜头来承载完整节奏。")

    dump_json(
        {
            "coverage_pass": len(missing_fields) == 0 and len(duplicate_roles) == 0,
            "missing_fields": missing_fields,
            "duplicate_or_weak_shots": duplicate_roles,
            "recommendations": recommendations,
            "board_type_detected": board_type or "未识别",
        }
    )


if __name__ == "__main__":
    main()
