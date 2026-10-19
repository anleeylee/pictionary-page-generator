#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pictionary-page-generator — batch-generate SEO-ready themed Pictionary content pages.

Reads one or more word-library JSON files (theme / title / entries[{prompt,
category, difficulty}]) and renders one static HTML page per library with:

  * keyword-optimized <title> and meta description
  * canonical URL, Open Graph tags and JSON-LD schema (WebPage + FAQPage)
  * generator embed block pointing to the live generator
  * category sample tables and how-to-play section
  * per-theme FAQ (3 generic + 2 themed questions)
  * internal links between all generated pages plus the site homepage

It also rewrites a sitemap.xml covering every generated page.

Output pages are plain static HTML: drop them into the site root (or a build
folder) and they are ready to deploy. This is the content pipeline behind
themed pages such as
https://pictionarywordgenerators.com/hard-pictionary-words.
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from html import escape
from pathlib import Path
from typing import Dict, List, Optional

SITE_NAME = "Pictionary Word Generator"
DEFAULT_SITE_URL = "https://pictionarywordgenerators.com"

SLUG_STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "for", "to", "in", "on", "with",
}

SITEMAP_HEAD = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
)
SITEMAP_TAIL = "</urlset>\n"

HTML_SKELETON = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{site_name}">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{og_description}">
<meta property="og:url" content="{canonical}">
<script type="application/ld+json">
{schema}
</script>
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;max-width:860px;margin:0 auto;padding:1.5rem;line-height:1.6;color:#1f2430}}
h1,h2,h3{{line-height:1.25}}
a{{color:#0b5cad}}
table{{border-collapse:collapse;width:100%;margin:1rem 0}}
th,td{{border:1px solid #d8dee8;padding:.5rem .75rem;text-align:left}}
th{{background:#f2f5fa}}
.generator-embed{{background:#f6f8fb;border:1px solid #d8dee8;border-radius:8px;padding:1rem 1.25rem;margin:1.5rem 0}}
.theme-links{{margin-top:2rem;padding-top:1rem;border-top:1px solid #d8dee8}}
.faq-item{{margin-bottom:1.25rem}}
</style>
</head>
<body>
{body}
</body>
</html>
"""

# ---- theme templates -------------------------------------------------------

GENERATOR_EMBED = (
    '<div class="generator-embed">\n'
    "  <h2>Need a fresh prompt? Use the free {title} Pictionary word generator</h2>\n"
    '  <p>When your hand is stuck, open the <a href="{site_url}/" '
    'title="{title} Pictionary words generator">{title} Pictionary words '
    'generator</a> and draw a random word in seconds — free, no sign-up, '
    "thousands of prompts.</p>\n"
    "</div>\n"
)

HOW_TO_PLAY = """<section>
<h2>How to play {title} Pictionary</h2>
<ol>
<li><strong>Split into two teams.</strong> Each team picks a drawer and a
scorekeeper; the drawer changes every round.</li>
<li><strong>Draw a card or spin the generator.</strong> The drawer silently
reads the prompt from the list below (or the generator) and must not say the
word, spell it, or make sounds.</li>
<li><strong>Sketch, don't write.</strong> Draw pictures only — letters and
numbers are not allowed, and the clock starts as soon as the prompt is
revealed.</li>
<li><strong>Guess out loud.</strong> Teammates call out guesses; the drawer may
nod or shake their head but can never speak.</li>
<li><strong>Score a point when the word is guessed</strong> within the time
limit (60&ndash;90 seconds works well), then pass the turn.</li>
</ol>
<p>First team to the agreed target (usually 10 points) wins. For rules, house
variants and printable score sheets see
<a href="{site_url}/how-to-play-pictionary">how to play Pictionary</a>.</p>
</section>
"""

FAQS_GENERIC: List[List[str]] = [
    ("What level are the {title} Pictionary words?",
     "The library mixes easy, medium and hard prompts so every round has a fair "
     "spread: simple concrete nouns for warm-ups, trickier actions and abstract "
     "ideas for the final rounds. You can also open the "
     "{site_link} to draw a random word at any difficulty."),
    ("How many {title} Pictionary words are there?",
     "Each themed library ships with a base list and the live generator can "
     "produce thousands of combinations, so the exact number you can play with "
     "is effectively unlimited — the sample table below is just the curated "
     "core."),
    ("Can I print the {title} word list?",
     "Yes. Select the table below, copy it into any document and print, or use "
     "a printable word list generator to produce cards sized for your game "
     "night. See {printable_link} for ready-made printable lists."),
]

FAQ_THEMED: Dict[str, List[List[str]]] = {
    "space": [
        ("What space words are easy to draw?",
         "Stick to single concrete nouns with strong shapes: Moon, rocket, star "
         "and Saturn are almost instantly recognizable on paper. Save nebulae "
         "and black holes for the hard rounds."),
        ("How do you draw an abstract space word like 'gravity'?",
         "Draw an apple falling past a planet, or a ball rolling off a table — "
         "players usually get it fast once they see the motion cue."),
    ],
}


def slugify(name: str) -> str:
    """'Hard Words!' -> 'hard-words' (lowercase, keep letters/digits)."""
    words = [
        w for w in re.sub(r"[^a-z0-9\s-]", "", name.lower()).split()
        if w and w not in SLUG_STOPWORDS
    ]
    return "-".join(words) or "pictionary-words"


def page_slug(theme: str) -> str:
    return slugify(theme)


def load_library(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict) or "entries" not in data:
        raise ValueError(f"{path}: expected {{theme, title, entries:[...]}}")
    return data


def _faq_jsonld(theme: str, site_url: str, site_link: str, printable_link: str) -> dict:
    faqs = []
    for q, a in FAQS_GENERIC:
        faqs.append({"@type": "Question", "name": q.format(title=theme, theme=theme),
                     "acceptedAnswer": {"@type": "Answer", "text": a.format(
                         title=theme, theme=theme, site_link=site_link,
                         printable_link=printable_link)}})
    for q, a in FAQ_THEMED.get(theme, FAQ_THEMED.get("space", [])):
        faqs.append({"@type": "Question", "name": q.format(title=theme, theme=theme),
                     "acceptedAnswer": {"@type": "Answer", "text": a.format(
                         title=theme, theme=theme)}})
    return faqs


def render_page(lib: dict, site_url: str, all_pages: List[dict]) -> str:
    """Render one themed HTML page. all_pages = [{theme, slug, title}]."""
    theme = str(lib.get("theme", "")).strip() or "pictionary"
    title_name = str(lib.get("title", "")).strip() or theme.title()
    slug = page_slug(theme)
    canonical = f"{site_url}/{slug}"
    site_link = f'<a href="{site_url}/" title="{SITE_NAME}">{SITE_NAME}</a>'
    printable_link = (
        f'<a href="{site_url}/printable-pictionary-words" '
        'title="printable Pictionary words">printable Pictionary word lists</a>'
    )

    h1 = f"{title_name} Pictionary Words"
    doc_title = f"{title_name} Pictionary Words — Free List & Generator"
    description = (
        f"{title_name} Pictionary words for your next game night: a free curated "
        f"list with difficulty levels, drawing tips and a built-in generator. "
        f"Draw, guess and score."
    )[:158]

    entries = lib.get("entries", [])
    # category sample table
    by_cat: Dict[str, List[dict]] = {}
    for e in entries:
        by_cat.setdefault(str(e.get("category", "Other")), []).append(e)
    rows = []
    for cat in sorted(by_cat):
        for e in by_cat[cat][:6]:
            rows.append(
                f"<tr><td>{escape(str(e.get('prompt', '')))}</td>"
                f"<td>{escape(cat)}</td>"
                f"<td>{escape(str(e.get('difficulty', 'medium')))}</td></tr>"
            )
    table = (
        "<table><thead><tr><th>Word</th><th>Category</th><th>Difficulty</th>"
        "</tr></thead><tbody>" + "\n".join(rows) + "</tbody></table>"
    ) if rows else "<p>Add entries to this library to populate the sample table.</p>"

    # internal links to every other generated page + homepage
    other = [p for p in all_pages if p["slug"] != slug]
    other_links = " · ".join(
        f'<a href="{p["url"]}" title="{p["title"]}">{p["title"]}</a>' for p in other
    )
    internal = (
        '<nav class="theme-links"><h3>More themed word lists</h3><p>'
        + other_links
        + "</p><p><a href=\"" + site_url + '/" title="Pictionary Word Generator">'
        + SITE_NAME + " — home</a></p></nav>"
    )

    faq_items = []
    for q, a in FAQS_GENERIC:
        faq_items.append(
            '<div class="faq-item"><h3>' + q.format(title=title_name, theme=title_name)
            + "</h3><p>"
            + a.format(title=title_name, theme=title_name, site_link=site_link,
                       printable_link=printable_link) + "</p></div>"
        )
    for q, a in FAQ_THEMED.get(theme, []):
        faq_items.append(
            '<div class="faq-item"><h3>' + q.format(title=title_name, theme=title_name)
            + "</h3><p>"
            + a.format(title=title_name, theme=title_name) + "</p></div>"
        )

    body = [
        f"<h1>{h1}</h1>",
        f"<p>{escape(description)}</p>",
        GENERATOR_EMBED.format(title=title_name, site_url=site_url),
        "<section><h2>Sample " + title_name + " Pictionary words</h2>" + table + "</section>",
        HOW_TO_PLAY.format(title=title_name, site_url=site_url),
        "<section><h2>" + title_name + " Pictionary FAQ</h2>" + "\n".join(faq_items) + "</section>",
        internal,
    ]

    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "@id": canonical,
                "url": canonical,
                "name": doc_title,
                "description": description,
                "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": site_url + "/"},
                "about": {"@type": "Game", "name": h1},
            },
            {"@type": "FAQPage", "mainEntity": _faq_jsonld(
                theme, site_url, site_link, printable_link)},
        ],
    }

    return HTML_SKELETON.format(
        title=doc_title,
        description=escape(description),
        canonical=canonical,
        site_name=SITE_NAME,
        og_title=escape(doc_title),
        og_description=escape(description),
        schema=json.dumps(schema, ensure_ascii=False, indent=2),
        body="\n".join(body),
    )


def write_sitemap(pages: List[dict], output_dir: Path, today: str) -> str:
    """Rewrite sitemap.xml from the list of generated pages."""
    lines = [SITEMAP_HEAD]
    for p in sorted(pages, key=lambda x: x["url"]):
        lines.append(
            "  <url><loc>{loc}</loc><lastmod>{lastmod}</lastmod>"
            "<changefreq>weekly</changefreq><priority>{priority}</priority></url>\n".format(
                loc=p["url"], lastmod=today, priority=p.get("priority", "0.7")))
    lines.append(SITEMAP_TAIL)
    xml = "".join(lines)
    (output_dir / "sitemap.xml").write_text(xml, encoding="utf-8")
    return xml


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="pictionary-page-generator",
        description="Batch-generate SEO-ready themed Pictionary content pages "
                    "(HTML) from word-library JSON, with title/meta/canonical/"
                    "OG/schema, internal links and a rewritten sitemap.xml.")
    parser.add_argument("--input", "-i", required=True,
                        help="Directory containing word-library JSON files, or a single JSON file")
    parser.add_argument("--output", "-o", default="pages",
                        help="Output directory for generated HTML pages (default: pages)")
    parser.add_argument("--site-url", default=DEFAULT_SITE_URL,
                        help=f"Site base URL used for canonical/OG URLs (default: {DEFAULT_SITE_URL})")
    parser.add_argument("--no-sitemap", action="store_true",
                        help="Do not rewrite sitemap.xml")
    args = parser.parse_args(argv)

    site_url = args.site_url.rstrip("/")
    input_path = Path(args.input)
    if input_path.is_file():
        lib_paths = [input_path]
    elif input_path.is_dir():
        lib_paths = sorted(input_path.glob("*.json"))
    else:
        print(f"error: input not found: {input_path}", file=sys.stderr)
        return 1

    libs = []
    for lp in lib_paths:
        try:
            libs.append(load_library(lp))
        except (ValueError, json.JSONDecodeError, OSError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

    if not libs:
        print("error: no word libraries found", file=sys.stderr)
        return 1

    # stable page plan (all pages known before rendering => cross-linking works)
    pages = []
    for lib in libs:
        theme = str(lib.get("theme", "")).strip() or "pictionary"
        slug = page_slug(theme)
        title_name = str(lib.get("title", "")).strip() or theme.title()
        pages.append({
            "slug": slug,
            "theme": theme,
            "title": f"{title_name} Pictionary Words",
            "url": f"{site_url}/{slug}",
            "priority": "1.0" if theme in ("hard", "easy") else "0.8",
        })

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today().isoformat()

    for lib, page in zip(libs, pages):
        html = render_page(lib, site_url, pages)
        out = output_dir / f"{page['slug']}.html"
        out.write_text(html, encoding="utf-8")
        print(f"wrote {out}  ->  {page['url']}")

    if not args.no_sitemap:
        write_sitemap(pages, output_dir, today)
        print(f"wrote {output_dir / 'sitemap.xml'}  ({len(pages)} urls)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
