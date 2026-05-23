from typing import Any, Dict, List

from pipeline_common import dump_json, load_input, markdown_bullet_list


def render_asset_section(asset_lock_map: Dict[str, Any]) -> str:
    lines = ["## 素材锁定", ""]
    assets = asset_lock_map.get("assets", [])
    if not assets:
        lines.append("- 本次未提供素材，按纯文本创作处理。")
        return "\n".join(lines)

    for asset in assets:
        lines.append(f"### {asset.get('asset_id') or '未命名素材'}")
        lines.append(f"- 角色：{asset.get('resolved_role')}")
        lines.append(f"- 优先级：{asset.get('priority')}")
        lines.append("- 必须继承：")
        lines.append(markdown_bullet_list(asset.get("must_keep", [])))
        lines.append("- 禁止继承：")
        lines.append(markdown_bullet_list(asset.get("must_avoid", [])))
        lines.append("")
    return "\n".join(lines).rstrip()


def render_plan_section(storyboard_plan: Dict[str, Any]) -> str:
    lines = [
        "## 导演规划摘要",
        "",
        f"- 分镜类型：`{storyboard_plan.get('board_type')}`",
        f"- 类型理由：{storyboard_plan.get('board_type_reason')}",
        f"- 输出形态：`{storyboard_plan.get('output_format')}`",
        f"- 格数：{storyboard_plan.get('panel_count')}",
        f"- 机位策略：{storyboard_plan.get('camera_strategy')}",
        "",
        "### 连续性规则",
        markdown_bullet_list(storyboard_plan.get("continuity_rules", [])),
        "",
        "### 分镜网格规划",
        "",
    ]
    for panel in storyboard_plan.get("panels", []):
        lines.extend(
            [
                f"#### 第 {panel.get('index')} 格",
                f"- 景别：{panel.get('shot_size')}",
                f"- 机位 / 构图：{panel.get('camera')}",
                f"- 主体位置：{panel.get('subject_position')}",
                f"- 动作阶段：{panel.get('action')}",
                f"- 表演重点：{panel.get('performance')}",
                f"- 空间锚点：{panel.get('spatial_anchor')}",
                f"- 导演功能：{panel.get('function')}",
                "",
            ]
        )
    return "\n".join(lines).rstrip()


def render_prompt_body(storyboard_request: Dict[str, Any], asset_lock_map: Dict[str, Any], storyboard_plan: Dict[str, Any]) -> str:
    output_format = storyboard_plan.get("output_format")
    title = storyboard_request.get("title") or "未命名故事板"
    aspect_ratio = storyboard_request.get("aspect_ratio", "16:9")
    panels = storyboard_plan.get("panels", [])
    roles = asset_lock_map.get("assets", [])

    locked_identities = []
    forbidden_inheritance = []
    for asset in roles:
        keep = "、".join(asset.get("must_keep", []))
        avoid = "、".join(asset.get("must_avoid", []))
        locked_identities.append(f"{asset.get('asset_id')} 负责 {asset.get('resolved_role')}，必须继承：{keep or '按该角色职责继承'}")
        forbidden_inheritance.append(f"{asset.get('asset_id')} 禁止继承：{avoid or '按该角色职责排除'}")

    header = [
        f"项目标题：{title}",
        f"输出形态：{output_format}",
        f"画幅比例：每个分镜格内部使用 {aspect_ratio}",
        f"分镜类型：{storyboard_plan.get('board_type')}",
        f"格数：{storyboard_plan.get('panel_count')}",
    ]

    prompt_lines: List[str] = []
    if output_format == "six_zone_pitch_sheet":
        prompt_lines.extend(
            [
                "请生成一张全中文的 6 区故事板提案板。",
                "区 1 为头部信息栏，展示项目标题、分镜类型和核心元信息。",
                "区 2 为素材锁定栏，只展示真正需要锁定的角色、服装、产品或场景锚点。",
                "区 3 为机位与运动规划区，用简洁示意表达摄影机路径和主体运动方向。",
                "区 4 为关键帧辅助区，展示环境、表情或动作力学重点。",
                "区 5 为核心分镜网格，按时间顺序展示连续分镜画面。",
                "区 6 为技术尾栏，概括光照、材质、色彩和关键镜头参数。",
            ]
        )
    else:
        prompt_lines.extend(
            [
                "请生成一张纯净参考板，只包含分镜图像，不包含标题、编号说明框、字幕、参数栏或其他 UI 文本。",
                "画面必须按时间顺序排布，并让图像本身承担叙事信息。",
            ]
        )

    prompt_lines.append("素材锁定规则：")
    prompt_lines.extend(f"- {line}" for line in locked_identities)
    prompt_lines.append("禁止继承规则：")
    prompt_lines.extend(f"- {line}" for line in forbidden_inheritance)
    prompt_lines.append("连续性规则：")
    prompt_lines.extend(f"- {line}" for line in storyboard_plan.get("continuity_rules", []))
    prompt_lines.append("分镜内容：")
    for panel in panels:
        prompt_lines.append(
            f"- 第 {panel.get('index')} 格：{panel.get('shot_size')}，{panel.get('camera')}，"
            f"{panel.get('subject_position')}，动作为“{panel.get('action')}”，"
            f"表演重点为“{panel.get('performance')}”，空间锚点为“{panel.get('spatial_anchor')}”。"
        )
    prompt_lines.append("整体要求：使用具体镜头语言，不使用空泛形容词，保证主体、空间、光线和道具的一致性。")

    return "\n".join(header + [""] + prompt_lines)


def main() -> None:
    payload = load_input()
    storyboard_request = payload.get("storyboard_request", {})
    asset_lock_map = payload.get("asset_lock_map", {})
    storyboard_plan = payload.get("storyboard_plan", {})

    prompt_body = render_prompt_body(storyboard_request, asset_lock_map, storyboard_plan)
    markdown = "\n".join(
        [
            f"# {storyboard_request.get('title') or '未命名故事板'}",
            "",
            f"- 输出形态：`{storyboard_plan.get('output_format')}`",
            f"- 图片执行：`{storyboard_request.get('generation_mode', 'generate_image')}`",
            "",
            render_asset_section(asset_lock_map),
            "",
            render_plan_section(storyboard_plan),
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
    if not generated_image_url and not image_error:
        image_error = {
            "code": "image_not_generated",
            "message": "当前输出已生成 Markdown 提示词，但未附带图片结果。执行器接入后应在此返回图片链接。",
        }

    dump_json(
        {
            "storyboard_request": storyboard_request,
            "asset_lock_map": asset_lock_map,
            "storyboard_plan": storyboard_plan,
            "master_prompt_markdown": markdown,
            "generation_mode": storyboard_request.get("generation_mode", "generate_image"),
            "generated_image_url": generated_image_url,
            "image_error": image_error,
        }
    )


if __name__ == "__main__":
    main()
