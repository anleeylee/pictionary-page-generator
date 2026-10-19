#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for pictionary-page-generator."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from page_generator import (  # noqa: E402
    DEFAULT_SITE_URL,
    HTML_SKELETON,
    load_library,
    page_slug,
    render_page,
    slugify,
    write_sitemap,
)

SPACE_LIB = {
    "theme": "space",
    "title": "Space",
    "entries": [
        {"prompt": "Moon", "category": "Celestial", "difficulty": "easy"},
        {"prompt": "Black Hole", "category": "Celestial", "difficulty": "hard"},
        {"prompt": "Gravity", "category": "Concepts", "difficulty": "hard"},
    ],
}

HARD_LIB = {
    "theme": "hard",
    "title": "Hard",
    "entries": [{"prompt": "Astronaut", "category": "People", "difficulty": "medium"}],
}


class TestSlugify(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(slugify("Hard Words!"), "hard-words")

    def test_stopwords_removed(self):
        self.assertEqual(slugify("Words for the Party"), "words-party")

    def test_empty_fallback(self):
        self.assertEqual(slugify("!!!"), "pictionary-words")

    def test_page_slug(self):
        self.assertEqual(page_slug("Hard"), "hard")


class TestRenderPage(unittest.TestCase):
    def setUp(self):
        self.pages = [
            {"slug": "space", "theme": "space", "title": "Space Pictionary Words",
             "url": f"{DEFAULT_SITE_URL}/space", "priority": "0.8"},
            {"slug": "hard", "theme": "hard", "title": "Hard Pictionary Words",
             "url": f"{DEFAULT_SITE_URL}/hard", "priority": "1.0"},
        ]
        self.html = render_page(SPACE_LIB, DEFAULT_SITE_URL, self.pages)

    def test_doctype(self):
        self.assertTrue(self.html.startswith("<!DOCTYPE html>"))

    def test_title_has_keywords(self):
        self.assertIn("<title>Space Pictionary Words — Free List & Generator</title>", self.html)

    def test_meta_description(self):
        self.assertIn('<meta name="description"', self.html)

    def test_canonical(self):
        self.assertIn(f'<link rel="canonical" href="{DEFAULT_SITE_URL}/space">', self.html)

    def test_open_graph(self):
        for prop in ("og:type", "og:site_name", "og:title", "og:description", "og:url"):
            self.assertIn(f'property="{prop}"', self.html)

    def test_jsonld_webpage_and_faq(self):
        match = self.html.split('<script type="application/ld+json">')[1].split("</script>")[0]
        schema = json.loads(match)
        types = [n["@type"] for n in schema["@graph"]]
        self.assertIn("WebPage", types)
        self.assertIn("FAQPage", types)

    def test_generator_embed_link(self):
        self.assertIn(f'href="{DEFAULT_SITE_URL}/"', self.html)
        self.assertIn("generator", self.html.lower())

    def test_sample_table(self):
        self.assertIn("<table>", self.html)
        self.assertIn("Moon", self.html)
        self.assertIn("Black Hole", self.html)

    def test_how_to_play(self):
        self.assertIn("How to play Space Pictionary", self.html)
        self.assertIn("how-to-play-pictionary", self.html)

    def test_internal_links_to_other_pages(self):
        self.assertIn(f'href="{DEFAULT_SITE_URL}/hard"', self.html)

    def test_homepage_link(self):
        self.assertIn(f'href="{DEFAULT_SITE_URL}/"', self.html)

    def test_faq_questions(self):
        for q in ("What level are the Space Pictionary words?",
                  "How many Space Pictionary words are there?",
                  "What space words are easy to draw?"):
            self.assertIn(q, self.html)

    def test_html_escaped_prompts(self):
        html = render_page({"theme": "x", "title": "X",
                            "entries": [{"prompt": "<script>alert(1)</script>",
                                         "category": "A", "difficulty": "easy"}]},
                           DEFAULT_SITE_URL, [])
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;script&gt;", html)


class TestLoadLibrary(unittest.TestCase):
    def test_invalid_schema(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            fh.write('{"theme": "x"}')
            path = fh.name
        try:
            with self.assertRaises(ValueError):
                load_library(Path(path))
        finally:
            os.unlink(path)


class TestSitemap(unittest.TestCase):
    def test_writes_all_urls(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            pages = [
                {"url": "https://example.com/a", "priority": "0.8"},
                {"url": "https://example.com/b", "priority": "1.0"},
            ]
            xml = write_sitemap(pages, out, "2026-10-20")
            self.assertIn("<loc>https://example.com/a</loc>", xml)
            self.assertIn("<loc>https://example.com/b</loc>", xml)
            self.assertIn("<lastmod>2026-10-20</lastmod>", xml)
            self.assertTrue((out / "sitemap.xml").exists())


if __name__ == "__main__":
    unittest.main()
