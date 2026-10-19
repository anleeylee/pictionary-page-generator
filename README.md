# Pictionary Page Generator

> **Batch-generate SEO-ready themed Pictionary content pages (HTML) from word-library JSON — keyword-optimized title/meta, canonical, Open Graph, JSON-LD schema, generator embed, category sample tables, how-to-play, per-theme FAQ, internal links and an automatically rewritten sitemap.xml.**

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![CLI](https://img.shields.io/badge/CLI-ready-4B8BBE)](page_generator.py)
[![No dependencies](https://img.shields.io/badge/deps-stdlib%20only-blueviolet)](requirements.txt)

---

## Links

- 🎲 **Try the live tool:** [Pictionary Word Generator — 7,000+ free drawing prompts](https://pictionarywordgenerators.com/)
- 📄 **Hard words page:** [Hard Pictionary Words — challenging drawing prompts](https://pictionarywordgenerators.com/hard-pictionary-words)
- Read the Chinese version: [README.zh-CN.md](README.zh-CN.md)

---

## What it does

A themed word library is only useful if people can find it. The
**Pictionary Page Generator** turns a word-library JSON file (the same schema
produced by the
[Pictionary Wordlist Generator](https://github.com/anleeylee/pictionary-wordlist-generator))
into a complete, deployable HTML content page for one theme:

- **keyword-optimized `<title>` and meta description** built from the theme name
  ("Space Pictionary Words — Free List & Generator");
- **canonical URL** pointing at the canonical site path for the theme;
- **Open Graph tags** (og:type / og:site_name / og:title / og:description / og:url)
  so shared links render nicely on social media;
- **JSON-LD schema** — a WebPage node plus a FAQPage node with the page's
  questions, eligible for rich results;
- a **generator embed block** that links back to the live generator
  ([Pictionary Word Generator](https://pictionarywordgenerators.com/));
- a **category sample table** (word / category / difficulty) straight from the
  library;
- a **how-to-play section** with standard Pictionary rules;
- a **per-theme FAQ** (3 generic + 2 themed questions, configurable);
- **internal links** between every generated page plus the site homepage —
  the whole theme cluster is cross-linked in one pass.

After rendering, the tool **rewrites `sitemap.xml`** with one `<url>` entry per
generated page (lastmod / changefreq / priority), so the new pages are
discoverable by search engines immediately.

## Why it matters

Content pages are how a Pictionary word site ranks for long-tail queries like
"hard Pictionary words" or "space Pictionary words". Doing the HTML by hand is
slow and inconsistent — titles drift, canonical tags get forgotten, schema
goes stale. This generator makes every theme page structurally identical and
SEO-complete by construction, and keeps the sitemap in sync automatically.

Because every page links to the generator and the other theme pages, each new
library grows the site's internal link graph instead of sitting as an orphan.

## Install

```bash
git clone https://github.com/anleeylee/pictionary-page-generator.git
cd pictionary-page-generator

# no pip install needed — standard library only
python page_generator.py --help
```

## Usage

```bash
# generate pages + sitemap from a directory of word libraries
python page_generator.py --input examples/libs --output pages

# generate from a single library
python page_generator.py --input examples/libs/space.json --output pages

# custom site URL (used for canonical / OG / sitemap)
python page_generator.py --input examples/libs --output pages \
  --site-url https://pictionarywordgenerators.com

# skip sitemap rewriting
python page_generator.py --input examples/libs --output pages --no-sitemap
```

### Options

| Option | Default | Meaning |
|---|---|---|
| `--input` | (required) | Directory of word-library JSON files, or a single JSON file |
| `--output` | `pages` | Output directory for generated HTML pages |
| `--site-url` | `https://pictionarywordgenerators.com` | Base URL for canonical / OG / sitemap URLs |
| `--no-sitemap` | off | Do not rewrite `sitemap.xml` |

## Expected library schema

```json
{
  "theme": "space",
  "title": "Space",
  "entries": [
    {"prompt": "Moon", "category": "Celestial", "difficulty": "easy"}
  ]
}
```

This is exactly the schema emitted by the
[Pictionary Wordlist Generator](https://github.com/anleeylee/pictionary-wordlist-generator)
and validated by the
[Pictionary Wordlist Auditor](https://github.com/anleeylee/pictionary-wordlist-auditor).

## Generated page anatomy

```
themed page (e.g. /space)
├── <title> Space Pictionary Words — Free List & Generator
├── meta description
├── <link rel="canonical" href="https://…/space">
├── Open Graph tags
├── JSON-LD: WebPage + FAQPage
├── generator embed block → links to the live generator
├── sample word table (word / category / difficulty)
├── how-to-play section → links to how-to-play page
├── themed FAQ (5 questions)
└── internal links → all other generated theme pages + homepage
```

## Tests

```bash
python -m unittest discover -s tests -v
```

Covers: slug normalization, title/meta/canonical/OG presence, JSON-LD
structure (WebPage + FAQPage), generator embed, sample table, how-to-play,
internal cross-links, FAQ rendering, HTML escaping and sitemap generation.

## License

MIT — use it, extend it, and keep the attribution. The pages it generates are
your site's content; the tool just makes them consistent and crawlable.
