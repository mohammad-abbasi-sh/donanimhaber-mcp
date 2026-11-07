"""Stdlib parsing for donanimhaber.com server-rendered pages.

Verified live 2026-11-07 against real pages (fixtures in tests/):
- Homepage /: <article class="medya"> cards — <a
  href="/<slug>--<id>" data-id data-title="FULL TITLE">, <div
  class="govde"> <a class="baslik">TITLE</a> <div
  class="aciklama">SUMMARY</div> <div class="alt"> <a
  href="/<section>" class="damga">Section</a> <span
  class="damga"><span class="icon-eye"></span>VIEWS</span> <span
  class="damga"><span class="icon-bubbles4"></span>COMMENTS</span>.
  57 articles on the recorded homepage.
- Section /<slug> (e.g. /teknoloji-haberleri): <article
  class="medya-yatay ..."> cards — <h3><a href="/<slug>--<id>"
  class="baslik">TITLE</a></h3>, <div class="bilgi"> author +
  <span data-title="14 Ekim 2026 16:57">3 hf.</span> (date!),
  aciklama summary, alt with category link, views, comments.
  70 articles on the recorded category page.
- Article /<slug>--<id>: schema.org NewsArticle inside a @graph
  JSON-LD block (headline, description, articleBody,
  datePublished, dateModified, author Person name,
  articleSection, commentCount, wordCount, url, image).
- Forum home (forum.donanimhaber.com): popular-topic rows
  (<div class="... populersatir">): <a class="satirikapla"
  href="/<slug>--<id>"><div class="populerbaslik">TITLE</div></a>
  (older markup: <a class="populerbaslik" href="...">TITLE</a>),
  <span class="altyazi"> TIME <a href="/<forum>--f<id>">FORUM</a>
  ... </span>, <div class="onlinekullanici ...">N</div>.

Views are Turkish-formatted: "949", "40,3b" (40.3 thousand),
"1,2mn" (1.2 million).
"""
from __future__ import annotations

import html
import json
import re

_TR_UPPER_TO_LOWER = str.maketrans({
    "İ": "i", "I": "ı", "Ş": "ş", "Ğ": "ğ",
    "Ü": "ü", "Ö": "ö", "Ç": "ç",
})

BASE = "https://www.donanimhaber.com"
FORUM_BASE = "https://forum.donanimhaber.com"


def _tr_lower(s: str) -> str:
    return s.translate(_TR_UPPER_TO_LOWER).lower()


def _clean(text: str | None) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _parse_views(raw: str | None) -> int | None:
    """Turkish view count: "949" -> 949, "40,3b" -> 40300, "1,2mn" -> 1200000."""
    if not raw:
        return None
    s = _clean(raw).lower().replace(".", "")
    mult = 1
    if s.endswith("mn"):
        mult, s = 1_000_000, s[:-2]
    elif s.endswith("b"):
        mult, s = 1_000, s[:-1]
    try:
        return int(float(s.replace(",", ".")) * mult)
    except ValueError:
        return None


def _parse_int(raw: str | None) -> int | None:
    if not raw:
        return None
    s = _clean(raw).replace(".", "").replace(",", "")
    try:
        return int(s)
    except ValueError:
        return None


# ---------------------------------------------------------------- news cards

_ARTICLE_RE = re.compile(r"<article\b[^>]*>(.*?)</article>", re.S)
_HREF_ID_RE = re.compile(r'href="(/[^"]*--(\d+))"')
_TITLE_ATTR_RE = re.compile(r'data-title="([^"]+)"')
_BASLIK_RE = re.compile(
    r'<a[^>]*class="[^"]*baslik[^"]*"[^>]*>(.*?)</a>', re.S
)
_ACIKLAMA_RE = re.compile(r'<div class="aciklama">(.*?)</div>', re.S)
_BILGI_RE = re.compile(r'<div class="bilgi">(.*?)</div>', re.S)
_ALT_RE = re.compile(r'<div class="alt[^"]*">(.*?)</div>\s*</div>', re.S)
_DAMGA_CAT_RE = re.compile(
    r'<a[^>]*class="(?:damga|category)"[^>]*>(.*?)</a>', re.S
)
# the capture must start with a digit: the hidden "bakanlar" eye span
# is followed by whitespace only, and must not match
_EYE_RE = re.compile(r'icon-eye"></span>\s*(\d[^<]*)')
_BUBBLE_RE = re.compile(r'icon-bubbles4"></span>\s*(\d[^<]*)')


def parse_cards(html_text: str) -> list[dict]:
    """All news cards on a listing page (homepage or section)."""
    out: list[dict] = []
    seen: set[int] = set()
    for m in _ARTICLE_RE.finditer(html_text):
        block = m.group(1)
        hm = _HREF_ID_RE.search(block)
        if not hm:
            continue
        path, aid = hm.group(1), int(hm.group(2))
        if aid in seen:
            continue
        seen.add(aid)
        # title: the <a class="baslik"> text first — the first
        # data-title on section cards is the DATE span's, not the title
        title = ""
        bm = _BASLIK_RE.search(block)
        if bm:
            title = _clean(bm.group(1))
        if not title:
            tm = _TITLE_ATTR_RE.search(block)
            if tm:
                title = html.unescape(tm.group(1)).strip()
        summary = ""
        am = _ACIKLAMA_RE.search(block)
        if am:
            summary = _clean(am.group(1))
        date_published = ""
        bm2 = _BILGI_RE.search(block)
        if bm2:
            dm = re.search(r'data-title="([^"]+)"', bm2.group(1))
            if dm:
                date_published = html.unescape(dm.group(1)).strip()
        category, views, comments = "", None, None
        alt = _ALT_RE.search(block)
        alt_html = alt.group(1) if alt else block
        cm = _DAMGA_CAT_RE.search(alt_html)
        if cm:
            category = _clean(cm.group(1))
        # the alt div nests other divs, so a non-greedy alt match can
        # cut off before the view/comment spans — search the block
        em = _EYE_RE.search(block)
        if em:
            views = _parse_views(em.group(1))
        bm3 = _BUBBLE_RE.search(block)
        if bm3:
            comments = _parse_int(bm3.group(1))
        out.append({
            "article_id": aid,
            "title": title,
            "summary": summary,
            "category": category,
            "date": date_published,
            "views": views,
            "comments": comments,
            "url": f"{BASE}{path}",
        })
    return out


def _fold(s: str) -> str:
    """Search fold: Turkish lower + circumflexes folded (zekâ -> zeka)."""
    return (_tr_lower(s).replace("â", "a").replace("î", "i")
            .replace("û", "u"))


def search_cards(cards: list[dict], keyword: str) -> list[dict]:
    """Case-insensitive (Turkish-aware) keyword filter over cards."""
    needle = _fold(keyword)
    return [c for c in cards
            if needle in _fold(c["title"])
            or needle in _fold(c["summary"])
            or needle in _fold(c["category"])]


# ---------------------------------------------------------------- article

_LD_RE = re.compile(
    r'<script type="application/ld\+json">(.*?)</script>', re.S
)


def parse_article(html_text: str, url: str = "") -> dict:
    """Parse an article page via its NewsArticle JSON-LD @graph node."""
    for m in _LD_RE.finditer(html_text):
        try:
            data = json.loads(m.group(1))
        except (json.JSONDecodeError, ValueError):
            continue
        nodes = data.get("@graph", []) if isinstance(data, dict) else []
        for node in nodes:
            if isinstance(node, dict) and node.get("@type") in (
                "NewsArticle", "Article",
            ):
                author = node.get("author") or {}
                image = node.get("image") or {}
                if isinstance(image, list):
                    image = image[0] if image else {}
                body = node.get("articleBody", "") or ""

                def _int_or_none(v):
                    try:
                        return int(v)
                    except (TypeError, ValueError):
                        return None

                return {
                    "headline": node.get("headline", ""),
                    "description": node.get("description", ""),
                    "body": _clean(body),
                    "author": author.get("name", "") if isinstance(author, dict) else "",
                    "date_published": node.get("datePublished", ""),
                    "date_modified": node.get("dateModified", ""),
                    "section": node.get("articleSection", ""),
                    "comments": _int_or_none(node.get("commentCount")),
                    "word_count": _int_or_none(node.get("wordCount")),
                    "url": node.get("url", url),
                    "image": image.get("url", "") if isinstance(image, dict) else "",
                }
    raise ValueError("no NewsArticle data found on this page")


# ---------------------------------------------------------------- sections

_SECTION_SKIP = {
    "", "rss", "ara", "dh-arsiv", "giris", "images", "hakkimizda",
    "kunye", "iletisim", "gizlilik", "kvkk",
}


def parse_sections(html_text: str) -> list[dict]:
    """Section/topic links from the homepage (name + slug + URL)."""
    out: list[dict] = []
    seen: set[str] = set()
    for slug, name in re.findall(
        r'<a[^>]*href="(?:https://www\.donanimhaber\.com)?'
        r'/([a-z0-9\-çğıöşü]+)"[^>]*>(.*?)</a>',
        html_text, re.S,
    ):
        slug = slug.strip("/")
        name = _clean(name)
        if (not slug or slug in seen or slug in _SECTION_SKIP
                or "--" in slug or slug.startswith("editor")
                or not name or len(name) > 40):
            continue
        seen.add(slug)
        out.append({"name": name, "slug": slug,
                    "url": f"{BASE}/{slug}"})
    return out


# ---------------------------------------------------------------- forum

_SATIR_RE = re.compile(
    r'<a class="satirikapla" href="(/[^"]*--(\d+))">'
    r'\s*<div class="populerbaslik">\s*(.*?)\s*</div>\s*</a>',
    re.S,
)
_POPULER_A_RE = re.compile(
    r'<a class="populerbaslik" href="(/[^"]*--(\d+))">\s*(.*?)\s*</a>',
    re.S,
)
_ALTYAZI_RE = re.compile(r'<span class="altyazi">(.*?)</span>', re.S)
_ONLINE_RE = re.compile(
    r'<div class="onlinekullanici[^"]*">\s*(\d+)\s*</div>'
)


def parse_forum_hot(html_text: str) -> list[dict]:
    """Popular forum topics from the forum homepage.

    Two markup variants exist: the current
    <a class="satirikapla"><div class="populerbaslik">TITLE</div></a>
    and the older <a class="populerbaslik" href="...">TITLE</a>.
    Time/forum/online count come from the text right after each
    anchor (altyazi span + onlinekullanici div).
    """
    found: list[tuple[int, int, str, str]] = []  # (pos, id, href, title)
    for m in _SATIR_RE.finditer(html_text):
        found.append((m.start(), int(m.group(2)), m.group(1),
                      _clean(m.group(3))))
    for m in _POPULER_A_RE.finditer(html_text):
        found.append((m.start(), int(m.group(2)), m.group(1),
                      _clean(m.group(3))))
    found.sort()
    out: list[dict] = []
    seen: set[int] = set()
    for pos, tid, href, title in found:
        if tid in seen or not title:
            continue
        seen.add(tid)
        tail = html_text[pos:pos + 2500]
        time_ago, forum = "", ""
        am = _ALTYAZI_RE.search(tail)
        if am:
            time_ago = _clean(am.group(1)).split("  ")[0].strip()
            fm = re.search(r'href="/([^"]+--f\d+)"[^>]*>([^<]+)</a>',
                          am.group(1))
            if fm:
                forum = _clean(fm.group(2))
        online = None
        om = _ONLINE_RE.search(tail)
        if om:
            online = int(om.group(1))
        out.append({
            "topic_id": tid,
            "title": title,
            "time_ago": time_ago,
            "forum": forum,
            "online_users": online,
            "url": f"{FORUM_BASE}{href}",
        })
    return out
