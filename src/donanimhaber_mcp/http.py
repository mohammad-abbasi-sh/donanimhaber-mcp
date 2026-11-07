"""HTTP layer for donanimhaber_mcp.

donanimhaber.com serves its news pages fully server-rendered —
no login, no API key (verified live 2026-11-07: homepage 200,
/teknoloji-haberleri 200, article pages 200, forum home 200).
The transport uses curl-cffi chrome120 impersonation, the same
proven pattern as the other Turkey-factory servers. Requests are
kept gentle (one at a time, ~0.8s apart) and read-only.

Caveats found while probing (documented, not worked around):
- The site's own search (/ara?q=...) ignores the query and
  returns the same 2 stale "ara" articles for every keyword; the
  search box and the forum search are token-gated Yandex/Elastic
  widgets. Keyword search in this server therefore filters the
  freshly fetched latest + tech listings client-side.
- The forum search needs a token + security key, so there is no
  forum keyword search — forum_hot lists the SSR popular topics
  and forum_topics lists a forum category's topics.
"""
from __future__ import annotations

import time
from urllib.parse import quote

from curl_cffi import requests as _r

BASE = "https://www.donanimhaber.com"
FORUM_BASE = "https://forum.donanimhaber.com"
TIMEOUT = 30.0
MIN_INTERVAL = 0.8  # seconds between requests — be polite

_HEADERS = {
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
}

_last_fetch = 0.0


class DonanimhaberError(RuntimeError):
    pass


def _get(url: str) -> str:
    global _last_fetch
    wait = MIN_INTERVAL - (time.monotonic() - _last_fetch)
    if wait > 0:
        time.sleep(wait)
    try:
        resp = _r.get(url, impersonate="chrome120", headers=_HEADERS, timeout=TIMEOUT)
    except Exception as e:
        raise DonanimhaberError(f"network error fetching {url}: {e}") from e
    finally:
        _last_fetch = time.monotonic()
    if resp.status_code == 403:
        raise DonanimhaberError(
            "donanimhaber.com refused the request (HTTP 403, bot wall) — try again later"
        )
    if resp.status_code == 429:
        raise DonanimhaberError(
            "donanimhaber.com rate-limited the request (HTTP 429) — try again later"
        )
    if resp.status_code == 404:
        raise DonanimhaberError(f"page not found (HTTP 404): {url}")
    if resp.status_code != 200:
        raise DonanimhaberError(f"unexpected HTTP {resp.status_code} fetching {url}")
    return resp.text


def fetch_home() -> str:
    return _get(f"{BASE}/")


def fetch_section(slug: str) -> str:
    """Section/topic listing: /teknoloji-haberleri, /yapay-zeka, /bitcoin ..."""
    return _get(f"{BASE}/{quote(slug.strip('/'))}")


def fetch_article(path: str) -> str:
    """Article page: full URL or /<slug>--<id> path."""
    url = path if path.startswith("http") else f"{BASE}/{path.lstrip('/')}"
    return _get(url)


def fetch_forum_home() -> str:
    return _get(f"{FORUM_BASE}/")
