# Endo Health — Blog Header Image Generator

Automatisierte Generierung von **markenkonsistenten Blog-Header-Bildern** fuer [endometriose.app](https://endometriose.app).

## Ergebnis

10 Blog-Header-Bilder im Endo Health Branding (Teal/Burgundy, Comfortaa-Schrift, medizinisch-warmherzig), generiert aus echten Blog-Titeln der Website.

## Workflow

```
Blog-Titel → Prompt Engineering → DALL-E 3 (HD) → Post-Processing → Fertiges Header-Bild
```

### 1. Prompt Engineering
Jedes Bild erhaelt den **gleichen Style-Prefix** (Farben, Komposition, Aesthetik) plus eine **titelspezifische visuelle Beschreibung**. Das sorgt fuer konsistenten Stil bei unterschiedlichem Inhalt.

### 2. Bildgenerierung (DALL-E 3)
- Modell: `dall-e-3` im HD-Modus
- Aufloesung: 1792 x 1024 (16:9 Landscape)
- Konsistenz durch identischen Style-Prefix in jedem Prompt

### 3. Post-Processing (Pillow)
Einheitliches Brand-Overlay auf jedes Bild:
- Teal-Gradient (#00B38F) im unteren Bilddrittel
- Blog-Titel in **Comfortaa Bold** (Endo Health Brand-Font)
- Teal-Akzentlinie am oberen Bildrand
- Export als WebP (<300KB pro Bild)

## Schnellstart

```bash
# 1. Abhaengigkeiten installieren
pip install -r requirements.txt

# 2. API-Key setzen
cp .env.example .env
# OPENAI_API_KEY in .env eintragen

# 3. Bilder generieren (CLI)
python generate.py

# 4. Bonus: Web-App starten
uvicorn app.main:app --port 8090
# Browser: http://localhost:8090
```

### Optionen

```bash
python generate.py              # Alle 10 Bilder generieren
python generate.py --dry-run    # Nur Prompts anzeigen (kein API-Aufruf)
```

## Architektur

```
endo-health-challenge/
  generate.py          ← CLI-Skript (Haupteinstieg)
  app/
    generator.py       ← Prompt-Bau + DALL-E 3 Integration
    postprocess.py     ← Pillow: Brand-Overlay + Titel-Text
    scraper.py         ← Blog-Titel von endometriose.app scrapen
    main.py            ← FastAPI Web-App (Bonus)
    templates/
      index.html       ← Web-UI (Tailwind CSS + SSE)
    static/
      fonts/           ← Comfortaa Bold/Regular (TTF)
      output/          ← Generierte Bilder
```

## Technologie-Entscheidungen

| Entscheidung | Wahl | Grund |
|---|---|---|
| **Image API** | DALL-E 3 | Beste Prompt-Treue, einfache Integration, zuverlaessige Qualitaet |
| **Konsistenz** | Style-Prefix + Post-Processing | Identischer Prompt-Prefix + Pillow-Overlay = visuell einheitlich |
| **Post-Processing** | Pillow | Leichtgewichtig, keine externe Abhaengigkeit, volle Kontrolle |
| **Web-Framework** | FastAPI + Jinja2 | Async-faehig, SSE fuer Echtzeit-Fortschritt, leichtgewichtig |
| **Font** | Comfortaa | Brand-Font von endometriose.app, warm und zugaenglich |
| **Bildformat** | WebP | Beste Kompression bei hoher Qualitaet, Web-Standard |

## Kosten

- 10 HD-Bilder via DALL-E 3: **~$0.80**
- Kein Abo noetig — reine Pay-per-Use API

## Erweiterungsmoeglichkeiten

- **A/B-Testing**: Mehrere Varianten pro Titel generieren, Performance vergleichen
- **CMS-Integration**: WordPress REST API Anbindung fuer automatischen Upload
- **Scheduled Generation**: Neue Blog-Posts erkennen, automatisch Header generieren
- **Style Transfer**: Eigenes Referenzbild als Stil-Vorlage via Stability AI ControlNet

## Tech Stack

Python 3.12 | FastAPI | DALL-E 3 | Pillow | Tailwind CSS | Comfortaa Font

---

*Coding Challenge — Aliaksandr Belafostau*
