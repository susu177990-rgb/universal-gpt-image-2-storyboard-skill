import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PIPELINE = ROOT / "run_storyboard_pipeline.py"


CASES = [
    {
        "name": "mixed_assets_review",
        "payload": {
            "project_info": {
                "title": "霓虹武士饮酒",
                "input_mode": "素材与文本混合",
                "output_purpose": "带文字导演故事板",
            },
            "story_request": {
                "story_framework": "一个武士坐在赛博朋克酒吧里，拿起发光瓶子喝酒。",
            },
            "provided_assets": [
                {
                    "asset_id": "face_ref",
                    "role_tag": "角色",
                    "asset_url": "https://example.com/face.png",
                    "description": "武士男性脸部参考",
                    "must_keep": "脸型, 发型",
                },
                {
                    "asset_id": "armor_ref",
                    "role_tag": "服装",
                    "asset_url": "https://example.com/armor.png",
                    "description": "日式盔甲参考",
                    "must_keep": "盔甲纹样, 颜色",
                    "must_avoid": "模特脸",
                },
                {
                    "asset_id": "bottle_ref",
                    "role_tag": "产品",
                    "asset_url": "https://example.com/bottle.png",
                    "description": "发光玻璃瓶",
                    "must_keep": "瓶子造型, 绿色发光",
                },
            ],
            "optional_parameters": {
                "aspect_ratio": "16:9 横屏",
                "allow_minor_inference": True,
            },
        },
    },
    {
        "name": "text_only_clean_grid",
        "payload": {
            "project_info": {
                "title": "镜中恶魔",
                "input_mode": "纯文本创作",
                "output_purpose": "无文字分镜宫格图",
            },
            "story_request": {
                "story_framework": "女孩触摸镜子，镜中倒影逐步变成恶魔。",
            },
            "provided_assets": [],
            "optional_parameters": {
                "board_type_hint": "转场",
                "aspect_ratio": "9:16 竖屏",
            },
        },
    },
]


def run_case(case):
    result = subprocess.run(
        [sys.executable, str(PIPELINE), json.dumps(case["payload"], ensure_ascii=False)],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert "storyboard_request" in payload
    assert "asset_lock_map" in payload
    assert "storyboard_plan" in payload
    assert "master_prompt_markdown" in payload
    assert "generated_image_url" in payload
    assert payload["generation_mode"] == "generate_image"
    assert payload["master_prompt_markdown"].startswith("# ")
    assert payload["storyboard_plan"]["panels"]
    assert payload["storyboard_request"]["main_action"]
    assert payload["storyboard_request"]["scene_description"]
    assert payload["storyboard_request"]["visual_goal"]
    assert "inferred_fields" in payload["storyboard_request"]


def main():
    for case in CASES:
        run_case(case)
    print("smoke_ok")


if __name__ == "__main__":
    main()
