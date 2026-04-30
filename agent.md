# Agent Handoff Notes

This repository contains a Matplotlib-based kitchen design drawing generator. It is being used interactively with the user to iterate kitchen layout, wall elevations, ceiling/floor views, electrical point placement, and wiring diagrams.

The user wants practical design drawings, not abstract diagrams. Preserve the current style unless explicitly asked to change it.

## Repository State

- Repository path: `/Users/bytedance/kitchen`
- Main script: `/Users/bytedance/kitchen/draw_kitchen_layout.py`
- Generated image directory: `/Users/bytedance/kitchen/output`
- Git remote: `git@github.com:thynics/kitchen.git`
- Branch: `main`
- Latest design/drawing commit before this handoff doc: `013b9c8 Clarify three-conductor wiring diagrams`
- Usual generation command:

```bash
cd /Users/bytedance/kitchen
python3 draw_kitchen_layout.py
```

The script writes all PNG outputs to `/Users/bytedance/kitchen/output`.

## Working Style Expected By User

- The user communicates in Chinese; reply in Chinese.
- The user expects immediate drawing/code changes, not long proposals.
- When showing generated images in the Codex desktop app, use absolute Markdown image paths, for example:

```markdown
![顶部墙三线走线图](/Users/bytedance/kitchen/output/wiring_view_from_south.png)
```

- The user cares about visual correctness. If they say "你自己观察", actually inspect the PNGs with `view_image` before answering.
- The user dislikes unclear or overlapping drawings. If a diagram looks visually ambiguous, fix the drawing rather than explaining it away.
- The user asked that all content be pushed to GitHub. Recent commits have already been pushed; continue pushing meaningful finished changes unless the user says not to.

## Important Editing Rules

- Use `apply_patch` for manual file edits.
- Do not use shell heredocs, `cat > file`, or Python write scripts for normal edits.
- Regenerate images after changing `draw_kitchen_layout.py`.
- Check `git status --short` before and after edits.
- Do not revert unrelated user changes if any appear.
- Commit generated PNGs together with the script changes that produce them.

Recommended workflow:

```bash
cd /Users/bytedance/kitchen
git status --short
# edit draw_kitchen_layout.py with apply_patch
python3 draw_kitchen_layout.py
git status --short
git add draw_kitchen_layout.py output/*.png
git commit -m "<short clear message>"
git push
```

For small documentation-only changes, add and commit the changed docs file only.

## Current Output Files

The generator currently produces these design drawings:

- `output/kitchen_floor_plan.png`
- `output/view_from_south.png`
- `output/view_from_north.png`
- `output/view_from_west.png`
- `output/view_from_east.png`
- `output/view_from_ceiling.png`
- `output/view_from_floor.png`

It also produces these wiring drawings:

- `output/wiring_view_from_south.png`
- `output/wiring_view_from_north.png`
- `output/wiring_view_from_west.png`
- `output/wiring_view_from_east.png`
- `output/wiring_view_from_ceiling.png`
- `output/wiring_view_from_floor.png`

The terminology in the drawings:

- "顶部墙 / 橱柜墙" means the north/top 500 cm wall in the floor plan.
- "底部墙" means the south/bottom 500 cm wall.
- "西墙" means the left 300 cm wall.
- "东墙" means the right 300 cm wall.
- Ceiling/floor views are plan-like horizontal surfaces.

## Core Room Geometry

All drawing units are centimeters.

Room:

- Width east-west: `ROOM_W = 500`
- Depth north-south: `ROOM_H = 300`
- Wall elevation height: `WALL_ELEVATION_H = 300`
- Output resolution: `OUTPUT_DPI = 450`

Top/north kitchen run:

- Counter depth: `COUNTER_DEPTH = 60`
- Counter height: `COUNTER_HEIGHT = 86`
- Top run starts at north wall in plan.
- The top wall counter run is 500 cm wide.

Window on top/north wall:

- Window x position from left/west end: `WINDOW_X = 252`
- Window width: `WINDOW_W = 100`
- Window sill height: `WINDOW_SILL_H = 93`
- Window height: `WINDOW_H = 118`
- Therefore top of window: 211 cm.
- User provided this exact window data and was sensitive about matching it.

Doors:

- Bottom/south wall door:
  - `BOTTOM_DOOR_X = 274`
  - `BOTTOM_DOOR_W = 86`
  - `BOTTOM_DOOR_H = 178`
  - Remaining right wall segment after this door: 140 cm
- Left/west wall door:
  - Door width: 70 cm
  - Door starts 32 cm from the south/bottom edge in west wall elevation
  - `LEFT_DOOR_H = 195`

Dining table:

- Final table size: 140 x 70 cm
- Table height: `TABLE_HEIGHT = 75`
- Current plan position:
  - `TABLE_X = 335`
  - `TABLE_Y = 75`
  - `TABLE_W = 140`
  - `TABLE_D = 70`
- The table is horizontal in plan and pushed toward/right side wall area.
- User previously considered using the large work space and asked about rotating/placing the table. Current accepted version is the table as represented by these constants unless they reopen that design.

## Current Base Cabinet / Appliance Plan

Top/north wall base modules are represented by `TOP_MODULES`.

Key values:

- Sink:
  - `SINK_X = 260`
  - `SINK_W = 80`
- Hob:
  - `HOB_W = 90`
  - `HOB_TO_SINK_GAP = 80`
  - `HOB_X = SINK_X - HOB_TO_SINK_GAP - HOB_W = 90`
- Left covered/hidden section:
  - `LEFT_COVERED_W = 52`
  - User specifically pointed out that the left 90 cm section has a covered/blocked part. Do not remove this.
- Left usable prep width:
  - `LEFT_USABLE_PREP_W = HOB_X - LEFT_COVERED_W = 38`

Current top run modules from west/left to east/right:

- 0-90: left prep zone, but 0-52 is covered/blocked and 52-90 is actual narrow prep.
- 90-180: hob, 90 cm.
- 180-260: prep gap between hob and sink, 80 cm.
- 260-340: sink, 80 cm.
- 340-420: base cabinet, 80 cm.
- 420-500: base cabinet, 80 cm.

Important historical correction:

- User recommended splitting the space right of sink as 160 cm into two 80 cm bases. This is now reflected by `base_right_1` and `base_right_2`.
- Earlier versions had dishwasher/base/pull-out 60/60/40, but that is no longer the current top-run plan.

Fridge/west wall:

- Fridge niche is on west/left wall.
- Plan originally labeled 75D x 90W.
- The wiring/elevation places a fridge outlet at low height H=40-50, not high. User explicitly corrected that fridge socket should be near the floor.

## Current Upper Cabinet Plan

Upper cabinets are represented by `UPPER_MODULES`.

User recommended not doing full-wall upper cabinets. The accepted logic:

- Do not bridge over the window.
- Use "烟机区 + 窗两侧储物区 + 冰箱上方独立桥柜" logic.
- Window cuts the wall; upper cabinets should respect the 100 cm window opening.

Current upper modules from left/west to right/east:

- `pipe_chase`: x=0, width=52, label `封板/包管 52`, hatched.
- `narrow`: x=52, width=38, label `窄吊柜 38`.
- `hood_cabinet`: x=90, width=90, label `烟机柜 90`.
- `left_wall_cabinet`: x=180, width=72, label `吊柜 72`.
- Window zone: x=252 to 352, no upper cabinet.
- `right_wall_cabinet_68`: x=352, width=68, label `吊柜 68`.
- `right_wall_cabinet_80`: x=420, width=80, label `吊柜 80`.

Upper cabinet dimensional constants:

- Upper depth: `UPPER_DEPTH = 35`
- Upper height: `UPPER_HEIGHT = 75`
- Upper bottom height: `UPPER_BOTTOM = COUNTER_HEIGHT + 60 = 146`
- Upper top height: `UPPER_TOP = 221`

The drawing also has bridge cabinet constants:

- `BRIDGE_CABINET_H = 40`
- `BRIDGE_CABINET_BOTTOM = 225`
- `BRIDGE_CABINET_TOP = 265`

## Lighting Plan

The user accepted 8 ceiling downlights:

- Grid: 2 rows x 4 columns
- X coordinates: `CEILING_LIGHT_XS = (70, 190, 310, 430)`
- Y from north/top wall: `CEILING_LIGHT_Y_FROM_NORTH = (80, 215)`

Equivalent plan coordinates in the script:

- `light_ys = [ROOM_H - y for y in CEILING_LIGHT_Y_FROM_NORTH]`
- Therefore rows are at y=220 and y=85 in the script's bottom-origin coordinate system.

Switch:

- There is a single switch.
- It controls all ceiling downlights.
- User corrected switch location: it is on the bottom/south wall, beside the bottom door, not on the west wall.
- Current switch/entry constants:
  - `ENTRY_X = BOTTOM_DOOR_X + BOTTOM_DOOR_W + 18 = 378`
  - `ENTRY_H = 125`
- The total incoming feed enters from the switch location.

## Electrical Point List

The user supplied the final electrical point list. Current drawings should preserve this intent:

1. Oil hood: high three-prong x1.
2. Induction hob / built-in hob: independent high-power circuit x1; socket or junction box depends on device power.
3. Under sink: small water heater x1, RO purifier x1, optional spare x1.
4. Dishwasher: socket x1, placed in adjacent cabinet for accessible unplugging/maintenance.
5. Fridge: three-prong x1, low/side position so it is not fully crushed behind the fridge.
6. Left prep counter: five-hole x2. User corrected this to be on the wall beside the fridge, not on the top prep wall.
7. Hob-sink main prep area: five-hole x2.
8. Right of sink counter: five-hole x2.
9. Far-right counter / microwave zone: five-hole x2-3.
10. Dining table high zone: five-hole x2.
11. Dining table low zone: five-hole x2.

Current heights:

- High countertop sockets: around H=115, or H=105-120 for dining high zone.
- Low dining sockets: H=30-35.
- Fridge: H=40-50.
- Under sink and dishwasher: H=45-60.
- Hood outlet: H=220.
- Switch: H=125.
- Counter height: H=86.
- Table height: H=75.

## Current Circuit/Wiring Assumptions

These are schematic assumptions for drawing clarity, not final electrical construction documents.

Global conductor colors:

- L / fire/live: red `#d62728`
- N / neutral: blue `#1f77b4`
- PE / earth: green `#2ca02c`

Important: The user was very unhappy when the wiring looked like one single line. Always make L/N/PE visually separate in the wiring drawings.

Current circuit labels:

- `IN`: total incoming feed, L/N/PE from switch area.
- `L1`: lighting, BV 3x1.5. Switch only cuts L; N/PE go directly to lights.
- `C2`: fridge, BV 3x2.5, L/N/PE to socket.
- `C3`: left/main prep + hood, BV 3x2.5, L/N/PE to points.
- `C4`: right counter / microwave / dining table, BV 3x2.5, L/N/PE to points.
- `C5`: under sink / dishwasher, BV 3x2.5, L/N/PE to points.
- `C6`: induction hob, BV 3x4-6, L/N/PE to device.

Current note shown in legends:

- The drawing spreads L/N/PE apart for readability.
- In real construction, conductors for the same circuit generally run together in the same conduit.

If editing wiring diagrams, preserve this distinction. The user wants to see all three conductors, but the diagram must not imply that real-world conductors are necessarily separated into different conduits.

## Wiring Drawing Implementation Details

Relevant constants/functions:

- `WIRE_COLORS` is intentionally neutral gray for circuit labels. Do not reintroduce per-circuit bright colors unless the user asks. The user asked for only three special global colors for L/N/PE.
- `CONDUCTOR_COLORS` stores L/N/PE colors.
- `CONDUCTOR_GAP = 7.0` separates conductors visually.
- `CONDUCTOR_OFFSETS` maps L/N/PE to offsets.
- `_offset_polyline(...)` computes real parallel polylines so three conductors do not overlap into one line.
- `draw_wire(...)` draws L/N/PE as separate conductors along a route.
- `draw_socket_row_feed(...)` draws a three-conductor feed and individual drops to every socket in a row.
- `draw_three_conductor_bus_with_riser(...)` is used for ceiling light rows. It avoids ugly diagonal artifacts by drawing a clear T-shaped three-conductor bus.

Why these functions exist:

- A prior implementation drew three conductors too close together, and the user correctly said it looked like a single line.
- A later diagonal-offset approach made some routes visually messy.
- Current implementation uses parallel polylines and expanded socket spacing in wiring views.

When drawing socket rows in wiring views:

- Use wider spacing than in normal elevations:
  - 2 sockets often use spacing 28.
  - 3 sockets often use spacing 24.
- This is intentionally not a perfect physical spacing diagram; it is a legible wiring schematic layered onto the elevation.

## Current Figure Builder Functions

Normal design drawings:

- `build_floor_plan_figure()`
- `build_view_from_south_figure()`
- `build_view_from_north_figure()`
- `build_view_from_west_figure()`
- `build_view_from_east_figure()`
- `build_view_from_ceiling_figure()`
- `build_view_from_floor_figure()`

Wiring drawings:

- `build_wiring_view_from_south_figure()`
- `build_wiring_view_from_north_figure()`
- `build_wiring_view_from_west_figure()`
- `build_wiring_view_from_east_figure()`
- `build_wiring_view_from_ceiling_figure()`
- `build_wiring_view_from_floor_figure()`

Main save list is near the bottom of `draw_kitchen_layout.py`. If you add a new figure, add it there.

## Visual Style Requirements

The user previously requested:

- Thinner lines overall.
- Chinese text in drawings.
- Units should remain as `cm`.
- Font should use YaHei when possible.
- High-resolution output.

Current script settings:

- Font list includes Microsoft YaHei, Hiragino Sans GB, STHeiti, Arial Unicode MS, Songti SC.
- `OUTPUT_DPI = 450`.
- Most line widths are intentionally thin.

Do not make walls, dimensions, or wires much thicker unless user explicitly asks. The user already complained that the lines were too thick earlier.

## User Preferences And Prior Corrections

Important corrections made by user:

- "hood above" in the original plan was not acceptable as a vague label. It became a proper hood/hood cabinet area.
- Hood/hob position was adjusted relative to sink; current key relation is hob left of sink with 80 cm gap.
- Table changed through multiple options, final current table is 140 x 70.
- Table should be by/right side wall area with two chairs on the left side in plan.
- User wanted separate wall elevations, not a single combined diagram.
- User emphasized wall elevation must show the full wall, at actual scale, not just a cropped cabinet run.
- South/top wall window exact size and position must match user-supplied data.
- Counter height changed from 90 to 86.
- The sink-right base run is two 80 cm bases.
- West wall must include the 70 cm door.
- All Chinese labels, units still cm.
- Add bottom/front wall elevation because it was missing.
- There are six face drawings if excluding the floor plan: north/top wall, south/bottom wall, west wall, east wall, ceiling, floor.
- For wiring, total incoming L/N/PE feed enters at the bottom/south wall switch position.
- User explicitly said "零 火 地三个特殊颜色就好了"; use only L/N/PE colors as special wire colors.
- User explicitly said a route to a socket should show at least three wires going down, not one.

## Safety / Electrical Caveat

Electrical drawings are high-stakes. Always state that:

- These drawings are schematic design/施工沟通示意.
- Final fixed wiring, conductor size, breaker/RCD/RCBO configuration, conduit routes, and load calculation must be reviewed and installed by a qualified electrician according to current local Chinese codes and site conditions.

Do not present these drawings as final stamped electrical construction drawings.

## How To Verify Before Answering

After changes:

1. Run:

```bash
python3 draw_kitchen_layout.py
```

2. Open the affected PNG(s) with `view_image`, preferably at original detail:

```text
/Users/bytedance/kitchen/output/<file>.png
```

3. Check:

- Text is readable.
- No important labels overlap.
- L/N/PE are visually distinct in wiring drawings.
- Socket rows show separate drops to each point.
- Wall elevations still show a complete wall and the correct dimensions.
- Generated images are committed if script changed.

## Common Final Response Pattern

For drawing changes, reply briefly in Chinese:

- Say what changed.
- Mention the file(s) or images regenerated.
- If pushed, mention the commit hash.
- Show the relevant image(s) using absolute Markdown image paths.
- Include the electrical caveat if the change concerns wiring.

Example:

```markdown
已改完并重新生成。这里每个插座点位都按 L/N/PE 三根线分别下引，颜色全局统一：红=L，蓝=N，绿=PE。已推送到 GitHub：`<hash>`。

![顶部墙三线走线图](/Users/bytedance/kitchen/output/wiring_view_from_south.png)
```

## Current Open Risks

- The drawings are detailed for visual planning but still schematic; no load calculation table exists yet.
- No breaker/distribution box schedule exists yet.
- No conduit diameter/count specification exists beyond labels like BV 3x2.5.
- No exact socket brand/module dimensions are modeled.
- Fridge final model and ventilation clearance are not yet confirmed.
- Microwave/steam-oven final power is not confirmed; if upgraded to high-power appliance, circuit assumptions may need revision.
- Actual wall chases and junction boxes must be coordinated with site structure, water lines, gas, exhaust ducting, and cabinet installer.

Keep these risks visible when discussing electrical details.
