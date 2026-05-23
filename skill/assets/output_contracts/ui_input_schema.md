# UI Input Schema (Payload Template)

This is the standard JSON/Markdown payload that the frontend UI must compile and send to the Agent as a single prompt.

```json
{
  "project_info": {
    "title": "String (Optional, default 'Untitled Sequence')",
    "board_type_hint": "String (Optional, e.g., Action, Transition, Establishing, Product. Let Agent decide if empty)"
  },
  "required_inputs": {
    "story_framework": "String (Required. The core action or narrative that must happen in this sequence)",
    "scene_description": "String (Required. Description of the environment, lighting, time of day)"
  },
  "provided_assets": [
    {
      "role_tag": "Enum (Required. Must be one of: Character, Scene, Prop, Costume, Style)",
      "asset_url": "String (URL to the uploaded image)",
      "description": "String (Brief description of what this asset is)"
    }
  ],
  "optional_parameters": {
    "aspect_ratio": "String (e.g., '16:9', '9:16', '1:1')",
    "camera_movement_preference": "String (e.g., 'Static', 'Tracking', 'Pan')"
  }
}
```

## Example Payload Sent by Frontend

```json
{
  "project_info": {
    "title": "Heavy Punch Strike",
    "board_type_hint": "Action Progression"
  },
  "required_inputs": {
    "story_framework": "The fighter throws a heavy punch directly at the camera, completely filling the screen.",
    "scene_description": "Dimly lit boxing ring with a single harsh spotlight shining straight down."
  },
  "provided_assets": [
    {
      "role_tag": "Character",
      "asset_url": "https://example.com/fighter.png",
      "description": "Rugged, determined fighter."
    }
  ],
  "optional_parameters": {
    "aspect_ratio": "16:9",
    "camera_movement_preference": "Locked Camera"
  }
}
```
