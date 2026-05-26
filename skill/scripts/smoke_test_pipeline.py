import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PIPELINE = ROOT / "run_storyboard_pipeline.py"


CASES = [
    {
        "name": "sitcom_preproduction_board",
        "payload": {
            "project_info": {
                "input_mode": "素材与文本混合",
                "output_purpose": "带文字导演故事板"
            },
            "story_request": {
                "story_framework": "一对情侣坐在沙发上讨论晚饭吃什么，最后发展成轻松斗嘴和一起大笑。",
                "scene_description": "夜晚现代公寓客厅，暖黄室内灯光，沙发和茶几上有零食。",
                "relationship_dynamic": "情侣式斗嘴，真实生活化互动。",
                "tone_keywords": "cozy, warm, sitcom realism, romantic comedy",
                "production_context": "情景喜剧"
            },
            "provided_assets": [
                {
                    "asset_id": "guy_ref",
                    "role_tag": "角色",
                    "asset_url": "https://example.com/guy.png",
                    "description": "年轻男性，居家服，表情丰富",
                    "must_keep": "发型, 脸型, 居家穿搭"
                },
                {
                    "asset_id": "girl_ref",
                    "role_tag": "角色",
                    "asset_url": "https://example.com/girl.png",
                    "description": "年轻女性，情绪表达明显",
                    "must_keep": "发型, 脸型, 居家穿搭"
                },
                {
                    "asset_id": "living_room_ref",
                    "role_tag": "场景",
                    "asset_url": "https://example.com/room.png",
                    "description": "现代公寓客厅，夜景窗户，暖黄台灯",
                    "must_keep": "沙发, 茶几, 暖黄色灯光, 夜景窗户"
                }
            ],
            "optional_parameters": {
                "aspect_ratio": "16:9 横屏",
                "image_quality": "2K 高清",
                "shot_count_hint": 8,
                "style_goal": "电影写实",
                "board_density": "信息丰富",
                "render_detail_level": "高",
                "inference_tolerance": "强"
            }
        }
    },
    {
        "name": "text_only_transition_board",
        "payload": {
            "project_info": {
                "input_mode": "纯文本创作",
                "output_purpose": "无文字分镜宫格图"
            },
            "story_request": {
                "story_framework": "女孩触摸镜子，镜中倒影逐步变成恶魔。",
                "production_context": "短片"
            },
            "provided_assets": [],
            "optional_parameters": {
                "board_type_hint": "转场",
                "aspect_ratio": "9:16 竖屏",
                "image_quality": "2K 高清"
            }
        }
    }
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
    assert "preproduction_board_plan" in payload
    assert "master_prompt_markdown" in payload
    assert payload["image_generation_status"] == "awaiting_confirmation"
    assert payload["confirmation_action"]["label"] == "确认生图"
    assert "generated_image_url" in payload
    assert payload["generated_image_url"] is None
    assert payload["image_error"] is None
    assert payload["master_prompt_markdown"].startswith("# ")
    assert payload["preproduction_board_plan"]["shot_list"]
    assert payload["preproduction_board_plan"]["concept_block"]
    assert payload["preproduction_board_plan"]["blocking_plan"]
    assert payload["preproduction_board_plan"]["lighting_and_sound"]
    assert payload["storyboard_request"]["performance_focus"]
    assert payload["storyboard_request"]["relationship_dynamic"]
    assert payload["storyboard_request"]["tone_keywords"]


def main():
    for case in CASES:
        run_case(case)
    print("smoke_ok")


if __name__ == "__main__":
    main()
