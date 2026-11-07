"""Offline tests for donanimhaber_mcp.news — recorded real pages.

Fixtures are real pages fetched 2026-11-07 (curl, browser UA):
- home.html: homepage (57 articles; first cards incl. Aina AI Ring
  --212567, "Ekranlı ve mikrofonlu akıllı yüzük: Aina AI Ring").
- category.html: /teknoloji-haberleri (70 articles; first:
  1.2 PureTech --211632, Onur Seven, "14 Ekim 2026 16:57",
  Yaşam, 40,3b views, 40 comments).
- article.html: /aina-ai-ring-...--212567 (NewsArticle JSON-LD:
  headline "Ekranlı ve mikrofonlu akıllı yüzük: Aina AI Ring",
  author Erkan Calp, datePublished 2026-11-06T20:44:00+03:00).
- forum.html: forum home, trimmed to the popular-topics region
  (101 popular rows; incl. AMD CEO'su Lisa Su topic --164319226).
"""
import os
import unittest

from donanimhaber_mcp import news as N

FIX = os.path.join(os.path.dirname(__file__), "fixtures")


def _read(name: str) -> str:
    with open(os.path.join(FIX, name), encoding="utf-8") as f:
        return f.read()


class TestParseViews(unittest.TestCase):
    def test_plain(self):
        self.assertEqual(N._parse_views("949"), 949)

    def test_thousands(self):
        self.assertEqual(N._parse_views("40,3b"), 40300)

    def test_millions(self):
        self.assertEqual(N._parse_views("1,2mn"), 1200000)

    def test_none(self):
        self.assertIsNone(N._parse_views(""))
        self.assertIsNone(N._parse_views(None))


class TestParseHomeCards(unittest.TestCase):
    def setUp(self):
        self.cards = N.parse_cards(_read("home.html"))

    def test_count(self):
        self.assertGreaterEqual(len(self.cards), 35)

    def test_aina_card(self):
        c = next(x for x in self.cards if x["article_id"] == 212567)
        self.assertEqual(
            c["title"], "Ekranlı ve mikrofonlu akıllı yüzük: Aina AI Ring"
        )
        self.assertTrue(c["summary"])
        self.assertEqual(
            c["url"],
            "https://www.donanimhaber.com/aina-ai-ring-tanitildi-ekranli-akilli-yuzuk-neler-sunuyor--212567",
        )

    def test_all_have_fields(self):
        for c in self.cards:
            self.assertGreater(c["article_id"], 0)
            self.assertTrue(c["title"])
            self.assertTrue(c["url"].startswith("https://www.donanimhaber.com/"))


class TestParseCategoryCards(unittest.TestCase):
    def setUp(self):
        self.cards = N.parse_cards(_read("category.html"))

    def test_count(self):
        self.assertGreaterEqual(len(self.cards), 45)

    def test_first_card(self):
        c = next(x for x in self.cards if x["article_id"] == 211632)
        self.assertIn("PureTech", c["title"])
        self.assertEqual(c["date"], "14 Ekim 2026 16:57")
        self.assertEqual(c["category"], "Yaşam")
        self.assertEqual(c["views"], 40300)
        self.assertEqual(c["comments"], 40)
        self.assertIn("Stellantis", c["summary"])

    def test_bim_card(self):
        c = next(x for x in self.cards if x["article_id"] == 212602)
        self.assertIn("BİM", c["title"])


class TestSearchCards(unittest.TestCase):
    def test_keyword(self):
        cards = N.parse_cards(_read("home.html"))
        cards += N.parse_cards(_read("category.html"))
        hits = N.search_cards(cards, "yapay zeka")
        self.assertGreater(len(hits), 0)
        for h in hits:
            hay = (h["title"] + h["summary"] + h["category"]).lower()
            self.assertIn("yapay", hay)

    def test_no_match(self):
        cards = N.parse_cards(_read("home.html"))
        self.assertEqual(N.search_cards(cards, "zzzqqqx"), [])


class TestParseArticle(unittest.TestCase):
    def setUp(self):
        self.a = N.parse_article(
            _read("article.html"),
            "https://www.donanimhaber.com/aina-ai-ring-tanitildi-ekranli-akilli-yuzuk-neler-sunuyor--212567",
        )

    def test_fields(self):
        self.assertEqual(
            self.a["headline"],
            "Ekranlı ve mikrofonlu akıllı yüzük: Aina AI Ring",
        )
        self.assertEqual(self.a["author"], "Erkan Calp")
        self.assertEqual(self.a["date_published"], "2026-11-06T20:44:00+03:00")
        self.assertTrue(self.a["body"])
        self.assertIn("Aina", self.a["body"])
        self.assertIsInstance(self.a["word_count"], int)

    def test_no_article(self):
        with self.assertRaises(ValueError):
            N.parse_article("<html><head></head><body>hi</body></html>")


class TestParseSections(unittest.TestCase):
    def test_sections(self):
        sections = N.parse_sections(_read("home.html"))
        self.assertGreaterEqual(len(sections), 8)
        by_slug = {s["slug"]: s["name"] for s in sections}
        self.assertIn("teknoloji-haberleri", by_slug)
        self.assertIn("yapay-zeka", by_slug)
        self.assertIn("bitcoin", by_slug)


class TestParseForumHot(unittest.TestCase):
    def setUp(self):
        self.topics = N.parse_forum_hot(_read("forum.html"))

    def test_count(self):
        self.assertGreaterEqual(len(self.topics), 50)

    def test_amd_topic(self):
        t = next(x for x in self.topics if x["topic_id"] == 164319226)
        self.assertIn("Lisa Su", t["title"])
        self.assertEqual(t["forum"], "Anasayfa Haberleri")
        self.assertEqual(t["online_users"], 102)

    def test_all_have_fields(self):
        for t in self.topics:
            self.assertGreater(t["topic_id"], 0)
            self.assertTrue(t["title"])
            self.assertTrue(t["url"].startswith("https://forum.donanimhaber.com/"))


if __name__ == "__main__":
    unittest.main()
