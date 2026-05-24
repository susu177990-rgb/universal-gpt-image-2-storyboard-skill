from typing import Any, Dict, List, Tuple

from classify_asset_roles import build_asset_lock_map


InferenceSource = str


def _assets_by_role(asset_lock_map: Dict[str, Any], role: str) -> List[Dict[str, Any]]:
    return [asset for asset in asset_lock_map.get("assets", []) if asset.get("resolved_role") == role]


def infer_main_action(story_framework: str, explicit: str = "") -> Tuple[str, bool, InferenceSource]:
    explicit = (explicit or "").strip()
    story = (story_framework or "").strip()
    if explicit:
        return explicit, False, "user_input"
    if story:
        return story, True, "story_framework"
    return "", True, "missing"


def infer_scene_description(story_framework: str, explicit: str, asset_lock_map: Dict[str, Any]) -> Tuple[str, bool, InferenceSource]:
    explicit = (explicit or "").strip()
    if explicit:
        return explicit, False, "user_input"

    scene_assets = _assets_by_role(asset_lock_map, "Scene")
    if scene_assets:
        parts = []
        for asset in scene_assets:
            anchors = asset.get("anchors", {})
            description = asset.get("description", "").strip()
            environment = "、".join(anchors.get("environment_anchors", []))
            lighting = "、".join(anchors.get("lighting_anchors", []))
            merged = "；".join(item for item in [description, environment, lighting] if item)
            if merged:
                parts.append(f"{asset.get('asset_id')}：{merged}")
        if parts:
            return f"依据场景素材推断空间与环境：{' | '.join(parts)}", True, "scene_assets"

    story = (story_framework or "").strip()
    if story:
        return f"未填写场景描述，依据核心故事「{story}」推断空间层次、时间气质与主要光线。", True, "director_inference"
    return "未填写场景描述，需由导演规划补足空间与光线。", True, "director_inference"


def infer_performance_focus(story_framework: str, explicit: str, asset_lock_map: Dict[str, Any]) -> Tuple[str, bool, InferenceSource]:
    explicit = (explicit or "").strip()
    if explicit:
        return explicit, False, "user_input"

    character_assets = _assets_by_role(asset_lock_map, "Character")
    product_assets = _assets_by_role(asset_lock_map, "Product")
    cues: List[str] = []

    if character_assets:
        for asset in character_assets[:2]:
            anchors = asset.get("anchors", {})
            performances = "、".join(anchors.get("performance_anchors", []))
            if performances:
                cues.append(f"{asset.get('asset_id')} 的表演重点：{performances}")
    if product_assets:
        cues.append("产品镜头要突出接触、观察、展示与人物反应。")

    if cues:
        story = (story_framework or "").strip()
        suffix = f" 并服务故事「{story}」" if story else ""
        return "；".join(cues) + suffix, True, "asset_roles"

    story = (story_framework or "").strip()
    if story:
        return f"未填写表演重点，依据核心故事「{story}」推断情绪、肢体与节奏重点。", True, "director_inference"
    return "突出表情、动作和节奏拍点。", True, "director_inference"


def infer_relationship_dynamic(story_framework: str, explicit: str) -> Tuple[str, bool, InferenceSource]:
    explicit = (explicit or "").strip()
    if explicit:
        return explicit, False, "user_input"

    story = (story_framework or "").strip()
    if any(token in story for token in ["情侣", "恋人", "夫妻"]):
        return "亲密关系中的轻微拉扯与默契互动", True, "story_framework"
    if any(token in story for token in ["争吵", "对峙", "冲突", "审讯"]):
        return "张力明确的对抗关系", True, "story_framework"
    if any(token in story for token in ["讨论", "聊天", "对话"]):
        return "带有生活感的互动关系", True, "story_framework"
    return "根据核心故事推断人物关系张力", True, "director_inference"


def infer_tone_keywords(story_framework: str, explicit: str, asset_lock_map: Dict[str, Any]) -> Tuple[str, bool, InferenceSource]:
    explicit = (explicit or "").strip()
    if explicit:
        return explicit, False, "user_input"

    style_assets = _assets_by_role(asset_lock_map, "Style")
    if style_assets:
        style_bits = []
        for asset in style_assets[:2]:
            anchors = asset.get("anchors", {})
            style_bits.extend(anchors.get("style_anchors", []))
        if style_bits:
            return "、".join(style_bits[:4]), True, "style_assets"

    story = (story_framework or "").strip()
    if any(token in story for token in ["喜剧", "轻松", "斗嘴", "日常"]):
        return "温暖、生活化、轻喜剧、真实互动", True, "story_framework"
    if any(token in story for token in ["恐怖", "镜中恶魔", "惊悚"]):
        return "压抑、诡异、低照度、慢热不安", True, "story_framework"
    return "电影化、真实、情绪明确、节奏可读", True, "director_inference"


def infer_production_context(story_framework: str, explicit: str) -> Tuple[str, bool, InferenceSource]:
    explicit = (explicit or "").strip()
    if explicit:
        return explicit, False, "user_input"

    story = (story_framework or "").strip()
    if "广告" in story or "产品" in story:
        return "广告", True, "story_framework"
    if "情景喜剧" in story or "斗嘴" in story:
        return "情景喜剧", True, "story_framework"
    return "短片", True, "director_inference"


def enrich_storyboard_request(storyboard_request: Dict[str, Any], asset_lock_map: Dict[str, Any], raw_story_request: Dict[str, Any] | None = None) -> Dict[str, Any]:
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
    performance_focus, performance_inferred, performance_source = infer_performance_focus(
        story_framework,
        raw_story_request.get("performance_focus", storyboard_request.get("performance_focus", "")),
        asset_lock_map,
    )
    relationship_dynamic, relationship_inferred, relationship_source = infer_relationship_dynamic(
        story_framework,
        raw_story_request.get("relationship_dynamic", storyboard_request.get("relationship_dynamic", "")),
    )
    tone_keywords, tone_inferred, tone_source = infer_tone_keywords(
        story_framework,
        raw_story_request.get("tone_keywords", storyboard_request.get("tone_keywords", "")),
        asset_lock_map,
    )
    production_context, context_inferred, context_source = infer_production_context(
        story_framework,
        raw_story_request.get("production_context", storyboard_request.get("production_context", "")),
    )

    assumptions = list(storyboard_request.get("assumptions", []))
    if main_inferred:
        assumptions.append("未单独填写主动作，默认与核心故事一体处理。")
    if scene_inferred:
        assumptions.append("未填写场景描述，已依据场景素材或导演推断补足空间信息。")
    if performance_inferred:
        assumptions.append("未填写表演重点，已依据角色素材与故事推断表演方向。")
    if relationship_inferred:
        assumptions.append("未填写人物关系，已依据故事内容推断互动张力。")
    if tone_inferred:
        assumptions.append("未填写基调关键词，已依据风格素材或故事自动推断。")
    if context_inferred:
        assumptions.append("未填写制作语境，已按故事内容自动归类。")

    return {
        **storyboard_request,
        "main_action": main_action,
        "scene_description": scene_description,
        "performance_focus": performance_focus,
        "relationship_dynamic": relationship_dynamic,
        "tone_keywords": tone_keywords,
        "production_context": production_context,
        "inferred_fields": {
            "main_action": {"inferred": main_inferred, "source": main_source},
            "scene_description": {"inferred": scene_inferred, "source": scene_source},
            "performance_focus": {"inferred": performance_inferred, "source": performance_source},
            "relationship_dynamic": {"inferred": relationship_inferred, "source": relationship_source},
            "tone_keywords": {"inferred": tone_inferred, "source": tone_source},
            "production_context": {"inferred": context_inferred, "source": context_source},
        },
        "assumptions": assumptions,
    }


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
