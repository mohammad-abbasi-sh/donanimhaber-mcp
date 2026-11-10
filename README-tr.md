# donanimhaber-mcp 🇹🇷

mcp-name: io.github.mohammad-abbasi-sh/donanimhaber-mcp

donanimhaber.com için resmi olmayan **salt okunur** MCP sunucusu — Türkiye'nin lider teknoloji haber sitesi + forumu: en son teknoloji haberleri, anahtar kelime araması, haberlerin tam metni, bölüm listeleri ve forumun en sıcak konuları.

> Mohammad Abbasi tarafından "Turkey MCP factory" (Sepehr tarzı hat) kapsamında geliştirildi. donanimhaber.com ile bağlantısı yoktur.

## Yapay zekâ ajanları için

MCP istemci yapılandırmanıza ekleyin (stdio):

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

Veya yerel çalıştırın: `python -m donanimhaber_mcp.server` (`mcp<2`, `curl-cffi` gerekir).

## Araçlar

| Araç | Açıklama |
|------|----------|
| `donanimhaber_latest` | En son teknoloji haberleri (ana sayfa) — `limit` 1..50; haberler (id, başlık, özet, kategori, görüntülenme, yorum, URL) |
| `donanimhaber_search_news` | Son haberlerde anahtar kelime araması (başlık, özet, kategori) — `keyword`, `limit` 1..50 |
| `donanimhaber_get_article` | Bir haberin tam metni — `article`: haber URL'si, `/<slug>--<id>` yolu veya yalın sayısal id (en son listelerde aranır); başlık, yazar, tarihler, bölüm, açıklama, tam metin, yorum sayısı, kelime sayısı |
| `donanimhaber_section` | Bir bölüm/konudaki haberler — `slug` (`donanimhaber_sections` çıktısından; örn. "teknoloji-haberleri", "yapay-zeka", "bitcoin", "gta-6"), `limit` 1..50 |
| `donanimhaber_sections` | Tüm haber bölümleri/konuları (ad + slug + URL), ana sayfadan |
| `donanimhaber_forum_hot` | DonanımHaber forumunun şu anki en sıcak konuları — `limit` 1..50; konular (id, başlık, süre, forum, çevrimiçi kullanıcı, URL) |

Örnek çıktı (`donanimhaber_latest` / 2026-11-07):

```json
{"total": 39, "articles": [
  {"article_id": 212608, "title": "Yenilenen Volkswagen Virtus'un ilk fotoğrafları yayınlandı",
   "category": "Otomobil Teknolojileri",
   "url": "https://www.donanimhaber.com/yenilenen-volkswagen-virtus-un-ilk-fotograflari-yayinlandi--212608"}, …]}
```

Örnek çıktı (`donanimhaber_get_article` / Aina AI Ring):

```json
{"headline": "Ekranlı ve mikrofonlu akıllı yüzük: Aina AI Ring",
 "author": "Erkan Calp", "date_published": "2026-11-06T20:44:00+03:00",
 "section": "Giyilebilir Teknolojiler", "word_count": 223, …}
```

## Nasıl çalışıyor?

donanimhaber.com haber sayfalarını tamamen sunucu taraflı render ediyor — giriş, API anahtarı ve oturum çerezi gerekmiyor. Listeleme sayfalarında `<article>` kartları bulunur (başlık, özet, kategori, "40,3b" = 40.300 gibi Türkçe formatlı görüntülenme, yorumlar; bölüm kartlarında ayrıca yayın tarihi). Haber sayfalarında schema.org NewsArticle JSON-LD bloğu bulunur (başlık, yazar, tarihler, bölüm, tam articleBody, yorum sayısı). Forumun popüler konuları forum.donanimhaber.com'da sunucu taraflı satırlar olarak yer alır. Aktarım Chrome TLS kimliğine bürünme kullanır (`curl-cffi`, `chrome120`); istekler ~0,8 sn arayla yapılır; her şey salt okunurdur.

2026-11-07'de canlı doğrulanan iki dürüst kısıtlama: (1) sitenin kendi `/ara?q=…` araması sorguyu yok sayıyor — her anahtar kelime için aynı 2 eski "ara" haberini döndürüyor — ve arama kutusu token gerektiren bir Yandex/Elastic widget'ı; bu nedenle `donanimhaber_search_news`, yeni çekilen en son + teknoloji listelerini istemci tarafında filtreler (Türkçe duyarlı, zekâ → zeka dönüşümü yapar); (2) forum araması da aynı şekilde token gerektirir, bu yüzden forumda anahtar kelime araması yoktur — `donanimhaber_forum_hot` sunucu taraflı popüler konuları listeler.

## Kurulum

```bash
uvx donanimhaber-mcp==0.1.0        # doğrudan çalıştır (uv gerekir)
# veya
pip install donanimhaber-mcp==0.1.0
donanimhaber-mcp    # MCP sunucusunu stdio üzerinde başlatır
```

## Testler

```bash
python -m venv .venv && .venv/bin/pip install -e .
.venv/bin/python -m unittest discover -s tests -v
```

Çevrimdışı testler kayıtlı örnek sayfalarla çalışır (2026-11-07'de çekilen gerçek sayfalar); canlı testler donanimhaber.com'a bağlanır. Derleme anında 32/32 yeşil (18 çevrimdışı + 14 canlı) ve bir MCP stdio duman testi (39 en son haber, 80 sıcak forum konusu).

## Yol haritası

- Forum kategori listeleri (`/<forum>--f<id>` konu listeleri)
- En çok okunan / en çok yorumlanan sıralamaları (ana sayfada yer alırlar)
- Haber yorumları (haber sayfası onlara bağlanır)

## Lisans

MIT — bkz. [LICENSE](LICENSE).
