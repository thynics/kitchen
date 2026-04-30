#!/usr/bin/env python3
"""Draw a scaled kitchen layout with Matplotlib.

The drawing uses centimeters as data units. It recreates the reference plan:
500 cm x 300 cm room, 60 cm countertop depth, top-run modules, left fridge
niche/door, bottom door, right dining zone, dimensions, legend, and scale bar.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.lines import Line2D


plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": [
            "Microsoft YaHei",
            "Microsoft YaHei UI",
            "Hiragino Sans GB",
            "STHeiti",
            "Arial Unicode MS",
            "Songti SC",
        ],
        "axes.unicode_minus": False,
    }
)


ROOM_W = 500
ROOM_H = 300
WALL_ELEVATION_H = 300
OUTPUT_DPI = 450
COUNTER_DEPTH = 60
TOP_Y0 = ROOM_H - COUNTER_DEPTH
COUNTER_HEIGHT = 86
WINDOW_X = 252
WINDOW_W = 100
WINDOW_SILL_H = 93
WINDOW_H = 118
BOTTOM_DOOR_X = 274
BOTTOM_DOOR_W = 86
BOTTOM_DOOR_H = 178
LEFT_DOOR_H = 195
SINK_X = 260
SINK_W = 80
HOB_W = 90
HOB_TO_SINK_GAP = 80
HOB_X = SINK_X - HOB_TO_SINK_GAP - HOB_W
LEFT_COVERED_W = 52
LEFT_USABLE_PREP_W = HOB_X - LEFT_COVERED_W
TABLE_X = 335
TABLE_Y = 75
TABLE_W = 140
TABLE_D = 70
TABLE_HEIGHT = 75
EAST_POWER_ZONE_POS = ROOM_H - TABLE_Y - TABLE_D / 2
CEILING_LIGHT_XS = (70, 190, 310, 430)
CEILING_LIGHT_Y_FROM_NORTH = (80, 215)
ENTRY_X = BOTTOM_DOOR_X + BOTTOM_DOOR_W + 18
ENTRY_H = 125
WALL_TRUNK_H = 262
HIGH_SOCKET_H = 112
LOW_SOCKET_H = 35
UPPER_DEPTH = 35
UPPER_HEIGHT = 75
UPPER_BOTTOM = COUNTER_HEIGHT + 60
UPPER_TOP = UPPER_BOTTOM + UPPER_HEIGHT
BRIDGE_CABINET_H = 40
BRIDGE_CABINET_BOTTOM = 225
BRIDGE_CABINET_TOP = BRIDGE_CABINET_BOTTOM + BRIDGE_CABINET_H

OUTPUT_DIR = Path(__file__).resolve().parent / "output"


@dataclass(frozen=True)
class Module:
    name: str
    x: float
    width: float
    label: str
    facecolor: str


@dataclass(frozen=True)
class UpperModule:
    name: str
    x: float
    width: float
    label: str
    facecolor: str
    hatch: str | None = None


TOP_MODULES = [
    Module("prep_left", 0, HOB_X, "", "#fff1a8"),
    Module("hob", HOB_X, HOB_W, "", "#ffd9d9"),
    Module("prep_gap", HOB_X + HOB_W, HOB_TO_SINK_GAP, f"备餐\n{HOB_TO_SINK_GAP:g}", "#fff1a8"),
    Module("sink", SINK_X, SINK_W, "水槽\n80", "#d8eefb"),
    Module("base_right_1", 340, 80, "地柜\n80", "#f3e7d8"),
    Module("base_right_2", 420, 80, "地柜\n80", "#eee8dc"),
]


UPPER_MODULES = [
    UpperModule("pipe_chase", 0, LEFT_COVERED_W, "封板/包管\n52", "#f2f2f2", "///"),
    UpperModule("narrow", LEFT_COVERED_W, LEFT_USABLE_PREP_W, "窄吊柜\n38", "#edf3ea"),
    UpperModule("hood_cabinet", HOB_X, HOB_W, "烟机柜\n90", "#f5ded8"),
    UpperModule("left_wall_cabinet", HOB_X + HOB_W, WINDOW_X - HOB_X - HOB_W, "吊柜\n72", "#edf3ea"),
    UpperModule("right_wall_cabinet_68", WINDOW_X + WINDOW_W, 68, "吊柜\n68", "#edf3ea"),
    UpperModule("right_wall_cabinet_80", WINDOW_X + WINDOW_W + 68, 80, "吊柜\n80", "#edf3ea"),
]


COLORS = {
    "wall": "#0b0b0b",
    "dimension": "#111111",
    "window": "#2c8a2c",
    "door_left": "#e41a1c",
    "door_bottom": "#ff7f00",
    "fridge": "#dbe9ff",
    "fridge_edge": "#3574b8",
    "utility": "#ece8ff",
    "table": "#f6e5cc",
    "table_edge": "#8a5423",
    "text_muted": "#555555",
    "purple": "#6b3fa0",
    "blue": "#1f77b4",
    "brown": "#7f2f2f",
    "green": "#2ca02c",
    "upper": "#496a55",
    "hood": "#b66b5d",
    "electric": "#264f9e",
    "switch": "#b35c00",
}


WIRE_COLORS = {
    "IN": "#444444",
    "L1": "#444444",
    "C2": "#444444",
    "C3": "#444444",
    "C4": "#444444",
    "C5": "#444444",
    "C6": "#444444",
}

CONDUCTOR_COLORS = {
    "L": "#d62728",
    "N": "#1f77b4",
    "PE": "#2ca02c",
}

CONDUCTOR_LABELS = {
    "L": "L 火线",
    "N": "N 零线",
    "PE": "PE 地线",
}

CONDUCTOR_GAP = 2.8

WIRE_LEGEND = [
    ("IN", "进线/分线区: 总进线 L/N/PE 从开关位附近进入"),
    ("L1", "L1 照明: BV 3x1.5, 开关只切 L, N/PE 到灯"),
    ("C2", "C2 冰箱: BV 3x2.5, L/N/PE, 独立插座"),
    ("C3", "C3 左/主备餐+烟机: BV 3x2.5, L/N/PE"),
    ("C4", "C4 右台面/微波炉/餐桌: BV 3x2.5, L/N/PE"),
    ("C5", "C5 水槽下/洗碗机: BV 3x2.5, L/N/PE"),
    ("C6", "C6 电磁炉: BV 3x4-6, L/N/PE, 按功率定"),
]


def add_rect(
    ax: plt.Axes,
    xy: tuple[float, float],
    width: float,
    height: float,
    *,
    fc: str = "none",
    ec: str = "#333333",
    lw: float = 0.5,
    alpha: float = 1.0,
    hatch: str | None = None,
    ls: str | tuple = "-",
    zorder: int = 2,
) -> patches.Rectangle:
    rect = patches.Rectangle(
        xy,
        width,
        height,
        facecolor=fc,
        edgecolor=ec,
        linewidth=lw,
        alpha=alpha,
        hatch=hatch,
        linestyle=ls,
        zorder=zorder,
    )
    ax.add_patch(rect)
    return rect


def add_label(
    ax: plt.Axes,
    x: float,
    y: float,
    text: str,
    *,
    size: float = 10,
    color: str = "#111111",
    weight: str = "normal",
    ha: str = "center",
    va: str = "center",
    rotation: float = 0,
    zorder: int = 5,
) -> None:
    ax.text(
        x,
        y,
        text,
        ha=ha,
        va=va,
        fontsize=size,
        color=color,
        fontweight=weight,
        rotation=rotation,
        zorder=zorder,
    )


def dim_line(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    label: str,
    *,
    color: str = "#111111",
    text_offset: float = 7,
    size: float = 9,
    label_color: str | None = None,
    extension: bool = True,
    lw: float = 0.42,
) -> None:
    """Draw a dimension line with arrowheads and a centered label."""

    x1, y1 = start
    x2, y2 = end
    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle="<|-|>",
            color=color,
            lw=lw,
            mutation_scale=7,
            shrinkA=0,
            shrinkB=0,
        ),
        zorder=6,
    )

    horizontal = abs(y2 - y1) < abs(x2 - x1)
    if horizontal:
        add_label(
            ax,
            (x1 + x2) / 2,
            y1 + text_offset,
            label,
            size=size,
            color=label_color or color,
        )
        if extension:
            for x in (x1, x2):
                ax.add_line(Line2D([x, x], [ROOM_H + 2, y1], color=color, lw=0.32, zorder=4))
    else:
        add_label(
            ax,
            x1 - text_offset,
            (y1 + y2) / 2,
            label,
            size=size,
            color=label_color or color,
            rotation=90,
        )
        if extension:
            for y in (y1, y2):
                ax.add_line(Line2D([x1, -2], [y, y], color=color, lw=0.32, zorder=4))


def bracket_line(
    ax: plt.Axes,
    x: float,
    y1: float,
    y2: float,
    label: str,
    *,
    color: str = "#111111",
    tick: float = 7,
    side: str = "right",
    size: float = 9,
) -> None:
    ax.add_line(Line2D([x, x], [y1, y2], color=color, lw=0.42, zorder=4))
    sgn = 1 if side == "right" else -1
    ax.add_line(Line2D([x - sgn * tick, x + sgn * tick], [y1, y1], color=color, lw=0.42, zorder=4))
    ax.add_line(Line2D([x - sgn * tick, x + sgn * tick], [y2, y2], color=color, lw=0.42, zorder=4))
    add_label(
        ax,
        x - sgn * (tick + 6),
        (y1 + y2) / 2,
        label,
        size=size,
        rotation=90,
        color=color,
    )


def draw_electrical_point(
    ax: plt.Axes,
    x: float,
    y: float,
    label: str,
    *,
    kind: str = "socket",
    label_dx: float = 0,
    label_dy: float = 10,
    size: float = 6.2,
    zorder: int = 12,
) -> None:
    color = COLORS["switch"] if kind == "switch" else COLORS["electric"]
    if kind == "switch":
        add_rect(ax, (x - 4.5, y - 5.5), 9, 11, fc="#fff6e8", ec=color, lw=0.45, zorder=zorder)
        add_label(ax, x, y, "S", size=4.8, color=color, weight="bold", zorder=zorder + 1)
    else:
        add_rect(ax, (x - 4, y - 3), 8, 6, fc="#f4f7ff", ec=color, lw=0.45, zorder=zorder)
        ax.add_patch(patches.Circle((x - 1.4, y), 0.55, facecolor=color, edgecolor=color, lw=0, zorder=zorder + 1))
        ax.add_patch(patches.Circle((x + 1.4, y), 0.55, facecolor=color, edgecolor=color, lw=0, zorder=zorder + 1))
    if label:
        add_label(ax, x + label_dx, y + label_dy, label, size=size, color=color, zorder=zorder + 1)


def draw_socket_row(
    ax: plt.Axes,
    x: float,
    y: float,
    count: int,
    label: str,
    *,
    spacing: float = 12,
    label_dx: float = 0,
    label_dy: float = 12,
    size: float = 5.4,
) -> None:
    start = x - (count - 1) * spacing / 2
    for i in range(count):
        draw_electrical_point(ax, start + i * spacing, y, "", size=size)
    add_label(ax, x + label_dx, y + label_dy, label, size=size, color=COLORS["electric"], zorder=13)


def draw_outer_room(ax: plt.Axes) -> None:
    add_rect(ax, (0, 0), ROOM_W, ROOM_H, fc="white", ec=COLORS["wall"], lw=0.6, zorder=1)


def draw_left_prep_coverage(ax: plt.Axes, y: float, height: float, *, label_size: float = 7.5) -> None:
    add_rect(
        ax,
        (0, y),
        LEFT_COVERED_W,
        height,
        fc="#f2f2f2",
        ec="#777777",
        lw=0.35,
        alpha=0.82,
        zorder=4,
    )
    ax.add_patch(
        patches.Rectangle(
            (0, y),
            LEFT_COVERED_W,
            height,
            facecolor="none",
            edgecolor="#999999",
            hatch="///",
            linewidth=0.0,
            zorder=5,
        )
    )
    add_label(ax, LEFT_COVERED_W / 2, y + height / 2, f"遮挡\n{LEFT_COVERED_W:g}", size=label_size, color="#555555", zorder=6)
    add_label(
        ax,
        LEFT_COVERED_W + LEFT_USABLE_PREP_W / 2,
        y + height / 2,
        f"备餐\n{LEFT_USABLE_PREP_W:g}",
        size=label_size + 1,
        zorder=6,
    )


def draw_top_run(ax: plt.Axes) -> None:
    for module in TOP_MODULES:
        add_rect(
            ax,
            (module.x, TOP_Y0),
            module.width,
            COUNTER_DEPTH,
            fc=module.facecolor,
            ec="#666666",
            lw=0.35,
            alpha=0.9,
            zorder=2,
        )
        if module.label:
            add_label(ax, module.x + module.width / 2, TOP_Y0 + COUNTER_DEPTH / 2, module.label, size=10)

    draw_left_prep_coverage(ax, TOP_Y0, COUNTER_DEPTH)
    draw_hob(ax)
    draw_sink(ax)

    # Module boundary line that separates the kitchen run from the open area.
    ax.add_line(Line2D([0, ROOM_W], [TOP_Y0, TOP_Y0], color="#777777", lw=0.38, zorder=3))

    # Top module widths, aligned with the reference segments.
    y = ROOM_H + 9
    top_segments = [
        (0, HOB_X, f"{HOB_X:g}"),
        (HOB_X, HOB_X + HOB_W, "90"),
        (HOB_X + HOB_W, SINK_X, f"{HOB_TO_SINK_GAP:g}"),
        (SINK_X, SINK_X + SINK_W, "80"),
        (340, 420, "80"),
        (420, 500, "80"),
    ]
    for x1, x2, label in top_segments:
        dim_line(ax, (x1, y), (x2, y), label, text_offset=8, size=9, extension=False)
        ax.add_line(Line2D([x1, x1], [ROOM_H, y + 3], color="#111111", lw=0.3, zorder=4))
    ax.add_line(Line2D([ROOM_W, ROOM_W], [ROOM_H, y + 3], color="#111111", lw=0.3, zorder=4))
    add_label(ax, ROOM_W / 2, y + 17, "顶部台面模块宽度 (cm)", size=9)

    # Window and top-total dimensions.
    dim_line(
        ax,
        (0, ROOM_H + 38),
        (252, ROOM_H + 38),
        "252 cm",
        color=COLORS["purple"],
        label_color=COLORS["purple"],
        extension=False,
        size=10,
    )
    ax.add_line(Line2D([WINDOW_X, WINDOW_X + WINDOW_W], [ROOM_H + 38, ROOM_H + 38], color=COLORS["window"], lw=0.62, zorder=5))
    dim_line(
        ax,
        (WINDOW_X, ROOM_H + 38),
        (WINDOW_X + WINDOW_W, ROOM_H + 38),
        "窗 100 cm",
        color=COLORS["window"],
        label_color="#111111",
        extension=False,
        size=9,
    )
    dim_line(
        ax,
        (WINDOW_X + WINDOW_W, ROOM_H + 38),
        (ROOM_W, ROOM_H + 38),
        "148 cm",
        color="#333333",
        extension=False,
        size=9,
    )
    dim_line(ax, (0, ROOM_H + 60), (ROOM_W, ROOM_H + 60), "500 cm", extension=True, size=10)


def draw_hob(ax: plt.Axes) -> None:
    hood_x = HOB_X + 18
    hob_x = HOB_X + 20
    add_label(ax, HOB_X + HOB_W / 2, 293, "烟机位", size=8)
    add_rect(ax, (hood_x, 282), 52, 7, fc="none", ec="#777777", lw=0.3, zorder=4)
    ax.add_line(Line2D([hood_x, hood_x + 52], [285.5, 285.5], color="#777777", lw=0.28, ls="--", zorder=4))

    add_rect(ax, (hob_x, 247), 46, 40, fc="#fff6f6", ec="#333333", lw=0.38, zorder=4)
    for cx in (hob_x + 10, hob_x + 36):
        for cy in (257, 275):
            burner = patches.Circle((cx, cy), 6, facecolor="#f7f7f7", edgecolor="#111111", lw=0.35, zorder=5)
            ax.add_patch(burner)


def draw_sink(ax: plt.Axes) -> None:
    # Sink basin and tap.
    add_rect(ax, (276, 248), 56, 38, fc="#f7fbff", ec="#333333", lw=0.38, zorder=4)
    add_rect(ax, (278, 250), 52, 34, fc="none", ec="#777777", lw=0.28, zorder=5)
    ax.add_patch(patches.Circle((300, 278), 2.5, facecolor="white", edgecolor="#333333", lw=0.35, zorder=6))
    ax.add_line(Line2D([300, 300], [279, 294], color="#333333", lw=0.45, zorder=6))
    ax.add_patch(patches.Arc((300, 292), 8, 12, theta1=90, theta2=270, color="#333333", lw=0.5, zorder=6))


def draw_upper_cabinet_projection(ax: plt.Axes) -> None:
    """Show wall cabinet footprints without turning the floor plan into a cabinet schedule."""

    top_projection_y = ROOM_H - UPPER_DEPTH
    for module in UPPER_MODULES:
        add_rect(
            ax,
            (module.x, top_projection_y),
            module.width,
            UPPER_DEPTH,
            fc=module.facecolor,
            ec=COLORS["upper"],
            lw=0.42,
            alpha=0.22,
            hatch=module.hatch,
            ls=(0, (5, 3)),
            zorder=7,
        )

    add_rect(
        ax,
        (0, 110),
        COUNTER_DEPTH,
        90,
        fc="#edf3ea",
        ec=COLORS["upper"],
        lw=0.42,
        alpha=0.16,
        ls=(0, (5, 3)),
        zorder=7,
    )


def draw_floor_electrical_points(ax: plt.Axes) -> None:
    dining_power_y = ROOM_H - EAST_POWER_ZONE_POS
    draw_electrical_point(ax, 9, 174, "冰箱三孔\n侧边低位\nH=40-50", label_dx=34, label_dy=2, size=4.8)
    draw_socket_row(ax, 9, 212, 2, "左备餐x2\n左墙冰箱旁\nH=115", spacing=8, label_dx=64, label_dy=-5, size=4.6)
    draw_electrical_point(ax, 132, 291, "油烟机\n三孔H=220", label_dy=-16, size=5.2)
    draw_electrical_point(ax, 136, 247, "电磁炉/嵌入灶\n独立大功率\nH=50", label_dy=-21, size=4.7)
    draw_socket_row(ax, 220, 238, 2, "主备餐x2\n五孔H=115", spacing=9, label_dy=-18, size=4.8)
    draw_socket_row(ax, 312, 238, 3, "水槽下x3\n小厨宝/RO/备", spacing=8, label_dy=-21, size=4.5)
    draw_electrical_point(ax, 354, 222, "洗碗机\n相邻柜\nH=45-60", label_dx=25, label_dy=-8, size=4.3)
    draw_socket_row(ax, 382, 238, 2, "水槽右x2\n五孔H=115", spacing=9, label_dy=15, size=4.7)
    draw_socket_row(ax, 462, 238, 3, "微波炉区x2-3\n五孔H=115", spacing=8, label_dy=-18, size=4.8)
    draw_electrical_point(
        ax,
        BOTTOM_DOOR_X + BOTTOM_DOOR_W + 18,
        8,
        "唯一开关\n控制天花灯\nH=125",
        kind="switch",
        label_dx=42,
        label_dy=8,
        size=4.8,
    )
    draw_socket_row(
        ax,
        506,
        dining_power_y + 18,
        2,
        "餐桌旁x2\n五孔H=105-120",
        spacing=8,
        label_dx=26,
        label_dy=0,
        size=4.8,
    )
    draw_socket_row(
        ax,
        506,
        dining_power_y - 18,
        2,
        "低位x2\n五孔H=30-35",
        spacing=8,
        label_dx=26,
        label_dy=0,
        size=4.8,
    )


def draw_left_zone(ax: plt.Axes) -> None:
    # Utility unit above the fridge niche.
    add_rect(ax, (0, 200), LEFT_COVERED_W, 40, fc=COLORS["utility"], ec="#6a62a5", lw=0.4, zorder=2)
    add_label(ax, LEFT_COVERED_W / 2, 220, "杂物柜\n40", size=9)

    # Fridge niche: 75 cm deep x 90 cm wide along the wall.
    add_rect(ax, (0, 110), 75, 90, fc=COLORS["fridge"], ec=COLORS["fridge_edge"], lw=0.5, zorder=2)
    add_label(ax, 37.5, 155, "冰箱位\n75D x 90W", size=9)

    # Left-wall 70 cm door, hinged at the lower end and swinging into the room.
    ax.add_line(Line2D([0, 0], [32, 102], color=COLORS["door_left"], lw=0.9, zorder=7))
    ax.add_line(Line2D([0, 70], [32, 32], color="#666666", lw=0.48, zorder=4))
    ax.add_patch(patches.Arc((0, 32), 140, 140, theta1=0, theta2=90, color="#666666", lw=0.4, ls=(0, (4, 3)), zorder=4))
    add_label(ax, 22, 58, "门\n70 cm", size=9)

    # Left-wall local dimensions from the reference.
    bracket_line(ax, -10, 200, 240, "40 cm", side="right", size=8)
    bracket_line(ax, -10, 110, 200, "90 cm", side="right", size=8)
    bracket_line(ax, -10, 0, 32, "32 cm", side="right", size=8)


def draw_bottom_door(ax: plt.Axes) -> None:
    # Bottom-wall 86 cm door, hinged at x=274 and swinging upward.
    door_end = BOTTOM_DOOR_X + BOTTOM_DOOR_W
    ax.add_line(Line2D([BOTTOM_DOOR_X, BOTTOM_DOOR_X], [0, 78], color=COLORS["window"], lw=0.72, zorder=7))
    ax.add_line(Line2D([BOTTOM_DOOR_X, door_end], [0, 0], color=COLORS["door_bottom"], lw=0.9, zorder=8))
    ax.add_patch(patches.Arc((BOTTOM_DOOR_X, 0), BOTTOM_DOOR_W * 2, BOTTOM_DOOR_W * 2, theta1=0, theta2=90, color="#666666", lw=0.4, ls=(0, (4, 3)), zorder=4))
    add_label(ax, 304, 30, "门\n86 cm", size=9)

    y = -18
    dim_line(ax, (0, y), (BOTTOM_DOOR_X, y), f"{BOTTOM_DOOR_X:g} cm", color=COLORS["blue"], label_color=COLORS["blue"], extension=False, size=10)
    dim_line(
        ax,
        (BOTTOM_DOOR_X, y),
        (door_end, y),
        f"{BOTTOM_DOOR_W:g} cm",
        color=COLORS["door_bottom"],
        label_color="#d95f02",
        extension=False,
        size=10,
    )
    dim_line(ax, (door_end, y), (ROOM_W, y), f"{ROOM_W - door_end:g} cm", color=COLORS["brown"], label_color=COLORS["brown"], extension=False, size=10)
    dim_line(ax, (0, -38), (500, -38), "500 cm", extension=True, size=10)


def draw_dining(ax: plt.Axes) -> None:
    # 140 x 70 cm table, placed horizontally in the open right-side workspace.
    add_rect(ax, (TABLE_X, TABLE_Y), TABLE_W, TABLE_D, fc=COLORS["table"], ec=COLORS["table_edge"], lw=0.48, zorder=2)
    add_label(ax, TABLE_X + TABLE_W / 2, TABLE_Y + TABLE_D / 2, "餐桌\n140 x 70 cm\n4座", size=9)

    chair_fc = "#f8ead6"
    chair_w = 40
    chair_d = 8
    for chair_x in (TABLE_X + 24, TABLE_X + 76):
        add_rect(ax, (chair_x, TABLE_Y + TABLE_D), chair_w, chair_d, fc=chair_fc, ec=COLORS["table_edge"], lw=0.34, zorder=1)
        add_rect(ax, (chair_x, TABLE_Y - chair_d), chair_w, chair_d, fc=chair_fc, ec=COLORS["table_edge"], lw=0.34, zorder=1)

    clear_x = TABLE_X + TABLE_W + 16
    dim_line(
        ax,
        (clear_x, TABLE_Y + TABLE_D),
        (clear_x, TOP_Y0),
        f"{TOP_Y0 - TABLE_Y - TABLE_D:g} cm",
        color=COLORS["table_edge"],
        label_color=COLORS["table_edge"],
        text_offset=8,
        extension=False,
        size=8,
    )
    dim_line(
        ax,
        (clear_x, 0),
        (clear_x, TABLE_Y),
        f"{TABLE_Y:g} cm",
        color=COLORS["table_edge"],
        label_color=COLORS["table_edge"],
        text_offset=8,
        extension=False,
        size=8,
    )


def draw_annotations(ax: plt.Axes) -> None:
    add_label(ax, ROOM_W / 2, ROOM_H + 78, "厨房平面布置图 - 最终方案", size=14, weight="bold")

    add_label(ax, 230, 128, "开放动线 /\n工作区", size=12, color=COLORS["text_muted"])

    dim_line(
        ax,
        (-30, 0),
        (-30, ROOM_H),
        "300 cm",
        color=COLORS["green"],
        label_color=COLORS["green"],
        text_offset=10,
        extension=True,
        size=10,
    )

    dim_line(
        ax,
        (515, TOP_Y0),
        (515, ROOM_H),
        "60 cm\n深",
        color="#111111",
        label_color="#111111",
        text_offset=-18,
        extension=True,
        size=9,
    )


def draw_legend(ax: plt.Axes) -> None:
    box_x = -42
    box_y = -108
    box_w = 115
    box_h = 88
    add_rect(ax, (box_x, box_y), box_w, box_h, fc="white", ec="#777777", lw=0.45, zorder=0)
    add_label(ax, box_x + 16, box_y + box_h - 8, "图例", size=8, weight="bold", ha="left")

    items = [
        (COLORS["window"], "窗 100 cm"),
        (COLORS["door_left"], "左墙门 70 cm"),
        (COLORS["door_bottom"], "底墙门 86 cm"),
        (COLORS["upper"], "虚线: 顶柜/桥柜"),
        (COLORS["electric"], "插座 / 开关点位"),
    ]
    for i, (color, text) in enumerate(items):
        y = box_y + box_h - 22 - i * 13
        ls = (0, (5, 3)) if "虚线" in text else "-"
        ax.add_line(Line2D([box_x + 13, box_x + 33], [y, y], color=color, lw=0.9, ls=ls, zorder=2))
        add_label(ax, box_x + 42, y, text, size=7.5, ha="left")


def draw_assumptions(ax: plt.Axes) -> None:
    box_x = 127
    box_y = -126
    box_w = 220
    box_h = 82
    add_rect(ax, (box_x, box_y), box_w, box_h, fc="white", ec="#777777", lw=0.45, zorder=0)
    add_label(ax, box_x + 10, box_y + box_h - 8, "方案参数", size=8, weight="bold", ha="left")

    assumptions = [
        "台面深度 60 cm，左上贴墙起始",
        "顶柜: 52封板 + 38窄柜 + 90烟机柜 + 72吊柜",
        "窗区 100 cm 留空，右侧顶柜 68 + 80 cm",
        "冰箱上方桥柜可选，需确认冰箱散热",
        "烟机/灶台右移，水槽左侧留 80 cm 备餐",
        "水槽右侧 160 cm 拆成两个 80 cm 地柜",
        "餐桌横放 140 x 70 cm，上方 95 cm / 下方 75 cm",
        "天花: 8个筒灯均布; 电位: 设备专用 + 台面/餐桌分区",
    ]
    for i, text in enumerate(assumptions):
        add_label(ax, box_x + 8, box_y + box_h - 18 - i * 7.6, f"-  {text}", size=6.2, ha="left")


def mini_x(panel_x: float, panel_w: float, value: float, total: float) -> float:
    return panel_x + 18 + value / total * (panel_w - 36)


def mini_dim(
    ax: plt.Axes,
    x1: float,
    x2: float,
    y: float,
    label: str,
    *,
    color: str = "#333333",
    size: float = 6.4,
) -> None:
    ax.annotate(
        "",
        xy=(x2, y),
        xytext=(x1, y),
        arrowprops=dict(arrowstyle="<->", color=color, lw=0.42, mutation_scale=6, shrinkA=0, shrinkB=0),
        zorder=6,
    )
    add_label(ax, (x1 + x2) / 2, y + 5, label, size=size, color=color)


def mini_vdim(
    ax: plt.Axes,
    x: float,
    y1: float,
    y2: float,
    label: str,
    *,
    color: str = "#333333",
    size: float = 6.4,
) -> None:
    ax.annotate(
        "",
        xy=(x, y2),
        xytext=(x, y1),
        arrowprops=dict(arrowstyle="<->", color=color, lw=0.42, mutation_scale=6, shrinkA=0, shrinkB=0),
        zorder=6,
    )
    add_label(ax, x + 5, (y1 + y2) / 2, label, size=size, color=color, rotation=90)


def draw_param_panel(ax: plt.Axes, x: float, y: float, w: float, h: float, title: str) -> None:
    add_rect(ax, (x, y), w, h, fc="white", ec="#777777", lw=0.5, zorder=0)
    add_label(ax, x + 8, y + h - 9, title, size=8, weight="bold", ha="left")


def draw_north_wall_params(ax: plt.Axes, x: float, y: float, w: float, h: float) -> None:
    draw_param_panel(ax, x, y, w, h, "顶部墙 / 台面 - 500 cm")
    block_y = y + 28
    block_h = 18
    for module in TOP_MODULES:
        x1 = mini_x(x, w, module.x, ROOM_W)
        x2 = mini_x(x, w, module.x + module.width, ROOM_W)
        add_rect(ax, (x1, block_y), x2 - x1, block_h, fc=module.facecolor, ec="#666666", lw=0.4, zorder=2)
        label = module.label.replace("\n", " ") if module.label else f"灶台 {HOB_W:g}"
        add_label(ax, (x1 + x2) / 2, block_y + block_h / 2, label, size=5.7)

    win_x1 = mini_x(x, w, 252, ROOM_W)
    win_x2 = mini_x(x, w, 352, ROOM_W)
    ax.add_line(Line2D([win_x1, win_x2], [y + 58, y + 58], color=COLORS["window"], lw=0.8, zorder=5))
    add_label(ax, (win_x1 + win_x2) / 2, y + 64, "窗 100 cm", size=6.4, color=COLORS["window"])
    mini_dim(ax, mini_x(x, w, 0, ROOM_W), mini_x(x, w, ROOM_W, ROOM_W), y + 17, "500 cm")
    mini_vdim(ax, x + w - 10, block_y, block_y + block_h, f"台面 H={COUNTER_HEIGHT:g} cm")


def draw_south_wall_params(ax: plt.Axes, x: float, y: float, w: float, h: float) -> None:
    draw_param_panel(ax, x, y, w, h, "底部墙 / 门洞 - 500 cm")
    wall_y = y + 27
    x0 = mini_x(x, w, 0, ROOM_W)
    x1 = mini_x(x, w, 274, ROOM_W)
    x2 = mini_x(x, w, 360, ROOM_W)
    x3 = mini_x(x, w, ROOM_W, ROOM_W)
    ax.add_line(Line2D([x0, x3], [wall_y, wall_y], color="#111111", lw=0.6, zorder=3))
    ax.add_line(Line2D([x1, x2], [wall_y, wall_y], color=COLORS["door_bottom"], lw=1.0, zorder=5))
    mini_dim(ax, x0, x1, y + 14, "274")
    mini_dim(ax, x1, x2, y + 14, "门 86", color=COLORS["door_bottom"])
    mini_dim(ax, x2, x3, y + 14, "140", color=COLORS["brown"])

    table_x1 = mini_x(x, w, 335, ROOM_W)
    table_x2 = mini_x(x, w, 475, ROOM_W)
    table_y = y + 47
    add_rect(ax, (table_x1, table_y), table_x2 - table_x1, 12, fc=COLORS["table"], ec=COLORS["table_edge"], lw=0.45, zorder=2)
    add_label(ax, (table_x1 + table_x2) / 2, table_y + 6, "餐桌 140 cm, H=75", size=6.2)
    mini_vdim(ax, x + w - 13, wall_y, table_y, "离墙 75 cm", color=COLORS["table_edge"], size=6.0)


def draw_west_wall_params(ax: plt.Axes, x: float, y: float, w: float, h: float) -> None:
    draw_param_panel(ax, x, y, w, h, "西墙 / 左墙 - 300 cm")
    block_y = y + 31
    block_h = 18
    segments = [
        (0, 32, "32", "#f7f7f7"),
        (32, 102, "门 70", "#ffe6e6"),
        (102, 110, "8", "#f7f7f7"),
        (110, 200, "冰箱 90", COLORS["fridge"]),
        (200, 240, "杂物 40", COLORS["utility"]),
        (240, 300, "顶部 60", "#fff1a8"),
    ]
    for a, b, label, color in segments:
        x1 = mini_x(x, w, a, ROOM_H)
        x2 = mini_x(x, w, b, ROOM_H)
        add_rect(ax, (x1, block_y), x2 - x1, block_h, fc=color, ec="#666666", lw=0.4, zorder=2)
        add_label(ax, (x1 + x2) / 2, block_y + block_h / 2, label, size=5.8)
    mini_dim(ax, mini_x(x, w, 0, ROOM_H), mini_x(x, w, ROOM_H, ROOM_H), y + 18, "300 cm")
    mini_vdim(ax, x + w - 10, block_y, block_y + block_h, f"台面 H={COUNTER_HEIGHT:g} cm")


def draw_east_wall_params(ax: plt.Axes, x: float, y: float, w: float, h: float) -> None:
    draw_param_panel(ax, x, y, w, h, "东墙 / 右墙 - 300 cm")
    block_y = y + 31
    block_h = 18
    segments = [
        (0, 75, "下侧留 75", "#f7f7f7"),
        (75, 145, "餐桌占 70", COLORS["table"]),
        (145, 240, "顶部留 95", "#f7f7f7"),
        (240, 300, "台面深 60", "#eee8dc"),
    ]
    for a, b, label, color in segments:
        x1 = mini_x(x, w, a, ROOM_H)
        x2 = mini_x(x, w, b, ROOM_H)
        add_rect(ax, (x1, block_y), x2 - x1, block_h, fc=color, ec="#666666", lw=0.4, zorder=2)
        add_label(ax, (x1 + x2) / 2, block_y + block_h / 2, label, size=5.7)
    mini_dim(ax, mini_x(x, w, 0, ROOM_H), mini_x(x, w, ROOM_H, ROOM_H), y + 18, "300 cm")
    power_x = mini_x(x, w, EAST_POWER_ZONE_POS, ROOM_H)
    ax.add_line(Line2D([power_x, power_x], [block_y - 3, block_y + block_h + 3], color=COLORS["electric"], lw=0.7, zorder=5))
    add_label(ax, power_x, y + 63, "餐桌高/低位", size=5.8, color=COLORS["electric"])
    add_label(ax, x + w - 10, y + 63, "餐桌 H=75 cm / 离右墙 25 cm", size=5.8, ha="right", color=COLORS["table_edge"])


def draw_wall_parameters(ax: plt.Axes) -> None:
    add_label(ax, ROOM_W / 2, -62, "各墙面参数 (cm)", size=10, weight="bold")
    left_x = -42
    right_x = 256
    panel_w = 286
    panel_h = 76
    draw_north_wall_params(ax, left_x, -145, panel_w, panel_h)
    draw_south_wall_params(ax, right_x, -145, panel_w, panel_h)
    draw_west_wall_params(ax, left_x, -235, panel_w, panel_h)
    draw_east_wall_params(ax, right_x, -235, panel_w, panel_h)


def draw_scale(ax: plt.Axes) -> None:
    box_x = 372
    box_y = -108
    box_w = 170
    box_h = 62
    add_rect(ax, (box_x, box_y), box_w, box_h, fc="white", ec="#777777", lw=0.45, zorder=0)
    add_label(ax, box_x + 8, box_y + box_h - 16, "比例 1:40", size=8, weight="bold", ha="left")

    x0 = box_x + 20
    y0 = box_y + 18
    total = 135
    segment = total / 4
    for i in range(4):
        fc = "black" if i % 2 == 0 else "white"
        add_rect(ax, (x0 + i * segment, y0), segment, 7, fc=fc, ec="black", lw=0.45, zorder=2)

    for i, label in enumerate(["0", "50", "100", "150", "200 cm"]):
        x = x0 + i * segment
        ax.add_line(Line2D([x, x], [y0, y0 + 11], color="black", lw=0.35, zorder=3))
        add_label(ax, x, y0 + 19, label, size=8)
    ax.add_line(Line2D([x0 + total, x0 + total], [y0, y0 + 11], color="black", lw=0.35, zorder=3))


def setup_wall_canvas(title: str, length: float, *, figsize: tuple[float, float]) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=figsize, dpi=160)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-35, length + 35)
    ax.set_ylim(-48, 178)
    ax.axis("off")
    add_label(ax, length / 2, 163, title, size=14, weight="bold")
    add_label(ax, length / 2, 146, "所有尺寸单位 cm", size=8, color=COLORS["text_muted"])
    return fig, ax


def draw_wall_total_dim(ax: plt.Axes, length: float, y: float = -32) -> None:
    mini_dim(ax, 0, length, y, f"墙长 {length:g} cm", size=8)
    ax.add_line(Line2D([0, 0], [y + 4, 0], color="#333333", lw=0.42, zorder=3))
    ax.add_line(Line2D([length, length], [y + 4, 0], color="#333333", lw=0.42, zorder=3))


def build_floor_plan_figure() -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=(14, 10.2), dpi=160)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-48, 548)
    ax.set_ylim(-134, 385)
    ax.axis("off")

    draw_outer_room(ax)
    draw_top_run(ax)
    draw_left_zone(ax)
    draw_upper_cabinet_projection(ax)
    draw_floor_electrical_points(ax)
    draw_bottom_door(ax)
    draw_dining(ax)
    draw_annotations(ax)
    draw_legend(ax)
    draw_assumptions(ax)
    draw_scale(ax)

    fig.tight_layout(pad=0.2)
    return fig, ax


def build_north_wall_figure() -> tuple[plt.Figure, plt.Axes]:
    fig, ax = setup_wall_canvas("顶部墙设计 - 台面", ROOM_W, figsize=(13.5, 5.2))

    add_label(ax, -24, 45, "地面", size=8, ha="left", color=COLORS["text_muted"])
    ax.add_line(Line2D([0, ROOM_W], [0, 0], color="#111111", lw=0.6, zorder=3))

    for module in TOP_MODULES:
        add_rect(ax, (module.x, 0), module.width, COUNTER_HEIGHT, fc=module.facecolor, ec="#555555", lw=0.4, zorder=2)
        label = module.label.replace("\n", " ") if module.label else f"灶台 {HOB_W:g}"
        add_label(ax, module.x + module.width / 2, 45, label, size=8)

    ax.add_line(Line2D([0, ROOM_W], [COUNTER_HEIGHT, COUNTER_HEIGHT], color="#111111", lw=0.6, zorder=5))
    mini_vdim(ax, ROOM_W + 18, 0, COUNTER_HEIGHT, f"台面 H={COUNTER_HEIGHT:g} cm", size=8)

    # Window is projected above the sink run, matching the floor plan coordinates.
    add_rect(ax, (252, 108), 100, 42, fc="#f6fff6", ec=COLORS["window"], lw=0.55, zorder=3)
    add_label(ax, 302, 129, "窗 100", size=8, color=COLORS["window"])
    mini_dim(ax, 252, 352, 154, "100 cm", color=COLORS["window"], size=7.5)

    # Hood reference above the hob module.
    hood_x = HOB_X + 19
    add_rect(ax, (hood_x, 116), 52, 8, fc="#fff6f6", ec="#777777", lw=0.45, zorder=4)
    add_label(ax, HOB_X + HOB_W / 2, 130, "烟机位", size=7)

    y = -14
    for module in TOP_MODULES:
        label = f"{module.width:g}"
        mini_dim(ax, module.x, module.x + module.width, y, label, size=7)
    draw_wall_total_dim(ax, ROOM_W)
    fig.tight_layout(pad=0.2)
    return fig, ax


def build_south_wall_figure() -> tuple[plt.Figure, plt.Axes]:
    fig, ax = setup_wall_canvas("底部墙设计 - 门与餐桌关系", ROOM_W, figsize=(13.5, 5.2))

    ax.add_line(Line2D([0, ROOM_W], [0, 0], color="#111111", lw=0.6, zorder=3))
    ax.add_line(Line2D([274, 360], [0, 0], color=COLORS["door_bottom"], lw=1.0, zorder=5))
    add_label(ax, 317, 13, "门 86", size=8, color="#d95f02")
    mini_dim(ax, 0, 274, -15, "274", color=COLORS["blue"], size=7)
    mini_dim(ax, 274, 360, -15, "86", color=COLORS["door_bottom"], size=7)
    mini_dim(ax, 360, 500, -15, "140", color=COLORS["brown"], size=7)

    add_rect(ax, (TABLE_X, TABLE_Y), TABLE_W, TABLE_D, fc=COLORS["table"], ec=COLORS["table_edge"], lw=0.5, zorder=2)
    add_label(ax, TABLE_X + TABLE_W / 2, TABLE_Y + TABLE_D / 2, "餐桌 140 x 70\nH=75 cm", size=8)
    mini_dim(ax, TABLE_X, TABLE_X + TABLE_W, TABLE_Y + TABLE_D + 10, "140 cm", color=COLORS["table_edge"], size=7.5)
    mini_vdim(ax, TABLE_X + TABLE_W + 14, 0, TABLE_Y, "留 75 cm", color=COLORS["table_edge"], size=7.5)
    mini_vdim(ax, TABLE_X - 14, TABLE_Y, TABLE_Y + TABLE_D, "餐桌深 70 cm", color=COLORS["table_edge"], size=7.0)

    add_label(ax, TABLE_X + TABLE_W / 2, TABLE_Y - 11, "餐桌离底墙距离", size=7, color=COLORS["text_muted"])
    draw_wall_total_dim(ax, ROOM_W)
    fig.tight_layout(pad=0.2)
    return fig, ax


def build_west_wall_figure() -> tuple[plt.Figure, plt.Axes]:
    fig, ax = setup_wall_canvas("西墙设计 - 左侧", ROOM_H, figsize=(9.5, 5.2))

    strip_y = 42
    strip_h = 34
    segments = [
        (0, 32, "32", "#f7f7f7"),
        (32, 102, "门 70", "#ffe6e6"),
        (102, 110, "8", "#f7f7f7"),
        (110, 200, "冰箱位\n90W x 75D", COLORS["fridge"]),
        (200, 240, "杂物柜\n40", COLORS["utility"]),
        (240, 300, "顶部台面\n60D", "#fff1a8"),
    ]
    for a, b, label, color in segments:
        add_rect(ax, (a, strip_y), b - a, strip_h, fc=color, ec="#666666", lw=0.45, zorder=2)
        add_label(ax, (a + b) / 2, strip_y + strip_h / 2, label, size=7)
        mini_dim(ax, a, b, strip_y - 12, f"{b - a:g}", size=6.8)

    ax.add_line(Line2D([0, ROOM_H], [strip_y, strip_y], color="#111111", lw=0.6, zorder=3))
    mini_vdim(ax, ROOM_H + 14, strip_y, strip_y + strip_h, f"台面 H={COUNTER_HEIGHT:g} cm", size=7.5)
    add_label(ax, 270, 98, "顶部台面深 60 cm", size=7.5, color=COLORS["text_muted"])
    draw_wall_total_dim(ax, ROOM_H)
    fig.tight_layout(pad=0.2)
    return fig, ax


def build_east_wall_figure() -> tuple[plt.Figure, plt.Axes]:
    fig, ax = setup_wall_canvas("东墙设计 - 餐桌间距", ROOM_H, figsize=(9.5, 5.2))

    strip_y = 42
    strip_h = 34
    segments = [
        (0, TABLE_Y, "下侧留\n75", "#f7f7f7"),
        (TABLE_Y, TABLE_Y + TABLE_D, "餐桌占\n70", COLORS["table"]),
        (TABLE_Y + TABLE_D, TOP_Y0, "顶部留\n95", "#f7f7f7"),
        (TOP_Y0, ROOM_H, "台面深\n60", "#eee8dc"),
    ]
    for a, b, label, color in segments:
        add_rect(ax, (a, strip_y), b - a, strip_h, fc=color, ec="#666666", lw=0.45, zorder=2)
        add_label(ax, (a + b) / 2, strip_y + strip_h / 2, label, size=7)
        mini_dim(ax, a, b, strip_y - 12, f"{b - a:g}", size=6.8)

    wall_offset = ROOM_W - TABLE_X - TABLE_W
    add_rect(ax, (TABLE_Y, 96), TABLE_D, 22, fc=COLORS["table"], ec=COLORS["table_edge"], lw=0.5, zorder=2)
    add_label(ax, TABLE_Y + TABLE_D / 2, 107, f"餐桌 H={TABLE_HEIGHT} cm\n离墙 {wall_offset:g} cm", size=7.2)
    mini_vdim(ax, TABLE_Y + TABLE_D + 12, 0, TABLE_HEIGHT, "餐桌 H=75 cm", color=COLORS["table_edge"], size=7.2)
    draw_wall_total_dim(ax, ROOM_H)
    fig.tight_layout(pad=0.2)
    return fig, ax


def setup_full_wall_view(title: str, wall_length: float, *, figsize: tuple[float, float]) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=figsize, dpi=160)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-42, wall_length + 42)
    ax.set_ylim(-72, WALL_ELEVATION_H + 50)
    ax.axis("off")

    add_label(ax, wall_length / 2, WALL_ELEVATION_H + 34, title, size=14, weight="bold")
    add_rect(ax, (0, 0), wall_length, WALL_ELEVATION_H, fc="#ffffff", ec=COLORS["wall"], lw=0.55, zorder=1)
    mini_dim(ax, 0, wall_length, -54, f"墙长 {wall_length:g} cm", size=8.5)
    mini_vdim(ax, wall_length + 20, 0, WALL_ELEVATION_H, f"墙高 {WALL_ELEVATION_H:g} cm", size=8.0)
    return fig, ax


def draw_upper_cabinets_elevation(ax: plt.Axes) -> None:
    for module in UPPER_MODULES:
        add_rect(
            ax,
            (module.x, UPPER_BOTTOM),
            module.width,
            UPPER_HEIGHT,
            fc=module.facecolor,
            ec=COLORS["upper"],
            lw=0.46,
            alpha=0.86,
            hatch=module.hatch,
            zorder=4,
        )
        add_label(
            ax,
            module.x + module.width / 2,
            UPPER_BOTTOM + UPPER_HEIGHT / 2,
            module.label,
            size=6.8 if module.width < 45 else 7.4,
            color=COLORS["upper"],
            zorder=5,
        )
        mini_dim(ax, module.x, module.x + module.width, UPPER_TOP + 9, f"{module.width:g}", color=COLORS["upper"], size=6.2)

    add_rect(
        ax,
        (WINDOW_X, UPPER_BOTTOM),
        WINDOW_W,
        UPPER_HEIGHT,
        fc="none",
        ec=COLORS["window"],
        lw=0.42,
        ls=(0, (5, 3)),
        zorder=4,
    )
    add_label(ax, WINDOW_X + WINDOW_W / 2, UPPER_TOP + 21, "窗区留空 100", size=6.8, color=COLORS["window"])

    hood_x1 = HOB_X + 15
    hood_x2 = HOB_X + HOB_W - 15
    hood = patches.Polygon(
        [(hood_x1, UPPER_BOTTOM), (hood_x2, UPPER_BOTTOM), (hood_x2 - 8, 116), (hood_x1 + 8, 116)],
        closed=True,
        facecolor="#fff3f0",
        edgecolor=COLORS["hood"],
        linewidth=0.5,
        zorder=6,
    )
    ax.add_patch(hood)
    add_label(ax, HOB_X + HOB_W / 2, 128, "油烟机", size=6.8, color=COLORS["hood"], zorder=7)
    ax.add_line(
        Line2D(
            [HOB_X + HOB_W / 2, HOB_X + HOB_W / 2],
            [UPPER_BOTTOM, UPPER_TOP],
            color=COLORS["hood"],
            lw=0.45,
            ls=(0, (4, 3)),
            zorder=7,
        )
    )

    mini_vdim(ax, -18, UPPER_BOTTOM, UPPER_TOP, f"顶柜 H={UPPER_HEIGHT:g} cm", color=COLORS["upper"], size=6.5)
    mini_vdim(ax, -31, 0, UPPER_BOTTOM, f"顶柜底 H={UPPER_BOTTOM:g} cm", color=COLORS["upper"], size=6.2)
    add_label(ax, 438, UPPER_TOP + 21, f"顶柜深 {UPPER_DEPTH:g}D", size=6.8, color=COLORS["upper"])


def draw_south_electrical_points(ax: plt.Axes) -> None:
    draw_electrical_point(ax, 165, 216, "油烟机\n三孔 H=220", label_dx=24, label_dy=0, size=5.1)
    draw_electrical_point(ax, 132, 52, "电磁炉/嵌入灶\n独立大功率\nH=50", label_dx=-40, label_dy=2, size=4.6)
    draw_socket_row(ax, 220, 115, 2, "主备餐 x2\n五孔 H=115", spacing=12, label_dy=15, size=4.8)
    draw_socket_row(ax, 312, 55, 3, "水槽下 x3\n小厨宝/RO/备用\nH=45-60", spacing=10, label_dy=18, size=4.5)
    draw_electrical_point(ax, 352, 52, "洗碗机\n相邻柜\nH=45-60", label_dx=24, label_dy=0, size=4.5)
    draw_socket_row(ax, 382, 115, 2, "水槽右 x2\n五孔 H=115", spacing=12, label_dy=15, size=4.8)
    draw_socket_row(ax, 462, 115, 3, "微波炉区 x2-3\n五孔 H=115", spacing=10, label_dy=15, size=4.8)


def draw_elevation_counter_run(ax: plt.Axes) -> None:
    for module in TOP_MODULES:
        add_rect(ax, (module.x, 0), module.width, COUNTER_HEIGHT, fc=module.facecolor, ec="#555555", lw=0.4, zorder=2)
        mini_dim(ax, module.x, module.x + module.width, -10, f"{module.width:g}", size=7)
        if module.name == "prep_left":
            continue
        label = module.label.replace("\n", " ") if module.label else f"灶台 {HOB_W:g}"
        add_label(ax, module.x + module.width / 2, 43, label, size=8)
    draw_left_prep_coverage(ax, 0, COUNTER_HEIGHT, label_size=6.8)

    ax.add_line(Line2D([0, ROOM_W], [COUNTER_HEIGHT, COUNTER_HEIGHT], color="#111111", lw=0.5, zorder=4))
    mini_vdim(ax, ROOM_W + 9, 0, COUNTER_HEIGHT, f"台面 H={COUNTER_HEIGHT:g} cm", size=7.6)

    add_rect(
        ax,
        (WINDOW_X, WINDOW_SILL_H),
        WINDOW_W,
        WINDOW_H,
        fc="#f6fff6",
        ec=COLORS["window"],
        lw=0.55,
        zorder=3,
    )
    add_label(ax, WINDOW_X + WINDOW_W / 2, WINDOW_SILL_H + WINDOW_H / 2, "窗", size=9, color=COLORS["window"])
    mini_dim(ax, 0, WINDOW_X, -31, f"{WINDOW_X:g} cm", color=COLORS["purple"], size=7.0)
    mini_dim(ax, WINDOW_X, WINDOW_X + WINDOW_W, -31, f"{WINDOW_W:g} cm", color=COLORS["window"], size=7.0)
    mini_dim(ax, WINDOW_X + WINDOW_W, ROOM_W, -31, f"{ROOM_W - WINDOW_X - WINDOW_W:g} cm", size=7.0)
    mini_vdim(ax, WINDOW_X - 12, 0, WINDOW_SILL_H, f"{WINDOW_SILL_H:g} cm", color=COLORS["green"], size=7.0)
    mini_vdim(ax, WINDOW_X + WINDOW_W + 12, WINDOW_SILL_H, WINDOW_SILL_H + WINDOW_H, f"{WINDOW_H:g} cm", color=COLORS["window"], size=7.0)
    draw_upper_cabinets_elevation(ax)
    draw_south_electrical_points(ax)


def draw_table_elevation(ax: plt.Axes, x: float, width: float, *, label: str, zorder: int = 5) -> None:
    add_rect(
        ax,
        (x, 0),
        width,
        TABLE_HEIGHT,
        fc=COLORS["table"],
        ec=COLORS["table_edge"],
        lw=0.55,
        alpha=0.72,
        zorder=zorder,
    )
    add_label(ax, x + width / 2, TABLE_HEIGHT / 2, label, size=8, zorder=zorder + 1)
    mini_vdim(ax, x + width + 10, 0, TABLE_HEIGHT, "餐桌 H=75 cm", color=COLORS["table_edge"], size=7.2)


def draw_side_counter_profile(ax: plt.Axes, start: float, end: float, *, show_dim: bool = True) -> None:
    add_rect(ax, (start, 0), end - start, COUNTER_HEIGHT, fc="#eee8dc", ec="#555555", lw=0.45, zorder=3)
    add_label(ax, (start + end) / 2, 45, f"顶部台面\n60D / H={COUNTER_HEIGHT:g}", size=8)
    if show_dim:
        mini_dim(ax, start, end, -10, "60", size=7)
    mini_vdim(ax, end + 10, 0, COUNTER_HEIGHT, f"台面 H={COUNTER_HEIGHT:g} cm", size=7.0)


def build_view_from_south_figure() -> tuple[plt.Figure, plt.Axes]:
    fig, ax = setup_full_wall_view("南向视图 - 看向顶部墙面", ROOM_W, figsize=(13.5, 7.0))
    draw_elevation_counter_run(ax)
    fig.tight_layout(pad=0.2)
    return fig, ax


def build_view_from_north_figure() -> tuple[plt.Figure, plt.Axes]:
    fig, ax = setup_full_wall_view("北向视图 - 看向底部墙面", ROOM_W, figsize=(13.5, 7.0))
    add_label(ax, ROOM_W / 2, WALL_ELEVATION_H + 18, "底边方向 500 cm", size=8, color=COLORS["text_muted"])

    add_rect(
        ax,
        (BOTTOM_DOOR_X, 0),
        BOTTOM_DOOR_W,
        BOTTOM_DOOR_H,
        fc="#fff7f0",
        ec=COLORS["door_bottom"],
        lw=0.6,
        zorder=2,
    )
    add_label(
        ax,
        BOTTOM_DOOR_X + BOTTOM_DOOR_W / 2,
        BOTTOM_DOOR_H / 2,
        f"门\n{BOTTOM_DOOR_W:g}W\nH={BOTTOM_DOOR_H:g}",
        size=8.0,
        color="#d95f02",
    )

    mini_dim(ax, 0, BOTTOM_DOOR_X, -10, f"{BOTTOM_DOOR_X:g}", color=COLORS["blue"], size=7.0)
    mini_dim(
        ax,
        BOTTOM_DOOR_X,
        BOTTOM_DOOR_X + BOTTOM_DOOR_W,
        -10,
        f"门 {BOTTOM_DOOR_W:g}",
        color=COLORS["door_bottom"],
        size=7.0,
    )
    mini_dim(
        ax,
        BOTTOM_DOOR_X + BOTTOM_DOOR_W,
        ROOM_W,
        -10,
        f"{ROOM_W - BOTTOM_DOOR_X - BOTTOM_DOOR_W:g}",
        color=COLORS["brown"],
        size=7.0,
    )
    mini_vdim(
        ax,
        BOTTOM_DOOR_X + BOTTOM_DOOR_W + 30,
        0,
        BOTTOM_DOOR_H,
        f"{BOTTOM_DOOR_H:g} cm",
        color=COLORS["door_bottom"],
        size=7.0,
    )
    draw_electrical_point(
        ax,
        BOTTOM_DOOR_X + BOTTOM_DOOR_W + 18,
        125,
        "唯一开关\n控制天花灯\nH=125",
        kind="switch",
        label_dx=35,
        label_dy=0,
        size=6.0,
    )
    fig.tight_layout(pad=0.2)
    return fig, ax


def build_view_from_west_figure() -> tuple[plt.Figure, plt.Axes]:
    fig, ax = setup_full_wall_view("西墙立面 - 左墙", ROOM_H, figsize=(9.5, 7.0))
    add_label(ax, 0, -42, "南 / 下侧", size=7, ha="left", color=COLORS["text_muted"])
    add_label(ax, ROOM_H, -42, "北 / 顶部台面", size=7, ha="right", color=COLORS["text_muted"])

    # West wall segments from the floor plan: 32 + Door 70 + 8 + Fridge 90 + Utility 40 + Top run 60.
    add_rect(ax, (32, 0), 70, LEFT_DOOR_H, fc="#fff7f7", ec=COLORS["door_left"], lw=0.48, zorder=2)
    add_label(ax, 67, LEFT_DOOR_H / 2, f"门\n70W\nH={LEFT_DOOR_H:g}", size=8, color=COLORS["door_left"])
    mini_vdim(ax, 18, 0, LEFT_DOOR_H, f"{LEFT_DOOR_H:g} cm", color=COLORS["door_left"], size=6.6)

    add_rect(ax, (110, 0), 90, 190, fc=COLORS["fridge"], ec=COLORS["fridge_edge"], lw=0.42, alpha=0.42, zorder=2)
    add_label(ax, 155, 120, "冰箱位\n90W x 75D\n高度待定", size=7, color=COLORS["fridge_edge"])

    add_rect(
        ax,
        (110, BRIDGE_CABINET_BOTTOM),
        90,
        BRIDGE_CABINET_H,
        fc="#edf3ea",
        ec=COLORS["upper"],
        lw=0.46,
        alpha=0.74,
        ls=(0, (5, 3)),
        zorder=3,
    )
    add_label(ax, 155, (BRIDGE_CABINET_BOTTOM + BRIDGE_CABINET_TOP) / 2, "可选桥柜\n90W x 60D\n需确认散热", size=6.4, color=COLORS["upper"])
    mini_vdim(ax, 205, BRIDGE_CABINET_BOTTOM, BRIDGE_CABINET_TOP, f"桥柜 H={BRIDGE_CABINET_H:g} cm", color=COLORS["upper"], size=6.0)

    add_rect(ax, (200, 0), 40, COUNTER_HEIGHT, fc=COLORS["utility"], ec="#6a62a5", lw=0.38, zorder=3)
    add_label(ax, 220, COUNTER_HEIGHT / 2, f"杂物柜\n40W / H={COUNTER_HEIGHT:g}", size=7)

    draw_side_counter_profile(ax, TOP_Y0, ROOM_H, show_dim=False)

    west_segments = [
        (0, 32, "32"),
        (32, 102, "门 70"),
        (102, 110, "8"),
        (110, 200, "冰箱 90"),
        (200, 240, "杂物 40"),
        (240, 300, "顶部 60"),
    ]
    for x1, x2, label in west_segments:
        mini_dim(ax, x1, x2, -10, label, size=6.6)
    draw_electrical_point(ax, 190, 45, "冰箱三孔\n侧边低位\nH=40-50", label_dx=-18, label_dy=42, size=5.2)
    draw_socket_row(ax, 220, 115, 2, "左备餐 x2\n左墙冰箱旁\n五孔 H=115", spacing=12, label_dy=18, size=4.8)
    fig.tight_layout(pad=0.2)
    return fig, ax


def build_view_from_east_figure() -> tuple[plt.Figure, plt.Axes]:
    fig, ax = setup_full_wall_view("东向视图 - 看向左侧", ROOM_H, figsize=(9.5, 7.0))
    add_label(ax, 0, -42, "北 / 顶部台面", size=7, ha="left", color=COLORS["text_muted"])
    add_label(ax, ROOM_H, -42, "南 / 下侧", size=7, ha="right", color=COLORS["text_muted"])

    counter_start = 0
    counter_end = COUNTER_DEPTH

    draw_side_counter_profile(ax, counter_start, counter_end)
    table_start = ROOM_H - TABLE_Y - TABLE_D
    add_rect(
        ax,
        (table_start, 0),
        TABLE_D,
        TABLE_HEIGHT,
        fc=COLORS["table"],
        ec=COLORS["table_edge"],
        lw=0.45,
        alpha=0.26,
        ls=(0, (5, 3)),
        zorder=2,
    )
    add_label(ax, table_start + TABLE_D / 2, TABLE_HEIGHT / 2, "餐桌投影", size=6.2, color=COLORS["table_edge"])

    add_rect(
        ax,
        (EAST_POWER_ZONE_POS - 34, 20),
        68,
        114,
        fc="#f8fbff",
        ec=COLORS["electric"],
        lw=0.35,
        alpha=0.42,
        ls=(0, (5, 3)),
        zorder=1,
    )
    add_label(ax, EAST_POWER_ZONE_POS, 143, "餐桌旁插座区", size=7.2, color=COLORS["electric"], weight="bold")
    draw_socket_row(
        ax,
        EAST_POWER_ZONE_POS,
        HIGH_SOCKET_H,
        2,
        "餐桌旁 x2\n五孔 H=105-120",
        label_dy=18,
        size=5.2,
    )
    draw_socket_row(
        ax,
        EAST_POWER_ZONE_POS,
        LOW_SOCKET_H,
        2,
        "低位 x2\n五孔 H=30-35",
        label_dy=-18,
        size=5.2,
    )
    mini_dim(ax, COUNTER_DEPTH, table_start, 151, f"{table_start - COUNTER_DEPTH:g}", color=COLORS["electric"], size=6.2)
    mini_dim(ax, table_start, EAST_POWER_ZONE_POS, 151, f"{EAST_POWER_ZONE_POS - table_start:g}", color=COLORS["electric"], size=6.2)
    fig.tight_layout(pad=0.2)
    return fig, ax


def setup_horizontal_surface_view(title: str, *, figsize: tuple[float, float] = (13.5, 7.0)) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=figsize, dpi=160)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-42, ROOM_W + 52)
    ax.set_ylim(-170, ROOM_H + 50)
    ax.axis("off")
    add_label(ax, ROOM_W / 2, ROOM_H + 35, title, size=14, weight="bold")
    add_rect(ax, (0, 0), ROOM_W, ROOM_H, fc="white", ec=COLORS["wall"], lw=0.62, zorder=1)
    add_label(ax, ROOM_W / 2, -43, "南 / 底部墙", size=7, color=COLORS["text_muted"])
    add_label(ax, ROOM_W / 2, ROOM_H + 12, "北 / 顶部墙", size=7, color=COLORS["text_muted"])
    add_label(ax, -24, ROOM_H / 2, "西 / 左墙", size=7, color=COLORS["text_muted"], rotation=90)
    add_label(ax, ROOM_W + 26, ROOM_H / 2, "东 / 右墙", size=7, color=COLORS["text_muted"], rotation=90)
    mini_dim(ax, 0, ROOM_W, -18, f"{ROOM_W:g} cm", size=7.4)
    mini_vdim(ax, ROOM_W + 18, 0, ROOM_H, f"{ROOM_H:g} cm", size=7.4)
    return fig, ax


def draw_plan_doors_for_surface(ax: plt.Axes) -> None:
    ax.add_line(Line2D([0, 0], [32, 102], color=COLORS["door_left"], lw=0.8, zorder=5))
    ax.add_patch(patches.Arc((0, 32), 140, 140, theta1=0, theta2=90, color="#777777", lw=0.35, ls=(0, (4, 3)), zorder=4))
    add_label(ax, 28, 55, "左墙门\n70", size=6.8, color=COLORS["door_left"])

    door_end = BOTTOM_DOOR_X + BOTTOM_DOOR_W
    ax.add_line(Line2D([BOTTOM_DOOR_X, door_end], [0, 0], color=COLORS["door_bottom"], lw=0.9, zorder=5))
    ax.add_patch(patches.Arc((BOTTOM_DOOR_X, 0), BOTTOM_DOOR_W * 2, BOTTOM_DOOR_W * 2, theta1=0, theta2=90, color="#777777", lw=0.35, ls=(0, (4, 3)), zorder=4))
    add_label(ax, BOTTOM_DOOR_X + BOTTOM_DOOR_W / 2, 28, "底墙门\n86", size=6.8, color="#d95f02")


def draw_downlight(ax: plt.Axes, x: float, y: float, *, label: str = "", size: float = 5.5) -> None:
    ax.add_patch(
        patches.Circle(
            (x, y),
            5.5,
            facecolor="#fff8cc",
            edgecolor="#d6a400",
            linewidth=0.48,
            zorder=5,
        )
    )
    ax.add_patch(
        patches.Circle(
            (x, y),
            2.2,
            facecolor="#ffe680",
            edgecolor="#d6a400",
            linewidth=0.35,
            zorder=6,
        )
    )
    if label:
        add_label(ax, x, y + 17, label, size=size, color="#7a5b00")


def draw_wire(
    ax: plt.Axes,
    points: list[tuple[float, float]] | tuple[tuple[float, float], ...],
    circuit: str,
    *,
    lw: float = 0.82,
    ls: str | tuple = "-",
    alpha: float = 0.92,
    zorder: int = 20,
    conductors: tuple[str, ...] = ("L", "N", "PE"),
) -> None:
    if len(conductors) == 1:
        conductor_offsets = {conductors[0]: 0.0}
    else:
        conductor_offsets = {"L": CONDUCTOR_GAP, "N": 0.0, "PE": -CONDUCTOR_GAP}
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        horizontal = abs(x2 - x1) >= abs(y2 - y1)
        for conductor in conductors:
            offset = conductor_offsets.get(conductor, 0.0)
            dx = 0.0 if horizontal else offset
            dy = offset if horizontal else 0.0
            ax.add_line(
                Line2D(
                    [x1 + dx, x2 + dx],
                    [y1 + dy, y2 + dy],
                    color=CONDUCTOR_COLORS[conductor],
                    lw=max(lw * 0.42, 0.20),
                    ls=ls,
                    alpha=alpha,
                    zorder=zorder,
                )
            )


def socket_centers(x: float, count: int, spacing: float) -> list[float]:
    start = x - (count - 1) * spacing / 2
    return [start + i * spacing for i in range(count)]


def draw_socket_row_feed(
    ax: plt.Axes,
    entry_points: list[tuple[float, float]] | tuple[tuple[float, float], ...],
    socket_x: float,
    socket_y: float,
    count: int,
    circuit: str,
    *,
    spacing: float = 12,
    feed_offset: float = 11,
    lw: float = 0.72,
    ls: str | tuple = "-",
) -> None:
    """Draw a three-conductor drop and small terminal bus for a socket row."""
    feed_y = socket_y + feed_offset
    centers = socket_centers(socket_x, count, spacing)
    draw_wire(ax, [*entry_points, (socket_x, feed_y)], circuit, lw=lw, ls=ls)
    if count > 1:
        draw_wire(ax, [(centers[0], feed_y), (centers[-1], feed_y)], circuit, lw=lw, ls=ls)
    for sx in centers:
        draw_wire(ax, [(sx, feed_y), (sx, socket_y)], circuit, lw=lw, ls=ls)


def draw_junction(ax: plt.Axes, x: float, y: float, label: str, circuit: str = "IN", *, size: float = 5.4) -> None:
    color = WIRE_COLORS[circuit]
    ax.add_patch(patches.Circle((x, y), 4.4, facecolor="#ffffff", edgecolor=color, linewidth=0.58, zorder=23))
    add_label(ax, x, y, "J", size=4.3, color=color, weight="bold", zorder=24)
    add_label(ax, x + 8, y + 8, label, size=size, color=color, ha="left", va="bottom", zorder=24)


def draw_wire_drop(
    ax: plt.Axes,
    x: float,
    y_top: float,
    y_bottom: float,
    circuit: str,
    label: str = "",
    *,
    label_dx: float = 8,
    size: float = 5.0,
) -> None:
    draw_wire(ax, [(x, y_top), (x, y_bottom)], circuit)
    if label:
        add_label(ax, x + label_dx, (y_top + y_bottom) / 2, label, size=size, color=WIRE_COLORS[circuit], ha="left")


def draw_wiring_legend(ax: plt.Axes, x: float, y: float, *, compact: bool = False) -> None:
    row_h = 9.5 if compact else 10.5
    rows = WIRE_LEGEND if not compact else WIRE_LEGEND[:1] + WIRE_LEGEND[1:4] + WIRE_LEGEND[4:]
    width = 304 if compact else 330
    height = 33 + len(rows) * row_h
    add_rect(ax, (x, y), width, height, fc="#ffffff", ec="#999999", lw=0.36, alpha=0.92, zorder=30)
    add_label(ax, x + 7, y + height - 7, "走线图例", size=6.3, weight="bold", ha="left", zorder=31)
    conductor_x = x + 66
    for i, conductor in enumerate(("L", "N", "PE")):
        xx = conductor_x + i * 49
        ax.add_line(Line2D([xx, xx + 12], [y + height - 8, y + height - 8], color=CONDUCTOR_COLORS[conductor], lw=1.2, zorder=31))
        add_label(ax, xx + 15, y + height - 8, CONDUCTOR_LABELS[conductor], size=4.7, color=CONDUCTOR_COLORS[conductor], ha="left", zorder=31)
    add_label(ax, x + 7, y + height - 18, "图中把 L/N/PE 拉开表达；实际同一回路仍同管同走", size=4.9, color="#555555", ha="left", zorder=31)
    for i, (code, text) in enumerate(rows):
        yy = y + height - 34 - i * row_h
        add_label(ax, x + 8, yy, code, size=4.9 if compact else 5.3, color=WIRE_COLORS[code], weight="bold", ha="left", zorder=31)
        add_label(ax, x + 26, yy, text, size=4.7 if compact else 5.1, color=WIRE_COLORS[code], ha="left", zorder=31)


def draw_wall_trunk(ax: plt.Axes, length: float, label: str = "吊顶/墙顶主干 H≈260") -> None:
    ax.add_line(Line2D([0, length], [WALL_TRUNK_H, WALL_TRUNK_H], color="#9a9a9a", lw=0.5, ls=(0, (5, 4)), zorder=18))
    add_label(ax, length / 2, WALL_TRUNK_H + 10, label, size=5.6, color="#666666", zorder=19)


def draw_wiring_note(ax: plt.Axes, x: float, y: float, text: str, *, width: float, height: float = 22) -> None:
    add_rect(ax, (x, y), width, height, fc="#ffffff", ec="#b0b0b0", lw=0.28, alpha=0.88, zorder=28)
    add_label(ax, x + 7, y + height / 2, text, size=5.0, color="#555555", ha="left", va="center", zorder=29)


def build_wiring_view_from_south_figure() -> tuple[plt.Figure, plt.Axes]:
    fig, ax = setup_full_wall_view("三线走线图 - 顶部墙 / 橱柜墙", ROOM_W, figsize=(13.5, 7.0))
    draw_elevation_counter_run(ax)
    draw_wall_trunk(ax, ROOM_W)
    add_label(ax, ENTRY_X, WALL_TRUNK_H + 21, "来自底墙开关位进线\n经吊顶主干转入", size=5.2, color=WIRE_COLORS["IN"])

    # C3: hood + main prep sockets.
    draw_wire(ax, [(ENTRY_X, WALL_TRUNK_H + 5), (165, WALL_TRUNK_H + 5), (165, 216)], "C3")
    draw_wire(ax, [(220, WALL_TRUNK_H + 5), (220, 115)], "C3")
    draw_junction(ax, 220, WALL_TRUNK_H + 5, "C3", "C3", size=4.6)

    # C4: right countertop and microwave zone.
    draw_wire(ax, [(ENTRY_X, WALL_TRUNK_H - 3), (382, WALL_TRUNK_H - 3), (382, 115)], "C4")
    draw_wire(ax, [(382, WALL_TRUNK_H - 3), (462, WALL_TRUNK_H - 3), (462, 115)], "C4")
    draw_junction(ax, 382, WALL_TRUNK_H - 3, "C4", "C4", size=4.6)

    # C5: wet area and dishwasher.
    draw_wire(ax, [(ENTRY_X, WALL_TRUNK_H - 11), (312, WALL_TRUNK_H - 11), (312, 55)], "C5")
    draw_wire(ax, [(312, WALL_TRUNK_H - 11), (352, WALL_TRUNK_H - 11), (352, 52)], "C5")
    draw_junction(ax, 312, WALL_TRUNK_H - 11, "C5 湿区", "C5", size=4.6)

    # C6: hob dedicated branch.
    draw_wire(ax, [(ENTRY_X, WALL_TRUNK_H - 19), (132, WALL_TRUNK_H - 19), (132, 52)], "C6")
    draw_junction(ax, 132, WALL_TRUNK_H - 19, "C6 灶具专线", "C6", size=4.5)

    add_label(ax, 255, 286, "每个回路画 L/N/PE 三根导体；同回路同管同走；墙面只做竖向下引", size=5.8, color="#555555")
    fig.tight_layout(pad=0.2)
    return fig, ax


def build_wiring_view_from_north_figure() -> tuple[plt.Figure, plt.Axes]:
    fig, ax = setup_full_wall_view("三线走线图 - 底部墙 / 进线与唯一开关", ROOM_W, figsize=(13.5, 7.0))
    add_label(ax, ROOM_W / 2, WALL_ELEVATION_H + 18, "总进线从门右侧开关位附近进入", size=8, color=COLORS["text_muted"])
    add_rect(ax, (BOTTOM_DOOR_X, 0), BOTTOM_DOOR_W, BOTTOM_DOOR_H, fc="#fff7f0", ec=COLORS["door_bottom"], lw=0.6, zorder=2)
    add_label(ax, BOTTOM_DOOR_X + BOTTOM_DOOR_W / 2, BOTTOM_DOOR_H / 2, f"门\n{BOTTOM_DOOR_W:g}W\nH={BOTTOM_DOOR_H:g}", size=8.0, color="#d95f02")
    mini_dim(ax, 0, BOTTOM_DOOR_X, -10, f"{BOTTOM_DOOR_X:g}", color=COLORS["blue"], size=7.0)
    mini_dim(ax, BOTTOM_DOOR_X, BOTTOM_DOOR_X + BOTTOM_DOOR_W, -10, f"门 {BOTTOM_DOOR_W:g}", color=COLORS["door_bottom"], size=7.0)
    mini_dim(ax, BOTTOM_DOOR_X + BOTTOM_DOOR_W, ROOM_W, -10, f"{ROOM_W - BOTTOM_DOOR_X - BOTTOM_DOOR_W:g}", color=COLORS["brown"], size=7.0)
    draw_wall_trunk(ax, ROOM_W, "上行到吊顶分线/过路区 H≈260")

    draw_electrical_point(ax, ENTRY_X, ENTRY_H, "唯一开关\n控制筒灯\nH=125", kind="switch", label_dx=28, label_dy=0, size=5.8)
    draw_junction(ax, ENTRY_X, ENTRY_H + 18, "厨房进线/分线起点", "IN", size=5.5)
    draw_wire(ax, [(ENTRY_X, ENTRY_H + 18), (ENTRY_X, WALL_TRUNK_H)], "IN", lw=1.4)
    draw_wire(ax, [(ENTRY_X - 8, ENTRY_H), (ENTRY_X - 8, WALL_TRUNK_H), (ENTRY_X + 55, WALL_TRUNK_H)], "L1", lw=1.0, conductors=("L",))
    add_label(ax, ENTRY_X + 42, 226, "L1 照明上行\nL经开关控制\nN/PE直达灯具", size=5.2, color=WIRE_COLORS["L1"], ha="left")
    add_label(ax, ENTRY_X - 88, 214, "插座/设备回路\nL/N/PE同管上吊顶\n电气上分回路", size=5.2, color=WIRE_COLORS["IN"], ha="right")
    draw_wiring_note(ax, 14, 222, "总进线从开关位进入：红=L火，蓝=N零，绿=PE地", width=230, height=24)
    fig.tight_layout(pad=0.2)
    return fig, ax


def build_wiring_view_from_west_figure() -> tuple[plt.Figure, plt.Axes]:
    fig, ax = setup_full_wall_view("三线走线图 - 西墙 / 冰箱与左备餐", ROOM_H, figsize=(9.5, 7.0))
    add_label(ax, 0, -42, "南 / 下侧", size=7, ha="left", color=COLORS["text_muted"])
    add_label(ax, ROOM_H, -42, "北 / 顶部台面", size=7, ha="right", color=COLORS["text_muted"])
    add_rect(ax, (32, 0), 70, LEFT_DOOR_H, fc="#fff7f7", ec=COLORS["door_left"], lw=0.48, zorder=2)
    add_label(ax, 67, LEFT_DOOR_H / 2, f"门\n70W\nH={LEFT_DOOR_H:g}", size=8, color=COLORS["door_left"])
    add_rect(ax, (110, 0), 90, 190, fc=COLORS["fridge"], ec=COLORS["fridge_edge"], lw=0.42, alpha=0.34, zorder=2)
    add_label(ax, 155, 120, "冰箱位", size=7, color=COLORS["fridge_edge"])
    draw_side_counter_profile(ax, TOP_Y0, ROOM_H, show_dim=False)
    draw_electrical_point(ax, 190, 45, "冰箱三孔\nH=40-50", label_dx=-20, label_dy=34, size=5.0)
    draw_socket_row(ax, 220, 115, 2, "左备餐 x2\nH=115", spacing=12, label_dy=18, size=5.0)
    draw_wall_trunk(ax, ROOM_H, "来自吊顶主干 H≈260")
    draw_wire(ax, [(ROOM_H, WALL_TRUNK_H + 4), (190, WALL_TRUNK_H + 4), (190, 45)], "C2")
    draw_wire(ax, [(ROOM_H, WALL_TRUNK_H - 5), (220, WALL_TRUNK_H - 5), (220, 115)], "C3")
    draw_junction(ax, 190, WALL_TRUNK_H + 4, "C2 冰箱", "C2", size=4.8)
    draw_junction(ax, 220, WALL_TRUNK_H - 5, "C3 左备餐", "C3", size=4.8)
    draw_wiring_note(ax, 8, 222, "C2/C3 管内均含 L/N/PE；墙面只做竖向下引", width=190, height=22)
    fig.tight_layout(pad=0.2)
    return fig, ax


def build_wiring_view_from_east_figure() -> tuple[plt.Figure, plt.Axes]:
    fig, ax = setup_full_wall_view("三线走线图 - 东墙 / 餐桌高低位插座", ROOM_H, figsize=(9.5, 7.0))
    add_label(ax, 0, -42, "北 / 顶部台面", size=7, ha="left", color=COLORS["text_muted"])
    add_label(ax, ROOM_H, -42, "南 / 下侧", size=7, ha="right", color=COLORS["text_muted"])
    draw_side_counter_profile(ax, 0, COUNTER_DEPTH)
    table_start = ROOM_H - TABLE_Y - TABLE_D
    add_rect(ax, (table_start, 0), TABLE_D, TABLE_HEIGHT, fc=COLORS["table"], ec=COLORS["table_edge"], lw=0.45, alpha=0.20, ls=(0, (5, 3)), zorder=2)
    add_label(ax, table_start + TABLE_D / 2, TABLE_HEIGHT / 2, "餐桌投影", size=6.2, color=COLORS["table_edge"])
    draw_socket_row(ax, EAST_POWER_ZONE_POS, HIGH_SOCKET_H, 2, "餐桌旁 x2\nH=105-120", label_dy=18, size=5.2)
    draw_socket_row(ax, EAST_POWER_ZONE_POS, LOW_SOCKET_H, 2, "低位 x2\nH=30-35", label_dy=-18, size=5.2)
    draw_wall_trunk(ax, ROOM_H, "来自吊顶主干 H≈260")
    draw_wire(ax, [(0, WALL_TRUNK_H), (EAST_POWER_ZONE_POS, WALL_TRUNK_H), (EAST_POWER_ZONE_POS, HIGH_SOCKET_H)], "C4")
    draw_wire(ax, [(EAST_POWER_ZONE_POS, HIGH_SOCKET_H), (EAST_POWER_ZONE_POS, LOW_SOCKET_H)], "C4")
    draw_junction(ax, EAST_POWER_ZONE_POS, WALL_TRUNK_H, "C4 餐桌/右区", "C4", size=4.8)
    add_label(ax, EAST_POWER_ZONE_POS + 18, 72, "C4: L/N/PE同管垂直下引\n高低位同墙分接", size=5.0, color=WIRE_COLORS["C4"], ha="left")
    draw_wiring_note(ax, 8, 222, "C4 管内含 L/N/PE；餐桌高低位同墙布置", width=190, height=22)
    fig.tight_layout(pad=0.2)
    return fig, ax


def build_wiring_view_from_ceiling_figure() -> tuple[plt.Figure, plt.Axes]:
    fig, ax = setup_horizontal_surface_view("三线走线图 - 天花板 / 主干与8个筒灯")
    add_rect(ax, (0, TOP_Y0), ROOM_W, COUNTER_DEPTH, fc="#f7f7f7", ec="#777777", lw=0.32, alpha=0.28, ls=(0, (5, 3)), zorder=2)
    add_label(ax, ROOM_W / 2, TOP_Y0 + COUNTER_DEPTH / 2, "顶部橱柜/台面投影", size=7, color=COLORS["text_muted"])
    add_rect(ax, (TABLE_X, TABLE_Y), TABLE_W, TABLE_D, fc=COLORS["table"], ec=COLORS["table_edge"], lw=0.35, alpha=0.16, ls=(0, (5, 3)), zorder=2)
    add_label(ax, TABLE_X + TABLE_W / 2, TABLE_Y + TABLE_D / 2, "餐桌投影", size=7, color=COLORS["table_edge"])
    draw_plan_doors_for_surface(ax)

    entry = (ENTRY_X, 0)
    j0 = (ENTRY_X, 150)
    draw_junction(ax, ENTRY_X, 11, "开关位进线", "IN", size=5.0)
    draw_wire(ax, [entry, j0], "IN", lw=1.3)
    draw_junction(ax, *j0, "吊顶分线点", "IN", size=5.0)

    light_ys = [ROOM_H - y for y in CEILING_LIGHT_Y_FROM_NORTH]
    for y in light_ys:
        draw_wire(ax, [j0, (ENTRY_X, y), (CEILING_LIGHT_XS[0], y), (CEILING_LIGHT_XS[-1], y)], "L1", lw=0.86)
        for x in CEILING_LIGHT_XS:
            draw_downlight(ax, x, y)
    for x in CEILING_LIGHT_XS:
        draw_wire(ax, [(x, light_ys[1]), (x, light_ys[0])], "L1", lw=0.36, ls=(0, (4, 5)), alpha=0.28, zorder=2)
    add_label(ax, 210, 152, "L1 照明: 8个筒灯\nL经开关；N/PE直达灯具", size=6.4, color=WIRE_COLORS["L1"])

    # Socket/device circuit bundle in ceiling, then split to north/west/east walls.
    draw_wire(ax, [j0, (ENTRY_X, 278), (ROOM_W, 278)], "C4", lw=0.72, ls=(0, (7, 3)))
    draw_wire(ax, [(ENTRY_X, 278), (ENTRY_X, ROOM_H)], "C3", lw=0.72, ls=(0, (7, 3)))
    draw_wire(ax, [(ENTRY_X - 10, 268), (0, 268), (0, 200)], "C2", lw=0.72, ls=(0, (7, 3)))
    draw_wire(ax, [(ENTRY_X - 16, 260), (ROOM_W / 2, 260), (ROOM_W / 2, ROOM_H)], "C5", lw=0.72, ls=(0, (7, 3)))
    draw_wire(ax, [(ENTRY_X - 22, 252), (132, 252), (132, ROOM_H)], "C6", lw=0.72, ls=(0, (7, 3)))
    add_label(ax, 392, 286, "至东墙餐桌/右台面", size=5.0, color=WIRE_COLORS["C4"])
    add_label(ax, 252, 287, "至顶部橱柜墙", size=5.0, color=WIRE_COLORS["C3"])
    add_label(ax, 70, 278, "至西墙冰箱/左备餐", size=5.0, color=WIRE_COLORS["C2"])
    add_label(ax, 158, 246, "至电磁炉专线", size=5.0, color=WIRE_COLORS["C6"])
    draw_wiring_legend(ax, 12, -160, compact=True)
    fig.tight_layout(pad=0.2)
    return fig, ax


def build_wiring_view_from_floor_figure() -> tuple[plt.Figure, plt.Axes]:
    fig, ax = setup_horizontal_surface_view("三线走线图 - 地面 / 不做地面横向强电")
    for x in range(50, ROOM_W, 50):
        ax.add_line(Line2D([x, x], [0, ROOM_H], color="#d0d0d0", lw=0.22, ls=(0, (3, 5)), zorder=1))
    for y in range(50, ROOM_H, 50):
        ax.add_line(Line2D([0, ROOM_W], [y, y], color="#d0d0d0", lw=0.22, ls=(0, (3, 5)), zorder=1))
    draw_plan_doors_for_surface(ax)
    add_rect(ax, (0, TOP_Y0), ROOM_W, COUNTER_DEPTH, fc="#eeeeee", ec="#777777", lw=0.30, alpha=0.18, ls=(0, (5, 3)), zorder=2)
    add_rect(ax, (TABLE_X, TABLE_Y), TABLE_W, TABLE_D, fc=COLORS["table"], ec=COLORS["table_edge"], lw=0.35, alpha=0.12, ls=(0, (5, 3)), zorder=2)
    draw_junction(ax, ENTRY_X, 8, "进线点投影", "IN", size=5.0)
    draw_wire(ax, [(ENTRY_X, 0), (ENTRY_X, 28)], "IN", lw=1.2)
    add_label(ax, ROOM_W / 2, ROOM_H / 2 + 22, "地面不布置横向强电管线", size=10.5, color="#555555", weight="bold")
    add_label(
        ax,
        ROOM_W / 2,
        ROOM_H / 2 - 8,
        "强电从开关位上墙进入吊顶，再沿墙/顶分配；\n避免厨房地面水汽、开槽和后期打孔风险。",
        size=7.0,
        color="#555555",
    )
    draw_wiring_legend(ax, 12, -160, compact=True)
    fig.tight_layout(pad=0.2)
    return fig, ax


def build_view_from_ceiling_figure() -> tuple[plt.Figure, plt.Axes]:
    fig, ax = setup_horizontal_surface_view("天花板图 - 8个筒灯与唯一开关")
    add_rect(ax, (0, TOP_Y0), ROOM_W, COUNTER_DEPTH, fc="#f7f7f7", ec="#777777", lw=0.32, alpha=0.34, ls=(0, (5, 3)), zorder=2)
    add_label(ax, ROOM_W / 2, TOP_Y0 + COUNTER_DEPTH / 2, "顶部台面投影", size=7, color=COLORS["text_muted"])

    add_rect(ax, (TABLE_X, TABLE_Y), TABLE_W, TABLE_D, fc=COLORS["table"], ec=COLORS["table_edge"], lw=0.35, alpha=0.20, ls=(0, (5, 3)), zorder=2)
    add_label(ax, TABLE_X + TABLE_W / 2, TABLE_Y + TABLE_D / 2, "餐桌投影", size=7, color=COLORS["table_edge"])

    light_ys = [ROOM_H - y for y in CEILING_LIGHT_Y_FROM_NORTH]
    for x in CEILING_LIGHT_XS:
        ax.add_line(Line2D([x, x], [light_ys[1], light_ys[0]], color="#d6a400", lw=0.22, ls=(0, (4, 5)), alpha=0.34, zorder=2))
    for y in light_ys:
        ax.add_line(Line2D([CEILING_LIGHT_XS[0], CEILING_LIGHT_XS[-1]], [y, y], color="#d6a400", lw=0.22, ls=(0, (4, 5)), alpha=0.34, zorder=2))
    for y in light_ys:
        for x in CEILING_LIGHT_XS:
            draw_downlight(ax, x, y)

    add_label(ax, ROOM_W / 2, 150, "筒灯 x8 / 2排 x 4\n单开关统一控制", size=7.2, color="#7a5b00")
    add_label(ax, 20, ROOM_H - 18, "灯位坐标原点: 左上角\nx=70/190/310/430 cm\ny=80/215 cm", size=5.4, color="#7a5b00", ha="left", va="top")
    mini_dim(ax, CEILING_LIGHT_XS[0], CEILING_LIGHT_XS[1], light_ys[0] + 18, "120", color="#d6a400", size=5.2)
    mini_dim(ax, CEILING_LIGHT_XS[1], CEILING_LIGHT_XS[2], light_ys[0] + 18, "120", color="#d6a400", size=5.2)
    mini_dim(ax, CEILING_LIGHT_XS[2], CEILING_LIGHT_XS[3], light_ys[0] + 18, "120", color="#d6a400", size=5.2)
    mini_vdim(ax, ROOM_W + 4, light_ys[0], ROOM_H, "80", color="#d6a400", size=5.2)
    mini_vdim(ax, ROOM_W + 4, light_ys[1], ROOM_H, "215", color="#d6a400", size=5.2)

    switch_x = BOTTOM_DOOR_X + BOTTOM_DOOR_W + 18
    switch_y = 8
    draw_electrical_point(
        ax,
        switch_x,
        switch_y,
        "唯一开关\n控制天花灯\nH=125",
        kind="switch",
        label_dx=50,
        label_dy=13,
        size=5.0,
    )
    ax.add_line(Line2D([switch_x, ROOM_W / 2], [switch_y + 5, 150], color=COLORS["switch"], lw=0.42, ls=(0, (4, 4)), alpha=0.65, zorder=3))
    draw_plan_doors_for_surface(ax)
    fig.tight_layout(pad=0.2)
    return fig, ax


def build_view_from_floor_figure() -> tuple[plt.Figure, plt.Axes]:
    fig, ax = setup_horizontal_surface_view("地面图 - 地面完成面与门洞")
    for x in range(50, ROOM_W, 50):
        ax.add_line(Line2D([x, x], [0, ROOM_H], color="#d0d0d0", lw=0.22, ls=(0, (3, 5)), zorder=1))
    for y in range(50, ROOM_H, 50):
        ax.add_line(Line2D([0, ROOM_W], [y, y], color="#d0d0d0", lw=0.22, ls=(0, (3, 5)), zorder=1))
    add_label(ax, ROOM_W / 2, ROOM_H / 2, "地面完成面\n500 x 300 cm", size=10, color=COLORS["text_muted"])

    add_rect(ax, (0, TOP_Y0), ROOM_W, COUNTER_DEPTH, fc="#eeeeee", ec="#777777", lw=0.30, alpha=0.22, ls=(0, (5, 3)), zorder=2)
    add_label(ax, ROOM_W / 2, TOP_Y0 + COUNTER_DEPTH / 2, "固定柜体投影", size=7, color=COLORS["text_muted"])
    add_rect(ax, (0, 110), 75, 130, fc="#eeeeee", ec="#777777", lw=0.30, alpha=0.22, ls=(0, (5, 3)), zorder=2)
    add_label(ax, 37.5, 175, "左侧固定区投影", size=6.6, color=COLORS["text_muted"], rotation=90)

    add_rect(ax, (TABLE_X, TABLE_Y), TABLE_W, TABLE_D, fc=COLORS["table"], ec=COLORS["table_edge"], lw=0.35, alpha=0.18, ls=(0, (5, 3)), zorder=2)
    add_label(ax, TABLE_X + TABLE_W / 2, TABLE_Y + TABLE_D / 2, "餐桌投影", size=7, color=COLORS["table_edge"])
    draw_plan_doors_for_surface(ax)
    fig.tight_layout(pad=0.2)
    return fig, ax


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    outputs = [
        ("kitchen_floor_plan.png", build_floor_plan_figure),
        ("view_from_south.png", build_view_from_south_figure),
        ("view_from_north.png", build_view_from_north_figure),
        ("view_from_west.png", build_view_from_west_figure),
        ("view_from_east.png", build_view_from_east_figure),
        ("view_from_ceiling.png", build_view_from_ceiling_figure),
        ("view_from_floor.png", build_view_from_floor_figure),
        ("wiring_view_from_south.png", build_wiring_view_from_south_figure),
        ("wiring_view_from_north.png", build_wiring_view_from_north_figure),
        ("wiring_view_from_west.png", build_wiring_view_from_west_figure),
        ("wiring_view_from_east.png", build_wiring_view_from_east_figure),
        ("wiring_view_from_ceiling.png", build_wiring_view_from_ceiling_figure),
        ("wiring_view_from_floor.png", build_wiring_view_from_floor_figure),
    ]

    expected = {name for name, _ in outputs}
    for stale in OUTPUT_DIR.glob("*.png"):
        if stale.name not in expected:
            stale.unlink()

    for filename, builder in outputs:
        fig, _ = builder()
        path = OUTPUT_DIR / filename
        fig.savefig(path, bbox_inches="tight", facecolor="white", dpi=OUTPUT_DPI)
        plt.close(fig)
        print(f"Saved {path}")


if __name__ == "__main__":
    main()
