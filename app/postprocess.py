"""
Post-processing: applies brand-consistent overlay and title text to generated images.
Uses Pillow to add teal gradient overlay + Comfortaa title text.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Brand colors as RGB tuples
TEAL = (0, 179, 143)        # #00B38F
BURGUNDY = (150, 15, 55)    # #960f37
WHITE = (255, 255, 255)

# Font paths (Comfortaa — Endo Health's brand font)
FONT_DIR = Path(__file__).parent / "static" / "fonts"
FONT_BOLD = FONT_DIR / "Comfortaa-Bold.ttf"
FONT_REGULAR = FONT_DIR / "Comfortaa-Regular.ttf"

# Target dimensions
TARGET_WIDTH = 1792
TARGET_HEIGHT = 1024


def _load_font(bold: bool = True, size: int = 48) -> ImageFont.FreeTypeFont:
    """Load Comfortaa font, fallback to default if not found."""
    font_path = FONT_BOLD if bold else FONT_REGULAR
    try:
        return ImageFont.truetype(str(font_path), size)
    except (OSError, IOError):
        return ImageFont.load_default()


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Word-wrap text to fit within max_width pixels."""
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = font.getbbox(test_line)
        text_width = bbox[2] - bbox[0]

        if text_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines or [text]


def apply_brand_overlay(
    image_path: Path,
    title: str,
    output_path: Path | None = None,
) -> Path:
    """Apply brand overlay to an image: gradient + title text.

    Args:
        image_path: Path to the raw DALL-E generated image.
        title: Blog post title to render on the image.
        output_path: Where to save. Defaults to same path with _final suffix.

    Returns:
        Path to the processed image.
    """
    if output_path is None:
        output_path = image_path.with_stem(image_path.stem + "_final")

    # Load and resize to target dimensions
    img = Image.open(image_path).convert("RGBA")
    img = img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.LANCZOS)

    # Create gradient overlay (bottom 35% of image)
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)

    gradient_start = int(TARGET_HEIGHT * 0.55)
    for y in range(gradient_start, TARGET_HEIGHT):
        progress = (y - gradient_start) / (TARGET_HEIGHT - gradient_start)
        alpha = int(200 * progress)  # 0 → 200 opacity
        draw_overlay.line(
            [(0, y), (TARGET_WIDTH, y)],
            fill=(*TEAL, alpha),
        )

    img = Image.alpha_composite(img, overlay)

    # Add thin teal accent line at top
    accent = Image.new("RGBA", (TARGET_WIDTH, 6), (*TEAL, 230))
    img.paste(accent, (0, 0), accent)

    # Render title text
    draw = ImageDraw.Draw(img)
    font = _load_font(bold=True, size=52)
    max_text_width = TARGET_WIDTH - 160  # 80px padding each side

    lines = _wrap_text(title, font, max_text_width)

    # Calculate vertical position (centered in bottom gradient area)
    line_height = 68
    total_text_height = len(lines) * line_height
    text_y = TARGET_HEIGHT - total_text_height - 60  # 60px from bottom

    for line in lines:
        bbox = font.getbbox(line)
        text_width = bbox[2] - bbox[0]
        text_x = (TARGET_WIDTH - text_width) // 2  # Center horizontally

        # Shadow for readability
        draw.text((text_x + 2, text_y + 2), line, font=font, fill=(0, 0, 0, 120))
        # Main text
        draw.text((text_x, text_y), line, font=font, fill=WHITE)
        text_y += line_height

    # Convert to RGB and save as WebP
    final = img.convert("RGB")
    output_path = output_path.with_suffix(".webp")
    final.save(output_path, "WEBP", quality=90)

    return output_path
