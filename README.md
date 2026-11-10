# donanimhaber-mcp 🇹🇷

mcp-name: io.github.mohammad-abbasi-sh/donanimhaber-mcp

Unofficial **read-only** MCP server for donanimhaber.com, Türkiye's leading technology news site + forum — latest tech news, keyword search, full article text, section listings and the forum's hottest topics.

> Built by Mohammad Abbasi as part of the "Turkey MCP factory" (Sepehr-style pipeline). Not affiliated with donanimhaber.com.

## For AI agents

Add to your MCP client config (stdio):

```json
{
  "mcpServers": {
    "donanimhaber": {
      "command": "uvx",
      "args": ["donanimhaber-mcp==0.1.0"]
    }
  }
}
```

Or run locally: `python -m donanimhaber_mcp.server` (needs `mcp<2`, `curl-cffi`).

## Tools

| Tool | Description |
|------|-------------|
| `donanimhaber_latest` | Latest tech news (homepage) — `limit` 1..50; articles (id, title, summary, category, views, comments, URL) |
| `donanimhaber_search_news` | Keyword search over recent news (title, summary, category) — `keyword`, `limit` 1..50 |
| `donanimhaber_get_article` | Full text of one article — `article`: the article URL, the `/<slug>--<id>` path, or a bare numeric id (looked up in the latest listings); returns headline, author, dates, section, description, full body, comment count, word count |
| `donanimhaber_section` | Articles in one section/topic — `slug` from `donanimhaber_sections` (e.g. "teknoloji-haberleri", "yapay-zeka", "bitcoin", "gta-6"), `limit` 1..50 |
| `donanimhaber_sections` | All news sections/topics (name + slug + URL) from the homepage |
| `donanimhaber_forum_hot` | Hottest topics on the DonanımHaber forum right now — `limit` 1..50; topics (id, title, time ago, forum, online users, URL) |

Example output (`donanimhaber_latest` / 2026-11-07):

```json
{"total": 39, "articles": [
  {"article_id": 212608, "title": "Yenilenen Volkswagen Virtus'un ilk fotoğrafları yayınlandı",
   "category": "Otomobil Teknolojileri",
   "url": "https://www.donanimhaber.com/yenilenen-volkswagen-virtus-un-ilk-fotograflari-yayinlandi--212608"}, …]}
```

Example output (`donanimhaber_get_article` / Aina AI Ring):

```json
{"headline": "Ekranlı ve mikrofonlu akıllı yüzük: Aina AI Ring",
 "author": "Erkan Calp", "date_published": "2026-11-06T20:44:00+03:00",
 "section": "Giyilebilir Teknolojiler", "word_count": 223, …}
```

## How it works

donanimhaber.com serves its news pages fully server-rendered — no login, no API key, no session cookies. Listing pages carry `<article>` cards (title, summary, category, Turkish-formatted views like "40,3b" = 40,300, comments; section cards also carry the publish date). Article pages carry a schema.org NewsArticle JSON-LD block (headline, author, dates, section, full articleBody, comment count). Forum popular topics are server-rendered rows on forum.donanimhaber.com. Transport uses Chrome TLS impersonation (`curl-cffi`, `chrome120`); requests are spaced ~0.8s apart; everything is read-only.

Two honest limitations, verified live 2026-11-07: (1) the site's own `/ara?q=…` search ignores the query string — it returns the same 2 stale "ara" articles for every keyword — and the search box is a token-gated Yandex/Elastic widget, so `donanimhaber_search_news` filters the freshly fetched latest + technology listings client-side instead (Turkish-aware, folds zekâ → zeka); (2) the forum search is token-gated the same way, so there is no forum keyword search — `donanimhaber_forum_hot` lists the server-rendered popular topics.

## Install

```bash
uvx donanimhaber-mcp==0.1.0        # run directly (needs uv)
# or
pip install donanimhaber-mcp==0.1.0
donanimhaber-mcp    # starts the MCP server on stdio
```

## Tests

```bash
python -m venv .venv && .venv/bin/pip install -e .
.venv/bin/python -m unittest discover -s tests -v
```

Offline tests run on recorded fixtures (real pages fetched 2026-11-07); live tests hit donanimhaber.com. 32/32 green at build time (18 offline + 14 live) plus an MCP stdio smoke test (39 latest articles, 80 hot forum topics).

## Roadmap

- Forum category listings (`/<forum>--f<id>` topic lists)
- Most-read / most-commented rankings (the homepage carries them)
- Article comments (the article page links them)

## License

MIT — see [LICENSE](LICENSE).

---

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
