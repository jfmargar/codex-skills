#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


GEORGIA_BOLD = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
GEORGIA = "/System/Library/Fonts/Supplemental/Georgia.ttf"
GILL_SANS = "/System/Library/Fonts/Supplemental/GillSans.ttc"


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size)


def vertical_gradient(size: tuple[int, int], top: str, bottom: str) -> Image.Image:
    width, height = size
    top_rgb = hex_to_rgb(top)
    bottom_rgb = hex_to_rgb(bottom)
    base = Image.new("RGB", size, top_rgb)
    draw = ImageDraw.Draw(base)
    for y in range(height):
        t = y / max(1, height - 1)
        color = tuple(int(top_rgb[i] * (1 - t) + bottom_rgb[i] * t) for i in range(3))
        draw.line([(0, y), (width, y)], fill=color)
    return base


def add_radial_glow(base: Image.Image, center: tuple[int, int], radius: int, color: str, alpha: int) -> None:
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    cx, cy = center
    rgb = hex_to_rgb(color)
    for step in range(radius, 0, -8):
        strength = max(0, int(alpha * (step / radius) ** 2))
        draw.ellipse((cx - step, cy - step, cx + step, cy + step), fill=(*rgb, strength))
    base.alpha_composite(glow)


def round_corners(image: Image.Image, radius: int) -> Image.Image:
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, image.width, image.height), radius=radius, fill=255)
    rounded = Image.new("RGBA", image.size, (0, 0, 0, 0))
    rounded.paste(image, (0, 0), mask)
    return rounded


def add_shadow(base: Image.Image, box: tuple[int, int, int, int], radius: int) -> None:
    x, y, w, h = box
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    draw.rounded_rectangle((x, y + 18, x + w, y + h + 18), radius=radius, fill=(46, 31, 17, 60))
    base.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(28)))


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def line_height(font: ImageFont.FreeTypeFont) -> int:
    box = font.getbbox("Ag")
    return box[3] - box[1]


def draw_copy(canvas: Image.Image, title: str, subtitle: str, device: str, brand: str) -> int:
    draw = ImageDraw.Draw(canvas)
    width, height = canvas.size
    if device == "iphone":
        left = int(width * 0.082)
        top = int(height * 0.078)
        max_width = int(width * 0.78)
        title_font = load_font(GEORGIA_BOLD, int(width * 0.074))
        subtitle_font = load_font(GILL_SANS, int(width * 0.039))
        kicker_font = load_font(GEORGIA, int(width * 0.028))
    else:
        left = int(width * 0.073)
        top = int(height * 0.067)
        max_width = int(width * 0.64)
        title_font = load_font(GEORGIA_BOLD, int(width * 0.057))
        subtitle_font = load_font(GILL_SANS, int(width * 0.026))
        kicker_font = load_font(GEORGIA, int(width * 0.020))

    draw.text((left, top), brand, font=kicker_font, fill="#A06E37")
    top += int(line_height(kicker_font) * 1.8)
    for line in wrap_text(draw, title, title_font, max_width):
        draw.text((left, top), line, font=title_font, fill="#1E1710")
        top += int(line_height(title_font) * 1.08)
    top += int(height * 0.012)
    for line in wrap_text(draw, subtitle, subtitle_font, max_width):
        draw.text((left, top), line, font=subtitle_font, fill="#5C4B3D")
        top += int(line_height(subtitle_font) * 1.28)
    return top


def place_screenshot(canvas: Image.Image, screenshot: Image.Image, text_bottom: int, device: str) -> None:
    width, height = canvas.size
    if device == "iphone":
        target_width = int(width * 0.80)
        top_margin = int(height * 0.05)
        bottom_margin = int(height * 0.04)
    else:
        target_width = int(width * 0.78)
        top_margin = int(height * 0.045)
        bottom_margin = int(height * 0.04)

    scale = target_width / screenshot.width
    target_height = int(screenshot.height * scale)
    max_height = height - text_bottom - top_margin - bottom_margin
    if target_height > max_height:
        scale = max_height / screenshot.height
        target_width = int(screenshot.width * scale)
        target_height = int(screenshot.height * scale)

    x = (width - target_width) // 2
    y = text_bottom + top_margin
    resized = screenshot.resize((target_width, target_height), Image.Resampling.LANCZOS).convert("RGBA")
    rounded = round_corners(resized, int(target_width * 0.05))
    add_shadow(canvas, (x, y, target_width, target_height), radius=int(target_width * 0.05))
    canvas.alpha_composite(rounded, (x, y))


def render_shot(entry: dict, source_root: Path, output_root: Path, brand: str) -> Path:
    source = Image.open(source_root / entry["source"]).convert("RGBA")
    size = tuple(entry["size"])
    device = entry["device"]
    canvas = vertical_gradient(size, top="#F8F0E4", bottom="#EEDFC9").convert("RGBA")
    add_radial_glow(canvas, (int(size[0] * 0.12), int(size[1] * 0.16)), int(size[0] * 0.35), "#F7D9A4", 70)
    add_radial_glow(canvas, (int(size[0] * 0.84), int(size[1] * 0.78)), int(size[0] * 0.30), "#D9C0A0", 55)
    add_radial_glow(canvas, (int(size[0] * 0.72), int(size[1] * 0.18)), int(size[0] * 0.24), "#FFF9F0", 50)
    text_bottom = draw_copy(canvas, entry["title"], entry["subtitle"], device, brand)
    place_screenshot(canvas, source, text_bottom, device)

    target_dir = output_root / device
    target_dir.mkdir(parents=True, exist_ok=True)
    output_path = target_dir / entry["output"]
    temp_path = output_path.with_suffix(".tmp.png")
    canvas.convert("RGB").save(temp_path, format="PNG")
    temp_path.replace(output_path)
    return output_path


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: generate_marketing_shots.py <spec.json>", file=sys.stderr)
        return 2

    spec_path = Path(sys.argv[1]).resolve()
    spec = json.loads(spec_path.read_text())
    source_root = Path(spec["source_root"]).resolve()
    output_root = Path(spec["output_root"]).resolve()
    brand = spec.get("brand", "App")
    outputs = [render_shot(entry, source_root, output_root, brand) for entry in spec["shots"]]
    for output in outputs:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
