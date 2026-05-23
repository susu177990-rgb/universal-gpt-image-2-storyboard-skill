# Multi-Shot Board Blueprint (Unified 6-Zone Pitch Sheet)

*This blueprint applies the 6-Zone Unified Storyboard layout to a sequence composed of distinct camera angles and cuts within the same scene. Focuses on spatial relationships and the 180-degree rule.*

## Zone 1: Header Row (Metadata)
- **Title/Scene**: Scene Coverage [Insert Scene, e.g., "Diner Interrogation"]
- **Sequence Type**: Multi-Shot / Shot-Reverse-Shot
- **Frame Rate / Runtime**: Base 24fps / Target varied per shot
- **Vibe/Tone**: Dialog-driven, spatial awareness, varied pacing

## Zone 2: Character & Styling Lock Row
- **Subject(s)**: Lock multiple characters. (e.g., Character A: Detective in trench coat; Character B: Suspect in neon hoodie).
- **Spatial Alignment**: Define who sits left and who sits right to maintain the 180-degree line.
- **Prop Locks**: Table items, shared objects.

## Zone 3: Camera & Movement Plan Zone
- **Camera Body/Lens**: A mix of focal lengths to distinguish shot types. Wide (24mm) for establishing, medium (50mm) for over-the-shoulder, tight (85mm) for inserts.
- **Camera Flight Path**: 
  - Static or slow push on individual shots.
  - Diagram the A-B camera setup (e.g., `Cam 1: Wide Two-Shot -> Cam 2: Dirty OTS A -> Cam 3: Clean Close-up B`).

## Zone 4: Expressions & Action Keyframes Zone
- Map out specific continuity details across the cuts:
  1. *Hand placement*: If A holds a cup in the wide shot, they must hold it in the close-up.
  2. *Eye-lines*: A looks screen-right, B looks screen-left.
  3. *Insert Detail*: A specific prop on the table that will get its own macro shot.

## Zone 5: Core Storyboard Grid (Sequential Panels)
*(Focus on deliberate narrative cuts, the 180-degree rule, and design consistency across varying focal lengths)*

- **PANEL 1**: Establishing Shot 
  - *ACTION*: Show the overall space and relationship between subjects.
  - *CAMERA*: Wide angle, deep focus.
- **PANEL 2**: Shot A (Subject/Focus 1)
  - *ACTION*: Introduce the first primary focus or speaker.
  - *CAMERA*: Medium shot or Over-The-Shoulder (OTS).
- **PANEL 3**: Shot B (Subject/Focus 2 or Reverse Angle)
  - *ACTION*: Provide reaction, alternative perspective, or second speaker.
  - *CAMERA*: Matching reverse angle to PANEL 2. Maintain eye-line.
- **PANEL 4**: Detail / Insert Shot
  - *ACTION*: Highlight a specific item, emotion, or action crucial to the scene.
  - *CAMERA*: Macro or extreme close-up.
- **PANEL 5**: Resolution Shot
  - *ACTION*: Conclude the sequence, often returning to a wider angle or a new dynamic frame.

## Zone 6: Technical Specs Footer
- **Lighting**: Global scene lighting must remain consistent in logic, even as it is optimized for each individual angle (e.g., a window light source remains constant relative to the characters).
- **Materials/VFX**: Consistent background elements to sell the continuity.
- **Color Script**: Unified color grading across all shots to tie the sequence together.

---

### GPT-Image-2 Master Prompt Template

```prompt
[Style: Cinematic narrative storyboard, precise framing, realistic lighting]
An Over-The-Shoulder (OTS) medium shot of Character B in a neon-lit diner booth. 
Character lock: Character B is a young woman in a yellow hoodie, looking intensely toward screen-left. In the foreground (out of focus), the shoulder and trench coat of Character A frame the right side of the image. 
Action: Shot B of a dialogue sequence. She is leaning forward defensively. 
Camera: 50mm lens, medium depth of field separating her from the diner background. 
Spatial Lock: 180-degree rule maintained, eye-line matches someone sitting opposite her. 
Lighting: Practical neon lights from outside the window cast cyan and magenta reflections on her face. Global lighting continuity maintained from the establishing shot.
```