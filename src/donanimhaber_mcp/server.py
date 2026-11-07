"""MCP server: unofficial read-only access to donanimhaber.com tech news + forum."""
from __future__ import annotations

import json
import re

from mcp.server.fastmcp import FastMCP

from . import http as _http
from . import news as _N

mcp = FastMCP("donanimhaber-mcp")

INSTRUCTIONS = """\
Unofficial read-only MCP server for donanimhaber.com, Türkiye's
leading technology news site + forum. Data comes from the site's
server-rendered pages — no login, no API key, no session cookies.
News cards: the homepage (latest) and section pages like
/teknoloji-haberleri, /yapay-zeka, /bitcoin (title, summary,
category, date where shown, views, comments). Articles carry a
schema.org NewsArticle JSON-LD block (headline, author, dates,
section, full body, comment count). The site's own /ara search
ignores the query string (same 2 stale results for every keyword)
and its search widgets are token-gated, so search_news filters
the freshly fetched latest + tech listings client-side. The forum
search is token-gated too — forum_hot lists the server-rendered
popular topics from forum.donanimhaber.com instead. Views are
Turkish-formatted ("40,3b" = 40,300). Read-only; transport uses
Chrome TLS impersonation; requests are spaced ~0.8s apart.
Built by Mohammad Abbasi (mohammad-abbasi-sh) — Turkey MCP
factory.\
"""


def _err(e: Exception) -> str:
    return json.dumps({"error": str(e)}, ensure_ascii=False)


def _validate_limit(limit: int, lo: int = 1, hi: int = 50) -> int:
    if not lo <= limit <= hi:
        raise ValueError(f"limit must be between {lo} and {hi}")
    return limit


@mcp.tool()
def donanimhaber_latest(limit: int = 10) -> str:
    """The latest tech news on donanimhaber.com (homepage). limit
    1..50. Returns articles (id, title, summary, category, views,
    comments, URL)."""
    try:
        _validate_limit(limit)
        cards = _N.parse_cards(_http.fetch_home())
    except (ValueError, _http.DonanimhaberError) as e:
        return _err(e)
    return json.dumps(
        {"count": min(limit, len(cards)), "total": len(cards),
         "articles": cards[:limit]},
        ensure_ascii=False,
    )


@mcp.tool()
def donanimhaber_search_news(keyword: str, limit: int = 10) -> str:
    """Search recent donanimhaber.com news by keyword (title,
    summary, category). The site's own search ignores queries, so
    this filters the freshly fetched latest + technology listings.
    limit 1..50."""
    try:
        if not keyword or not keyword.strip():
            raise ValueError("keyword must not be empty")
        _validate_limit(limit)
        cards = _N.parse_cards(_http.fetch_home())
        cards += _N.parse_cards(_http.fetch_section("teknoloji-haberleri"))
        seen: set[int] = set()
        unique = []
        for c in cards:
            if c["article_id"] not in seen:
                seen.add(c["article_id"])
                unique.append(c)
        hits = _N.search_cards(unique, keyword.strip())
    except (ValueError, _http.DonanimhaberError) as e:
        return _err(e)
    return json.dumps(
        {"keyword": keyword.strip(), "count": min(limit, len(hits)),
         "total_matches": len(hits), "articles": hits[:limit]},
        ensure_ascii=False,
    )


@mcp.tool()
def donanimhaber_get_article(article: str) -> str:
    """Full text of one donanimhaber.com article. article: the
    article URL (https://www.donanimhaber.com/<slug>--<id>), the
    /<slug>--<id> path, or a bare numeric id (looked up in the
    latest listings). Returns headline, author, dates, section,
    description, full body, comment count and word count."""
    try:
        if not article or not article.strip():
            raise ValueError("article must not be empty")
        article = article.strip()
        url = article
        if re.fullmatch(r"\d+", article):
            cards = _N.parse_cards(_http.fetch_home())
            cards += _N.parse_cards(_http.fetch_section("teknoloji-haberleri"))
            hit = next(
                (c for c in cards if c["article_id"] == int(article)), None
            )
            if hit is None:
                raise ValueError(
                    f"article {article} not in the latest listings — "
                    "pass its full URL from donanimhaber_latest"
                )
            url = hit["url"]
        html_text = _http.fetch_article(url)
        data = _N.parse_article(html_text, url)
    except (ValueError, _http.DonanimhaberError) as e:
        return _err(e)
    return json.dumps(data, ensure_ascii=False)


@mcp.tool()
def donanimhaber_section(slug: str, limit: int = 10) -> str:
    """Articles in one donanimhaber.com section/topic — slug from
    donanimhaber_sections (e.g. "teknoloji-haberleri", "yapay-zeka",
    "bitcoin", "gta-6", "telefon-onerileri"). limit 1..50."""
    try:
        if not slug or not slug.strip():
            raise ValueError("slug must not be empty")
        _validate_limit(limit)
        cards = _N.parse_cards(_http.fetch_section(slug.strip()))
    except (ValueError, _http.DonanimhaberError) as e:
        return _err(e)
    return json.dumps(
        {"section": slug.strip(), "count": min(limit, len(cards)),
         "total": len(cards), "articles": cards[:limit]},
        ensure_ascii=False,
    )


@mcp.tool()
def donanimhaber_sections() -> str:
    """All news sections/topics on donanimhaber.com (name + slug +
    URL), parsed from the homepage."""
    try:
        sections = _N.parse_sections(_http.fetch_home())
    except (ValueError, _http.DonanimhaberError) as e:
        return _err(e)
    return json.dumps(
        {"count": len(sections), "sections": sections}, ensure_ascii=False
    )


@mcp.tool()
def donanimhaber_forum_hot(limit: int = 10) -> str:
    """The hottest topics on the DonanımHaber forum right now
    (forum.donanimhaber.com popular topics). limit 1..50. Returns
    topics (id, title, time ago, forum, online users, URL). The
    forum's own search is token-gated, so there is no keyword
    search for the forum."""
    try:
        _validate_limit(limit)
        topics = _N.parse_forum_hot(_http.fetch_forum_home())
    except (ValueError, _http.DonanimhaberError) as e:
        return _err(e)
    return json.dumps(
        {"count": min(limit, len(topics)), "total": len(topics),
         "topics": topics[:limit]},
        ensure_ascii=False,
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
