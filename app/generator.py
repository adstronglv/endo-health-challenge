"""
Core image generator: prompt engineering + DALL-E 3 integration.
Generates brand-consistent blog header images for Endo Health (endometriose.app).
"""

import os
from pathlib import Path

import httpx
from openai import OpenAI

# Endo Health brand identity
BRAND = {
    "primary": "#00B38F",      # Teal
    "secondary": "#960f37",    # Burgundy
    "accent_light": "#E8D5E0", # Soft pink/lavender
    "accent_purple": "#7B5EA7", # Purple accent
    "white": "#FFFFFF",
    "font": "Comfortaa",
}

# Style prefix applied to EVERY prompt for visual consistency
STYLE_PREFIX = (
    "Modern, feminine healthcare blog header image. "
    "Soft digital illustration style — clean, warm, and approachable. "
    "Color palette: muted teal (#00B38F), soft rose-pink, warm blush, "
    "dusty mauve, cream white, and light gray. Balanced and harmonious. "
    "Clean composition with whitespace and soft gradients. "
    "Gentle, rounded shapes — professional yet warm. "
    "Absolutely no text, letters, or words in the image. "
    "Only soft, gentle objects — flowers, leaves, light, fabric, nature. "
    "Warm, hopeful, feminine mood — empowering and supportive. "
    "High quality, 16:9 landscape format, suitable as a blog header image. "
)

# Blog titles mapped to topic-specific visual descriptions
BLOG_PROMPTS: list[dict[str, str]] = [
    {
        "title": "Künstliche Wechseljahre – was steckt dahinter und was kannst du tun?",
        "visual": (
            "A confident woman in her 30s with a slim figure, sitting cross-legged "
            "on a cozy armchair, holding a warm cup of tea. She wears a comfortable "
            "sweater. Behind her, a window with golden autumn light. "
            "On one side autumn leaves (orange, gold), on the other side spring blossoms (pink). "
            "Symbolizing change and renewal. Cozy, empowering, peaceful."
        ),
    },
    {
        "title": "Endometriose kennt kein Alter",
        "visual": (
            "Three women of different ages (young, middle-aged, older) standing together "
            "in solidarity, connected by a flowing teal ribbon. Soft, warm background with "
            "abstract circular shapes representing life stages. Inclusive, empowering, "
            "diverse representation. Gentle light and warm tones."
        ),
    },
    {
        "title": "Früherkennung bei Endometriose",
        "visual": (
            "A woman and a friendly female doctor having a warm conversation "
            "in a bright, modern office with plants and natural light. "
            "The doctor is listening attentively, both are smiling gently. "
            "A soft magnifying glass icon glows subtly in the background. "
            "Trust, care, and early attention — warm and reassuring."
        ),
    },
    {
        "title": "Umweltfaktoren, Genetik und ihre Rolle bei Endometriose",
        "visual": (
            "A beautiful, abstract split composition: on the left, a stylized DNA helix "
            "made of soft teal and rose ribbons, intertwined with flowers. "
            "On the right, lush green leaves, water droplets, and clean air swirls. "
            "Both sides connected by gentle flowing lines. "
            "Nature meets science — elegant, feminine, and harmonious."
        ),
    },
    {
        "title": "Autoimmunerkrankungen und Endometriose",
        "visual": (
            "A woman gently holding her hands over her heart, surrounded by soft "
            "glowing protective light in rose and blush tones. Delicate, abstract "
            "butterfly-like shapes floating around her — symbolizing the immune system. "
            "Soft botanical elements (peonies, eucalyptus). "
            "Nurturing, protective atmosphere — the body caring for itself."
        ),
    },
    {
        "title": "Endometriose mit künstlicher Intelligenz früher erkennen",
        "visual": (
            "A woman looking at a modern, elegant tablet screen that shows soft, "
            "glowing data visualizations in rose and teal. Gentle flowing lines "
            "connecting abstract dots — representing AI analysis. "
            "Warm, sunlit room with plants. The technology feels friendly and personal, "
            "not cold or clinical. Hope and innovation in a feminine setting."
        ),
    },
    {
        "title": "Yselty® – Neu zugelassener Wirkstoff bei Endometriose",
        "visual": (
            "A stylized pharmaceutical scene: a soft-glowing capsule or pill surrounded "
            "by molecular structures in teal and purple. Gentle light rays emanating outward "
            "suggesting breakthrough and hope. Clean laboratory aesthetic with warm undertones. "
            "Professional yet approachable — science serving patients."
        ),
    },
    {
        "title": "Anschlussheilbehandlung (AHB) und Reha bei Endometriose",
        "visual": (
            "A woman sitting peacefully on a soft blanket in a sunlit garden, "
            "doing gentle breathing exercises. Surrounded by soft pink roses, "
            "lavender, and warm morning light. A cup of herbal tea beside her. "
            "Barefoot on grass, eyes closed, serene smile. "
            "Healing, recovery, and self-care in nature — deeply feminine and peaceful."
        ),
    },
    {
        "title": "Endometriose: Fakten statt Mythen",
        "visual": (
            "A symbolic split scene: on the left, soft grey clouds and fading question marks "
            "dissolving into mist. On the right, warm golden light breaking through "
            "with an open book, gentle checkmarks, and blooming flowers. "
            "The transition from confusion to clarity and knowledge. "
            "Empowering, educational, hopeful — darkness giving way to light."
        ),
    },
    {
        "title": "Endo March: Was steht an? Wie kann ich aktiv werden?",
        "visual": (
            "A diverse group of people walking together in a peaceful march, some holding "
            "yellow endometriosis awareness ribbons. Teal and yellow color accents. "
            "Urban park setting with spring flowers and warm sunlight. "
            "Community, solidarity, and action — uplifting and energizing atmosphere."
        ),
    },
]


def build_prompt(blog_entry: dict[str, str]) -> str:
    """Build a complete DALL-E 3 prompt from style prefix + topic-specific visual."""
    return f"{STYLE_PREFIX}\nTopic: {blog_entry['visual']}"


def get_client() -> OpenAI:
    """Create OpenAI client from environment."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY nicht gesetzt. "
            "Bitte in .env Datei eintragen oder als Umgebungsvariable setzen."
        )
    return OpenAI(api_key=api_key)


async def generate_image(
    client: OpenAI,
    prompt: str,
    size: str = "1792x1024",
    quality: str = "hd",
) -> str:
    """Generate a single image via DALL-E 3. Returns the image URL."""
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        quality=quality,
        n=1,
    )
    return response.data[0].url


async def download_image(url: str, output_path: Path) -> Path:
    """Download an image from URL to local file."""
    async with httpx.AsyncClient() as http:
        resp = await http.get(url, timeout=60.0)
        resp.raise_for_status()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(resp.content)
    return output_path
