"""Live tests for donanimhaber_mcp — real requests to donanimhaber.com.

Requires network + Chrome TLS impersonation (curl-cffi). The server
is polite by design (~0.8s between requests), so this file takes
~15s. Run: python -m unittest discover -s tests -v

News changes during the day; tests assert structure and sane
ranges, not exact headlines.
"""
import json
import unittest

from donanimhaber_mcp import http as H
from donanimhaber_mcp import news as N


class TestLiveLatest(unittest.TestCase):
    def test_home(self):
        cards = N.parse_cards(H.fetch_home())
        self.assertGreaterEqual(len(cards), 35)
        self.assertTrue(cards[0]["title"])
        self.assertTrue(cards[0]["url"])

    def test_section(self):
        cards = N.parse_cards(H.fetch_section("teknoloji-haberleri"))
        self.assertGreaterEqual(len(cards), 35)
        self.assertTrue(any(c["date"] for c in cards))

    def test_topic_section(self):
        cards = N.parse_cards(H.fetch_section("yapay-zeka"))
        self.assertGreater(len(cards), 0)

    def test_unknown_section_404(self):
        with self.assertRaises(H.DonanimhaberError):
            H.fetch_section("boyle-bir-bolum-yok-xyz")


class TestLiveArticle(unittest.TestCase):
    def test_article(self):
        cards = N.parse_cards(H.fetch_home())
        first = cards[0]
        a = N.parse_article(H.fetch_article(first["url"]), first["url"])
        self.assertEqual(a["headline"], first["title"])
        self.assertTrue(a["author"])
        self.assertTrue(a["date_published"])
        self.assertTrue(len(a["body"]) > 200)


class TestLiveSections(unittest.TestCase):
    def test_sections(self):
        sections = N.parse_sections(H.fetch_home())
        self.assertGreaterEqual(len(sections), 8)
        slugs = {s["slug"] for s in sections}
        self.assertIn("teknoloji-haberleri", slugs)


class TestLiveForum(unittest.TestCase):
    def test_forum_hot(self):
        topics = N.parse_forum_hot(H.fetch_forum_home())
        self.assertGreaterEqual(len(topics), 20)
        self.assertTrue(topics[0]["title"])


class TestLiveServerTools(unittest.TestCase):
    """End-to-end: call the MCP tool functions and check JSON output."""

    def test_latest_tool(self):
        from donanimhaber_mcp.server import donanimhaber_latest

        out = json.loads(donanimhaber_latest(limit=3))
        self.assertEqual(out["count"], 3)
        self.assertEqual(len(out["articles"]), 3)

    def test_search_tool(self):
        from donanimhaber_mcp.server import donanimhaber_search_news

        out = json.loads(donanimhaber_search_news("Samsung", limit=3))
        self.assertIn("total_matches", out)
        self.assertLessEqual(len(out["articles"]), 3)

    def test_get_article_tool(self):
        from donanimhaber_mcp.server import (
            donanimhaber_get_article, donanimhaber_latest,
        )

        latest = json.loads(donanimhaber_latest(limit=1))
        url = latest["articles"][0]["url"]
        out = json.loads(donanimhaber_get_article(url))
        self.assertEqual(out["headline"], latest["articles"][0]["title"])
        self.assertTrue(len(out["body"]) > 200)

    def test_get_article_by_id_tool(self):
        from donanimhaber_mcp.server import (
            donanimhaber_get_article, donanimhaber_latest,
        )

        latest = json.loads(donanimhaber_latest(limit=1))
        aid = str(latest["articles"][0]["article_id"])
        out = json.loads(donanimhaber_get_article(aid))
        self.assertEqual(out["headline"], latest["articles"][0]["title"])

    def test_sections_tool(self):
        from donanimhaber_mcp.server import donanimhaber_sections

        out = json.loads(donanimhaber_sections())
        self.assertGreaterEqual(out["count"], 8)

    def test_forum_tool(self):
        from donanimhaber_mcp.server import donanimhaber_forum_hot

        out = json.loads(donanimhaber_forum_hot(limit=3))
        self.assertEqual(out["count"], 3)
        self.assertTrue(out["topics"][0]["title"])

    def test_empty_keyword_error(self):
        from donanimhaber_mcp.server import donanimhaber_search_news

        out = json.loads(donanimhaber_search_news("   "))
        self.assertIn("error", out)


if __name__ == "__main__":
    unittest.main()
