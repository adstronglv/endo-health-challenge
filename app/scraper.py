"""
Blog title scraper for endometriose.app.
Fetches actual blog titles from the Endo Health website.
"""

import httpx
from bs4 import BeautifulSoup


BLOG_URL = "https://endometriose.app/aktuelles-2/"


async def scrape_blog_titles(url: str = BLOG_URL, limit: int = 10) -> list[str]:
    """Scrape blog post titles from endometriose.app.

    Args:
        url: Blog listing page URL.
        limit: Maximum number of titles to return.

    Returns:
        List of blog post titles.
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, follow_redirects=True)
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Try common WordPress blog title selectors
        titles = []
        for selector in ["h2.entry-title a", "h2.wp-block-post-title a", "h2 a", ".entry-title a"]:
            elements = soup.select(selector)
            for el in elements:
                text = el.get_text(strip=True)
                if text and len(text) > 10:
                    titles.append(text)
            if titles:
                break

        # Deduplicate while preserving order
        seen = set()
        unique = []
        for t in titles:
            if t not in seen:
                seen.add(t)
                unique.append(t)

        return unique[:limit]

    except Exception as e:
        print(f"Scraping fehlgeschlagen ({e}), verwende gespeicherte Titel.")
        return []
