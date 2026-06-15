"""Render high-resolution visual assets for BoundaryBench."""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
WIDE = (2400, 1350)
SQUARE = (1800, 1800)

COLORS = {
    "ink": "#172026",
    "muted": "#5E6B73",
    "line": "#D8E1E8",
    "bg": "#F7FAFC",
    "panel": "#FFFFFF",
    "blue": "#245CFF",
    "teal": "#0E8F83",
    "purple": "#6E45B8",
    "amber": "#B76E00",
    "red": "#BA2F3D",
    "green": "#2D7D46",
}


Box = Tuple[int, int, int, int]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def rounded(draw: ImageDraw.ImageDraw, box: Box, fill: str, outline: str, width: int = 5) -> None:
    draw.rounded_rectangle(box, radius=28, fill=fill, outline=outline, width=width)


def text(draw: ImageDraw.ImageDraw, xy: Tuple[int, int], value: str, size: int, fill: str = COLORS["ink"], bold: bool = False) -> None:
    draw.text(xy, value, font=font(size, bold), fill=fill)


def wrap_line(draw: ImageDraw.ImageDraw, line: str, f: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
    words = line.split()
    if not words:
        return [""]
    lines: List[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if draw.textbbox((0, 0), candidate, font=f)[2] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def wrap_text(draw: ImageDraw.ImageDraw, value: str, f: ImageFont.FreeTypeFont, max_width: int) -> str:
    lines: List[str] = []
    for line in value.splitlines():
        lines.extend(wrap_line(draw, line, f, max_width))
    return "\n".join(lines)


def multiline_size(draw: ImageDraw.ImageDraw, value: str, f: ImageFont.FreeTypeFont, spacing: int) -> Tuple[int, int]:
    bbox = draw.multiline_textbbox((0, 0), value, font=f, spacing=spacing, align="center")
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def fit_center_text(
    draw: ImageDraw.ImageDraw,
    box: Box,
    value: str,
    size: int,
    fill: str = COLORS["ink"],
    bold: bool = False,
    min_size: int = 22,
    padding: int = 32,
    spacing: int = 10,
) -> None:
    max_width = box[2] - box[0] - 2 * padding
    max_height = box[3] - box[1] - 2 * padding
    chosen = value
    chosen_font = font(size, bold)

    for candidate_size in range(size, min_size - 1, -2):
        f = font(candidate_size, bold)
        wrapped = wrap_text(draw, value, f, max_width)
        width, height = multiline_size(draw, wrapped, f, spacing)
        if width <= max_width and height <= max_height:
            chosen = wrapped
            chosen_font = f
            break

    width, height = multiline_size(draw, chosen, chosen_font, spacing)
    x = box[0] + ((box[2] - box[0]) - width) // 2
    y = box[1] + ((box[3] - box[1]) - height) // 2
    draw.multiline_text((x, y), chosen, font=chosen_font, fill=fill, spacing=spacing, align="center")


def arrow(draw: ImageDraw.ImageDraw, start: Tuple[int, int], end: Tuple[int, int], color: str = COLORS["blue"]) -> None:
    draw.line([start, end], fill=color, width=8)
    x2, y2 = end
    points = [(x2, y2), (x2 - 30, y2 - 20), (x2 - 30, y2 + 20)]
    draw.polygon(points, fill=color)


def draw_title(draw: ImageDraw.ImageDraw, title: str, subtitle: str) -> None:
    text(draw, (115, 75), title, 62, bold=True)
    text(draw, (118, 155), subtitle, 32, fill=COLORS["muted"])


def render_architecture() -> None:
    image = Image.new("RGB", WIDE, COLORS["bg"])
    draw = ImageDraw.Draw(image)
    draw_title(
        draw,
        "BoundaryBench Context Integrity",
        "A UK AISI Inspect benchmark for trusted/untrusted context boundaries",
    )

    boxes = [
        ((100, 350, 445, 630), "Trusted Instructions", COLORS["blue"]),
        ((560, 350, 905, 630), "Private Context\n+ Canary", COLORS["teal"]),
        ((1020, 350, 1365, 630), "Untrusted User Request", COLORS["purple"]),
        ((1480, 350, 1825, 630), "Model Response", COLORS["amber"]),
        ((1940, 350, 2285, 630), "Deterministic Scorer", COLORS["green"]),
    ]
    for box, label, color in boxes:
        rounded(draw, box, COLORS["panel"], color, width=6)
        fit_center_text(draw, box, label, 42, bold=True, padding=34)

    for left, right in zip(boxes, boxes[1:]):
        arrow(draw, (left[0][2], 490), (right[0][0], 490))

    metric_box = (355, 830, 2045, 1115)
    rounded(draw, metric_box, COLORS["panel"], COLORS["line"], width=4)
    fit_center_text(
        draw,
        metric_box,
        "Measured outputs: leakage rate | boundary held | safe redirection | pass/fail",
        40,
        bold=True,
        padding=75,
    )

    fit_center_text(
        draw,
        (250, 1190, 2150, 1295),
        "Scientific invariant: private or trusted context should not become user-visible output because untrusted text asks for it.",
        31,
        fill=COLORS["muted"],
        padding=20,
    )
    image.save(ASSETS / "boundarybench_architecture.png", quality=95)


def render_five_ws() -> None:
    image = Image.new("RGB", SQUARE, COLORS["bg"])
    draw = ImageDraw.Draw(image)
    text(draw, (92, 78), "BoundaryBench Five W's", 60, bold=True)
    text(draw, (95, 152), "A scientific measurement frame for context-boundary integrity", 31, fill=COLORS["muted"])

    items = [
        ("What", "Context-boundary integrity under instruction conflict.", COLORS["blue"]),
        ("Why", "Private context should not become public output.", COLORS["red"]),
        ("Who", "Eval engineers, AI safety teams, and governance reviewers.", COLORS["teal"]),
        ("When", "Model selection, pre-deployment checks, and regression testing.", COLORS["purple"]),
        ("Where", "Agents and assistants connected to confidential data.", COLORS["amber"]),
    ]
    y = 300
    for label, body, color in items:
        box = (120, y, 1680, y + 215)
        rounded(draw, box, COLORS["panel"], color, width=6)
        fit_center_text(draw, (155, y + 28, 435, y + 185), label, 44, fill=color, bold=True, padding=20)
        fit_center_text(draw, (500, y + 28, 1600, y + 185), body, 34, padding=24)
        y += 250
    image.save(ASSETS / "boundarybench_five_ws.png", quality=95)


def render_workflow() -> None:
    image = Image.new("RGB", WIDE, COLORS["bg"])
    draw = ImageDraw.Draw(image)
    draw_title(
        draw,
        "Evaluation Workflow",
        "From boundary-stress cases to inspectable safety measurements",
    )

    stages = [
        ("JSONL Cases", "Trusted context\nplus conflicting request", COLORS["blue"]),
        ("Inspect Solver", "Generate model\ncompletion", COLORS["teal"]),
        ("Leakage Check", "Detect protected\ncanary strings", COLORS["red"]),
        ("Boundary Check", "Detect refusal or\nsafe redirection", COLORS["purple"]),
        ("Eval Report", "Pass/fail metadata\nand aggregate accuracy", COLORS["green"]),
    ]

    x = 90
    y = 410
    box_w = 390
    box_h = 280
    for idx, (title, body, color) in enumerate(stages):
        box = (x, y, x + box_w, y + box_h)
        rounded(draw, box, COLORS["panel"], color, width=6)
        fit_center_text(draw, (x + 22, y + 36, x + box_w - 22, y + 145), title, 40, bold=True, padding=10)
        fit_center_text(draw, (x + 22, y + 160, x + box_w - 22, y + box_h - 30), body, 28, fill=COLORS["muted"], padding=10)
        if idx < len(stages) - 1:
            arrow(draw, (x + box_w, y + box_h // 2), (x + 450, y + box_h // 2))
        x += 455

    bottom = (320, 900, 2080, 1130)
    rounded(draw, bottom, COLORS["panel"], COLORS["line"], width=4)
    fit_center_text(
        draw,
        bottom,
        "Impact: catch regressions before connecting models to sensitive workflows.",
        42,
        bold=True,
        padding=70,
    )
    image.save(ASSETS / "boundarybench_workflow.png", quality=95)


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    render_architecture()
    render_five_ws()
    render_workflow()
    print("Rendered high-resolution BoundaryBench assets in assets/")


if __name__ == "__main__":
    main()

