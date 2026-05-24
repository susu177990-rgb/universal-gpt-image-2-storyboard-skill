from pipeline_common import ROLE_META, dump_json, load_input, resolve_assets, split_terms


def build_asset_lock_map(assets):
    mapped_assets = []
    role_summary = {}

    for asset in assets:
        role = asset["resolved_role"]
        meta = ROLE_META.get(role, ROLE_META["Prop"])
        must_keep = split_terms(asset.get("must_keep")) or meta["must_keep_defaults"]
        must_avoid = split_terms(asset.get("must_avoid")) or meta["must_avoid_defaults"]

        mapped = {
            "asset_id": asset.get("asset_id") or "未命名素材",
            "asset_url": asset.get("asset_url"),
            "resolved_role": role,
            "priority": meta["priority"],
            "description": asset.get("description", "").strip(),
            "must_keep": must_keep,
            "must_avoid": must_avoid,
            "positive_constraints": [f"{meta['positive_prefix']}：{item}" for item in must_keep],
            "negative_constraints": [f"{meta['negative_prefix']}：{item}" for item in must_avoid],
            "anchors": {
                "identity_anchors": list(meta.get("identity_defaults", [])),
                "performance_anchors": list(meta.get("performance_defaults", [])),
                "environment_anchors": list(meta.get("environment_defaults", [])),
                "lighting_anchors": list(meta.get("lighting_defaults", [])),
                "prop_anchors": list(meta.get("prop_defaults", [])),
                "style_anchors": list(meta.get("style_defaults", [])),
            },
        }
        mapped_assets.append(mapped)
        role_summary[role] = role_summary.get(role, 0) + 1

    mapped_assets.sort(key=lambda item: item["priority"], reverse=True)
    return {
        "priority_order": [
            "PreviousFrame",
            "Character",
            "Scene",
            "Product",
            "Prop",
            "Costume",
            "Motion",
            "Lighting",
            "Layout",
            "Style",
        ],
        "assets": mapped_assets,
        "role_summary": role_summary,
    }


def main():
    payload = load_input()
    assets = resolve_assets(payload)
    dump_json({"asset_lock_map": build_asset_lock_map(assets)})


if __name__ == "__main__":
    main()
