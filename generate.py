#!/usr/bin/env python3
"""
Endo Health Blog Header Image Generator
========================================
Generates 10 brand-consistent blog header images for endometriose.app
using DALL-E 3 with post-processing for visual consistency.

Usage:
    python generate.py              # Generate all 10 images
    python generate.py --dry-run    # Show prompts without generating
    python generate.py --scrape     # Scrape live titles from website

Author: Aliaksandr Belafostau
"""

import argparse
import asyncio
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

# Load environment before imports that need it
load_dotenv()

from app.generator import BLOG_PROMPTS, build_prompt, get_client, generate_image, download_image
from app.postprocess import apply_brand_overlay


OUTPUT_DIR = Path(__file__).parent / "output"


async def generate_all(dry_run: bool = False) -> list[Path]:
    """Generate all blog header images.

    Args:
        dry_run: If True, only print prompts without generating images.

    Returns:
        List of paths to generated images.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results = []

    if dry_run:
        print("\n=== DRY RUN — Prompts ohne Bildgenerierung ===\n")
        for i, entry in enumerate(BLOG_PROMPTS, 1):
            prompt = build_prompt(entry)
            print(f"[{i}/10] {entry['title']}")
            print(f"  Prompt: {prompt[:150]}...")
            print()
        return []

    client = get_client()
    total = len(BLOG_PROMPTS)
    start_time = time.time()

    print(f"\n{'='*60}")
    print(f"  Endo Health Blog Header Generator")
    print(f"  {total} Bilder werden generiert (DALL-E 3 HD)")
    print(f"{'='*60}\n")

    for i, entry in enumerate(BLOG_PROMPTS, 1):
        title = entry["title"]
        prompt = build_prompt(entry)

        print(f"[{i}/{total}] {title}")
        print(f"  -> Generiere Bild...", end=" ", flush=True)

        try:
            # Generate via DALL-E 3
            image_url = await generate_image(client, prompt)
            print("OK", flush=True)

            # Download raw image
            raw_path = OUTPUT_DIR / f"{i:02d}_raw.png"
            print(f"  -> Downloade...", end=" ", flush=True)
            await download_image(image_url, raw_path)
            print("OK", flush=True)

            # Apply brand overlay
            print(f"  -> Brand-Overlay...", end=" ", flush=True)
            final_path = apply_brand_overlay(
                raw_path,
                title,
                output_path=OUTPUT_DIR / f"{i:02d}_header",
            )
            print(f"OK -> {final_path.name}", flush=True)

            results.append(final_path)
            print()

        except Exception as e:
            print(f"FEHLER: {e}")
            print()
            continue

    elapsed = time.time() - start_time

    print(f"{'='*60}")
    print(f"  Fertig! {len(results)}/{total} Bilder generiert")
    print(f"  Dauer: {elapsed:.0f}s | Ausgabe: {OUTPUT_DIR.absolute()}")
    print(f"{'='*60}\n")

    # Print summary
    for path in results:
        print(f"  {path.name}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Generiert Blog-Header-Bilder fuer Endo Health (endometriose.app)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Nur Prompts anzeigen, keine Bilder generieren",
    )
    args = parser.parse_args()

    try:
        results = asyncio.run(generate_all(dry_run=args.dry_run))
        if not args.dry_run and results:
            print(f"\n  Oeffne {OUTPUT_DIR.absolute()} um die Bilder zu sehen.")
    except KeyboardInterrupt:
        print("\n\nAbgebrochen.")
        sys.exit(1)
    except RuntimeError as e:
        print(f"\nFehler: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
