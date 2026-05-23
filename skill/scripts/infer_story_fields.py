from typing import Any, Dict, List, Tuple

from classify_asset_roles import build_asset_lock_map


InferenceSource = str


def _scene_assets(asset_lock_map: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [asset for asset in asset_lock_map.get("assets", []) if asset.get("resolved_role") == "Scene"]


def _character_assets(asset_lock_map: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [asset for asset in asset_lock_map.get("assets", []) if asset.get("resolved_role") == "Character"]


def infer_main_action(story_framework: str, explicit: str = "") -> Tuple[str, bool, InferenceSource]:
    cleaned_explicit = (explicit or "").strip()
    cleaned_story = (story_framework or "").strip()
    if cleaned_explicit:
        return cleaned_explicit, False, "user_input"
    if cleaned_story:
        return cleaned_story, True, "story_framework"
    return "", True, "missing"


def infer_scene_description(
    story_framework: str,
    explicit: str,
    asset_lock_map: Dict[str, Any],
) -> Tuple[str, bool, InferenceSource]:
    cleaned_explicit = (explicit or "").strip()
    if cleaned_explicit:
        return cleaned_explicit, False, "user_input"

    scene_assets = _scene_assets(asset_lock_map)
    if scene_assets:
        parts: List[str] = []
        for asset in scene_assets:
            chunks = [asset.get("description", "").strip()]
            must_keep = "、".join(asset.get("must_keep", []))
            if must_keep:
                chunks.append(f"必须继承：{must_keep}")
            blob = "，".join(chunk for chunk in chunks if chunk)
            if blob:
                parts.append(f"{asset.get('asset_id')}：{blob}")
        if parts:
            return f"依据场景参考图建立空间与光向：{'；'.join(parts)}", True, "scene_assets"

    cleaned_story = (story_framework or "").strip()
    if cleaned_story:
        return (
            f"未填写场景描述且无场景参考图，依据核心故事「{cleaned_story}」由导演规划推断环境布局、空间关系与主要光向。",
            True,
            "director_inference",
        )
    return "未提供场景信息，需由导演规划补全空间与光向。", True, "director_inference"


def infer_visual_goal(
    story_framework: str,
    explicit: str,
    asset_lock_map: Dict[str, Any],
) -> Tuple[str, bool, InferenceSource]:
    cleaned_explicit = (explicit or "").strip()
    if cleaned_explicit:
        return cleaned_explicit, False, "user_input"

    role_summary = asset_lock_map.get("role_summary", {})
    character_assets = _character_assets(asset_lock_map)
    goals: List[str] = []

    if character_assets:
        identity_bits: List[str] = []
        for asset in character_assets:
            desc = asset.get("description", "").strip()
            if desc:
                identity_bits.append(desc)
            must_keep = "、".join(asset.get("must_keep", []))
            if must_keep:
                identity_bits.append(f"锁定{must_keep}")
        if identity_bits:
            goals.append(f"围绕角色参考保持身份一致（{'；'.join(identity_bits[:2])}）")
        else:
            goals.append("强调角色身份一致与表演可读")

    if role_summary.get("Product"):
        goals.append("强调产品识别度、可见性与交互位置")
    if role_summary.get("Prop"):
        goals.append("强调道具形态稳定与交互关系")
    if role_summary.get("Costume"):
        goals.append("强调服装版型与纹样一致，不继承模特身份")
    if role_summary.get("Style"):
        goals.append("只提取风格色彩与质感，不继承风格图内容物")
    if role_summary.get("Scene") and not _scene_assets(asset_lock_map):
        goals.append("结合场景素材保持空间与光向连续")

    cleaned_story = (story_framework or "").strip()
    if goals:
        story_hint = f"并服务核心故事「{cleaned_story}」" if cleaned_story else ""
        return f"{'；'.join(goals)}{story_hint}", True, "asset_roles"

    if cleaned_story:
        return (
            f"未填写视觉目标，依据核心故事「{cleaned_story}」突出动作推进、表演可读与画面叙事重点。",
            True,
            "director_inference",
        )
    return "突出动作推进与画面叙事重点。", True, "director_inference"


def enrich_storyboard_request(
    storyboard_request: Dict[str, Any],
    asset_lock_map: Dict[str, Any],
    raw_story_request: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    raw_story_request = raw_story_request or {}
    story_framework = storyboard_request.get("story_framework", "")

    main_action, main_inferred, main_source = infer_main_action(
        story_framework,
        raw_story_request.get("main_action", storyboard_request.get("main_action", "")),
    )
    scene_description, scene_inferred, scene_source = infer_scene_description(
        story_framework,
        raw_story_request.get("scene_description", storyboard_request.get("scene_description", "")),
        asset_lock_map,
    )
    visual_goal, visual_inferred, visual_source = infer_visual_goal(
        story_framework,
        raw_story_request.get("visual_goal", storyboard_request.get("visual_goal", "")),
        asset_lock_map,
    )

    assumptions = list(storyboard_request.get("assumptions", []))
    if main_inferred:
        assumptions.append("未单独填写主动作，默认与核心故事一体处理。")
    if scene_inferred:
        if scene_source == "scene_assets":
            assumptions.append("未填写场景描述，已依据场景参考图推断空间与光向。")
        else:
            assumptions.append("未填写场景描述且无场景参考图，已按导演规划推断环境。")
    if visual_inferred:
        if visual_source == "asset_roles":
            assumptions.append("未填写视觉目标，已依据角色/产品等参考图与核心故事推断视觉重点。")
        else:
            assumptions.append("未填写视觉目标，已依据核心故事推断视觉重点。")

    enriched = {
        **storyboard_request,
        "main_action": main_action,
        "scene_description": scene_description,
        "visual_goal": visual_goal,
        "inferred_fields": {
            "main_action": {"inferred": main_inferred, "source": main_source},
            "scene_description": {"inferred": scene_inferred, "source": scene_source},
            "visual_goal": {"inferred": visual_inferred, "source": visual_source},
        },
        "assumptions": assumptions,
    }
    return enriched


def build_asset_lock_map_from_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    from pipeline_common import resolve_assets

    return build_asset_lock_map(resolve_assets(payload))


def main() -> None:
    from compress_user_brief import build_storyboard_request
    from pipeline_common import dump_json, load_input

    payload = load_input()
    storyboard_request = build_storyboard_request(payload)
    asset_lock_map = build_asset_lock_map_from_payload(payload)
    dump_json(
        {
            "storyboard_request": enrich_storyboard_request(
                storyboard_request,
                asset_lock_map,
                payload.get("story_request", {}),
            )
        }
    )


if __name__ == "__main__":
    main()
