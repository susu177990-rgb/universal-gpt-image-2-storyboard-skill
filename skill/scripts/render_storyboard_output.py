from typing import Any, Dict, List

from pipeline_common import dump_json, load_input, markdown_bullet_list


def render_asset_section(asset_lock_map: Dict[str, Any]) -> str:
    lines = ["## 素材锁定与锚点", ""]
    assets = asset_lock_map.get("assets", [])
    if not assets:
        lines.append("- 本次未提供素材，按纯文本导演推断处理。")
        return "\n".join(lines)

    for asset in assets:
        anchors = asset.get("anchors", {})
        lines.append(f"### {asset.get('asset_id')}")
        lines.append(f"- 角色：{asset.get('resolved_role')}")
        lines.append(f"- 优先级：{asset.get('priority')}")
        lines.append("- 必须继承：")
        lines.append(markdown_bullet_list(asset.get("must_keep", [])))
        lines.append("- 禁止继承：")
        lines.append(markdown_bullet_list(asset.get("must_avoid", [])))
        for label, key in [
            ("身份锚点", "identity_anchors"),
            ("表演锚点", "performance_anchors"),
            ("环境锚点", "environment_anchors"),
            ("光照锚点", "lighting_anchors"),
            ("道具锚点", "prop_anchors"),
            ("风格锚点", "style_anchors"),
        ]:
            values = anchors.get(key, [])
            if values:
                lines.append(f"- {label}：")
                lines.append(markdown_bullet_list(values))
        lines.append("")
    return "\n".join(lines).rstrip()


def render_request_section(request: Dict[str, Any]) -> str:
    inferred = request.get("inferred_fields", {})

    def mark(field: str) -> str:
        meta = inferred.get(field, {})
        return "（推断）" if meta.get("inferred") else "（用户填写）"

    lines = [
        "## 故事与导演输入",
        "",
        f"- 核心故事：{request.get('story_framework')}",
        f"- 主动作 {mark('main_action')}：{request.get('main_action')}",
        f"- 场景描述 {mark('scene_description')}：{request.get('scene_description')}",
        f"- 表演重点 {mark('performance_focus')}：{request.get('performance_focus')}",
        f"- 人物关系 {mark('relationship_dynamic')}：{request.get('relationship_dynamic')}",
        f"- 基调关键词 {mark('tone_keywords')}：{request.get('tone_keywords')}",
        f"- 制作语境 {mark('production_context')}：{request.get('production_context')}",
    ]
    assumptions = request.get("assumptions", [])
    if assumptions:
        lines.extend(["", "### 推断说明", markdown_bullet_list(assumptions)])
    return "\n".join(lines)


def render_board_plan_section(plan: Dict[str, Any]) -> str:
    concept = plan.get("concept_block", {})
    tone = plan.get("tone_and_mood", {})
    visual = plan.get("visual_direction", {})
    blocking = plan.get("blocking_plan", {})
    lighting = plan.get("lighting_and_sound", {})
    lines = [
        "## 预制作导演板摘要",
        "",
        f"- 板型：`{plan.get('board_type')}`",
        f"- 板型理由：{plan.get('board_type_reason')}",
        f"- 输出形态：`{plan.get('output_format')}`",
        "",
        "### 概念区",
        f"- 标题：{concept.get('title')}",
        f"- 副标题：{concept.get('subtitle')}",
        f"- Logline：{concept.get('logline')}",
        f"- 题材：{concept.get('genre')}",
        f"- 时长参考：{concept.get('runtime_hint')}",
        f"- 场景设定：{concept.get('setting')}",
        "",
        "### 情绪与基调",
        f"- 情绪关键词：{', '.join(tone.get('tags', []))}",
        f"- 人物关系：{tone.get('relationship_dynamic')}",
        f"- 表演重心：{tone.get('performance_focus')}",
        "",
        "### 视觉方向",
        f"- 画幅：{visual.get('aspect_ratio')}",
        f"- 画质：{visual.get('image_quality')}",
        f"- 风格目标：{visual.get('style_goal')}",
        f"- 灯光逻辑：{', '.join(visual.get('lighting_direction', []))}",
        f"- 质感方向：{', '.join(visual.get('style_references', []))}",
        "",
        "### 顶视机位与阻挡",
        f"- 顶视逻辑：{blocking.get('top_view_logic')}",
        f"- 人物动线：{blocking.get('talent_movement')}",
        f"- 机位点位：{', '.join(blocking.get('camera_positions', []))}",
        f"- 机位路线：{', '.join(blocking.get('camera_paths', []))}",
        "",
        "### 镜头语言与节奏",
        f"- 镜头语言：{plan.get('camera_language_summary')}",
        f"- 节奏摘要：{plan.get('scene_rhythm_summary')}",
        "",
        "### 灯光与声音",
        f"- 灯光计划：{', '.join(lighting.get('lighting_plan', []))}",
        f"- 摄影说明：{', '.join(lighting.get('cinematography_notes', []))}",
        f"- 声音质感：{', '.join(lighting.get('sound_texture', []))}",
        "",
        "### 风险控制",
        markdown_bullet_list(plan.get("risk_controls", [])),
        "",
        "### Shot List",
        "",
    ]
    for shot in plan.get("shot_list", []):
        lines.extend(
            [
                f"#### Shot {shot.get('shot_id')}",
                f"- 镜头作用：{shot.get('shot_role')}",
                f"- 景别：{shot.get('shot_size')}",
                f"- 角度：{shot.get('camera_angle')}",
                f"- 运镜：{shot.get('camera_motion')}",
                f"- Blocking：{shot.get('blocking')}",
                f"- 动作节拍：{shot.get('action_beat')}",
                f"- 表演节拍：{shot.get('performance_beat')}",
                f"- 台词 / 旁白：{shot.get('dialogue_or_voiceover')}",
                f"- 情绪拍点：{shot.get('mood_beat')}",
                f"- 灯光说明：{shot.get('lighting_note')}",
                f"- 存在理由：{shot.get('why_this_shot_exists')}",
                "",
            ]
        )
    return "\n".join(lines).rstrip()


def render_prompt_body(request: Dict[str, Any], asset_lock_map: Dict[str, Any], plan: Dict[str, Any]) -> str:
    concept = plan.get("concept_block", {})
    tone = plan.get("tone_and_mood", {})
    visual = plan.get("visual_direction", {})
    blocking = plan.get("blocking_plan", {})
    character_bible = plan.get("character_bible", [])
    set_plan = plan.get("set_and_environment", {})
    shot_list = plan.get("shot_list", [])

    lines = [
        "请生成一张完整的电影级导演预制作视觉板（Cinematic Pre-Production Board）。",
        "整体必须像专业影视项目的导演工作板，而不是普通分镜图。",
        f"画幅比例：整板使用 {visual.get('aspect_ratio')} 输出。",
        f"画质：{visual.get('image_quality')}。",
        f"核心故事：{concept.get('logline')}",
        f"题材与上下文：{concept.get('genre')}，{concept.get('subtitle')}",
        f"场景设定：{concept.get('setting')}",
        f"情绪关键词：{', '.join(tone.get('tags', []))}",
        f"人物关系动态：{tone.get('relationship_dynamic')}",
        f"风格目标：{visual.get('style_goal')}",
        "",
        "整板必须至少包含以下大区块：",
        "1. 顶部概念区：标题、logline、tone tags、production notes。",
        "2. 角色参考区：主角色身份、角度、表情、姿态、服装。",
        "3. 场景与美术区：场景主视图、细节参考、生活化道具。",
        "4. 顶视机位阻挡区：top view、机位点位、人物动线、镜头方向。",
        "5. Shot list 主区：按镜头编号组织主要镜头画面。",
        "6. 底部技术与情绪区：灯光计划、摄影说明、色彩脚本、声音设计、mood references。",
        "",
        "角色锁定规则：",
    ]
    for asset in asset_lock_map.get("assets", []):
        lines.append(f"- {asset.get('asset_id')} / {asset.get('resolved_role')} 必须继承：{'、'.join(asset.get('must_keep', []))}")
        lines.append(f"- {asset.get('asset_id')} 禁止继承：{'、'.join(asset.get('must_avoid', []))}")
    lines.extend(
        [
            "",
            "角色参考区重点：",
        ]
    )
    for character in character_bible:
        lines.append(
            f"- {character.get('asset_id')}：身份锚点 { '、'.join(character.get('identity_anchors', [])) }；"
            f"表演锚点 { '、'.join(character.get('performance_anchors', [])) }。"
        )
    lines.extend(
        [
            "",
            "场景与美术区重点：",
            f"- 空间功能区：{'、'.join(set_plan.get('space_zones', []))}",
            f"- 关键道具：{'、'.join(set_plan.get('hero_props', []))}",
            f"- 生活化说明：{'、'.join(set_plan.get('livability_notes', []))}",
            "",
            "顶视机位阻挡区重点：",
            f"- 顶视逻辑：{blocking.get('top_view_logic')}",
            f"- 人物动线：{blocking.get('talent_movement')}",
            f"- 机位点位：{'、'.join(blocking.get('camera_positions', []))}",
            f"- 机位路线：{'、'.join(blocking.get('camera_paths', []))}",
            "",
            "Shot List 区重点：",
        ]
    )
    for shot in shot_list:
        lines.append(
            f"- Shot {shot.get('shot_id')}：{shot.get('shot_role')}；{shot.get('shot_size')}；"
            f"{shot.get('camera_angle')}；{shot.get('camera_motion')}；"
            f"动作“{shot.get('action_beat')}”；表演“{shot.get('performance_beat')}”。"
        )
    lines.extend(
        [
            "",
            "灯光与声音区重点：",
            f"- 灯光计划：{'、'.join(plan.get('lighting_and_sound', {}).get('lighting_plan', []))}",
            f"- 摄影说明：{'、'.join(plan.get('lighting_and_sound', {}).get('cinematography_notes', []))}",
            f"- 声音质感：{'、'.join(plan.get('lighting_and_sound', {}).get('sound_texture', []))}",
            "",
            "整体要求：信息丰富但不杂乱，电影化、专业、分区清晰，真实影视工业感明显。",
            "如果输出为带文字导演故事板，则允许清晰的分区标题和最少量说明文字；如果输出为无文字分镜宫格图，则去掉说明性文字，只保留画面叙事。",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    payload = load_input()
    request = payload.get("storyboard_request", {})
    asset_lock_map = payload.get("asset_lock_map", {})
    plan = payload.get("preproduction_board_plan", {})
    markdown = "\n".join(
        [
            f"# {request.get('title') or '未命名预制作导演板'}",
            "",
            render_request_section(request),
            "",
            render_asset_section(asset_lock_map),
            "",
            render_board_plan_section(plan),
            "",
            "## 最终渲染提示词",
            "",
            "```text",
            render_prompt_body(request, asset_lock_map, plan),
            "```",
        ]
    )

    dump_json(
        {
            "storyboard_request": request,
            "asset_lock_map": asset_lock_map,
            "preproduction_board_plan": plan,
            "master_prompt_markdown": markdown,
            "generated_image_url": payload.get("generated_image_url"),
            "image_error": payload.get("image_error"),
        }
    )


def render_request_section(request: Dict[str, Any]) -> str:
    inferred = request.get("inferred_fields", {})

    def mark(field: str) -> str:
        return "（推断）" if inferred.get(field, {}).get("inferred") else "（用户填写）"

    lines = [
        "## 导演输入摘要",
        "",
        f"- 核心故事：{request.get('story_framework')}",
        f"- 主动作 {mark('main_action')}：{request.get('main_action')}",
        f"- 场景描述 {mark('scene_description')}：{request.get('scene_description')}",
        f"- 表演重点 {mark('performance_focus')}：{request.get('performance_focus')}",
        f"- 人物关系 {mark('relationship_dynamic')}：{request.get('relationship_dynamic')}",
        f"- 基调关键词 {mark('tone_keywords')}：{request.get('tone_keywords')}",
        f"- 制作语境 {mark('production_context')}：{request.get('production_context')}",
    ]
    if request.get("assumptions"):
        lines.extend(["", "### 推断说明", markdown_bullet_list(request.get("assumptions", []))])
    return "\n".join(lines)


if __name__ == "__main__":
    main()
