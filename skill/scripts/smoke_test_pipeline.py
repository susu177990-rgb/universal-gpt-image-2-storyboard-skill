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
                "output_purpose": "带文字导演故事板",
            },
            "story_request": {
                "story_framework": "一个武士坐在酒吧里，拿起发光瓶子喝酒。",
                "main_action": "武士拿起瓶子并饮用。",
                "scene_description": "赛博朋克酒吧内部，霓虹反射在金属与木质台面上。",
                "visual_goal": "强调角色身份、产品可见性和酒吧氛围。",
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
        "name": "transition_clean_grid",
        "payload": {
            "project_info": {
                "title": "镜中恶魔",
                "output_purpose": "无文字分镜宫格图",
            },
            "story_request": {
                "story_framework": "女孩触摸镜子，镜中倒影逐步变成恶魔。",
                "main_action": "女孩触发镜中变身。",
                "scene_description": "黑暗浴室，镜前低照度环境。",
                "visual_goal": "强调前状态、触发点、中间态和稳定尾帧。",
            },
            "provided_assets": [
                {
                    "asset_id": "girl_ref",
                    "role_tag": "角色",
                    "asset_url": "https://example.com/girl.png",
                    "description": "女孩正面参考",
                    "must_keep": "脸型, 发型, 服装",
                },
                {
                    "asset_id": "bathroom_ref",
                    "role_tag": "场景",
                    "asset_url": "https://example.com/bathroom.png",
                    "description": "黑暗浴室",
                    "must_keep": "镜子的位置, 低照度环境",
                },
            ],
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


def main():
    for case in CASES:
        run_case(case)
    print("smoke_ok")


if __name__ == "__main__":
    main()
