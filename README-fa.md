# donanimhaber-mcp 🇹🇷

mcp-name: io.github.mohammad-abbasi-sh/donanimhaber-mcp

سرور MCP غیررسمی و **فقط-خواندنی** برای donanimhaber.com، سایت پیشروی اخبار فناوری ترکیه + انجمن آن — تازه‌ترین اخبار فناوری، جست‌وجوی کلیدواژه، متن کامل خبر، فهرست بخش‌ها و داغ‌ترین موضوع‌های انجمن.

> ساخته‌شده توسط محمد عباسی در چارچوب «کارخانهٔ MCP ترکیه» (خط تولید به سبک سپهر). وابسته به donanimhaber.com نیست.

## برای ایجنت‌های هوش مصنوعی

به پیکربندی MCP client خود اضافه کنید (stdio):

```json
{
  "mcpServers": {
    "donanimhaber": {
      "command": "uvx",
      "args": ["donanimhaber-mcp==0.1.1"]
    }
  }
}
```

یا به‌صورت محلی اجرا کنید: `python -m donanimhaber_mcp.server` (نیازمند `mcp<2` و `curl-cffi`).

## ابزارها

| ابزار | توضیح |
|------|-------|
| `donanimhaber_latest` | تازه‌ترین اخبار فناوری (صفحهٔ اصلی) — `limit` ۱ تا ۵۰؛ خبرها (شناسه، عنوان، خلاصه، دسته، بازدید، نظر، URL) |
| `donanimhaber_search_news` | جست‌وجوی کلیدواژه در اخبار اخیر (عنوان، خلاصه، دسته) — `keyword`، `limit` ۱ تا ۵۰ |
| `donanimhaber_get_article` | متن کامل یک خبر — `article`: نشانی خبر، مسیر `/<slug>--<id>`، یا شناسهٔ عددی تنها (در تازه‌ترین فهرست‌ها جست‌وجو می‌شود)؛ تیتر، نویسنده، تاریخ‌ها، بخش، توضیح، متن کامل، تعداد نظر، تعداد کلمه |
| `donanimhaber_section` | خبرهای یک بخش/موضوع — `slug` از خروجی `donanimhaber_sections` (مثلاً «teknoloji-haberleri»، «yapay-zeka»، «bitcoin»، «gta-6»)، `limit` ۱ تا ۵۰ |
| `donanimhaber_sections` | همهٔ بخش‌ها/موضوع‌های خبری (نام + slug + URL) از صفحهٔ اصلی |
| `donanimhaber_forum_hot` | داغ‌ترین موضوع‌های انجمن DonanımHaber در حال حاضر — `limit` ۱ تا ۵۰؛ موضوع‌ها (شناسه، عنوان، زمان، انجمن، کاربران آنلاین، URL) |

خروجی نمونه (`donanimhaber_latest` / ۲۰۲۶-۱۱-۰۷):

```json
{"total": 39, "articles": [
  {"article_id": 212608, "title": "Yenilenen Volkswagen Virtus'un ilk fotoğrafları yayınlandı",
   "category": "Otomobil Teknolojileri",
   "url": "https://www.donanimhaber.com/yenilenen-volkswagen-virtus-un-ilk-fotograflari-yayinlandi--212608"}, …]}
```

خروجی نمونه (`donanimhaber_get_article` / Aina AI Ring):

```json
{"headline": "Ekranlı ve mikrofonlu akıllı yüzük: Aina AI Ring",
 "author": "Erkan Calp", "date_published": "2026-11-06T20:44:00+03:00",
 "section": "Giyilebilir Teknolojiler", "word_count": 223, …}
```

## نحوهٔ کار

donanimhaber.com صفحه‌های خبری را کاملاً سمت سرور رندر می‌کند — بدون ورود، کلید API و کوکی نشست. صفحه‌های فهرست کارت‌های `<article>` دارند (عنوان، خلاصه، دسته، بازدید با قالب ترکی مثل «40,3b» = ۴۰٬۳۰۰، نظرها؛ کارت‌های بخش تاریخ انتشار را هم دارند). صفحه‌های خبر بلوک NewsArticle از نوع JSON-LD از schema.org دارند (تیتر، نویسنده، تاریخ‌ها، بخش، articleBody کامل، تعداد نظر). موضوع‌های محبوب انجمن به‌صورت ردیف‌های سمت سرور در forum.donanimhaber.com هستند. انتقال با جعل TLS کروم انجام می‌شود (`curl-cffi`، `chrome120`)؛ درخواست‌ها با فاصلهٔ ‎~۰٫۸ ثانیه فرستاده می‌شوند؛ همه‌چیز فقط-خواندنی است.

دو محدودیت صادقانه که در ۲۰۲۶-۱۱-۰۷ به‌صورت زنده تأیید شد: (۱) جست‌وجوی `/ara?q=…` خود سایت رشتهٔ جست‌وجو را نادیده می‌گیرد — برای هر کلیدواژه همان ۲ خبر قدیمی «ara» را برمی‌گرداند — و جعبهٔ جست‌وجو یک ویجت Yandex/Elastic نیازمند توکن است؛ پس `donanimhaber_search_news` در عوض تازه‌ترین فهرست‌های دریافت‌شده + فناوری را سمت کاربر فیلتر می‌کند (حساس به ترکی، با تبدیل zekâ به zeka)؛ (۲) جست‌وجوی انجمن هم به همان شکل نیازمند توکن است، پس جست‌وجوی کلیدواژه برای انجمن وجود ندارد — `donanimhaber_forum_hot` موضوع‌های محبوب رندرشدهٔ سمت سرور را فهرست می‌کند.

## نصب

```bash
uvx donanimhaber-mcp==0.1.1        # اجرای مستقیم (نیازمند uv)
# یا
pip install donanimhaber-mcp==0.1.1
donanimhaber-mcp    # سرور MCP را روی stdio راه می‌اندازد
```

## تست‌ها

```bash
python -m venv .venv && .venv/bin/pip install -e .
.venv/bin/python -m unittest discover -s tests -v
```

تست‌های آفلاین روی صفحات ضبط‌شده اجرا می‌شوند (صفحات واقعی دریافت‌شده در ۲۰۲۶-۱۱-۰۷)؛ تست‌های زنده به donanimhaber.com وصل می‌شوند. در زمان ساخت ۳۲ از ۳۲ سبز بود (۱۸ آفلاین + ۱۴ زنده) به‌همراه یک تست دود MCP روی stdio (۳۹ خبر تازه، ۸۰ موضوع داغ انجمن).

## نقشهٔ راه

- فهرست دسته‌های انجمن (فهرست موضوع‌های `/<forum>--f<id>`)
- رتبه‌بندی پربازدیدترین / پرنظرترین (در صفحهٔ اصلی هستند)
- نظرهای خبر (صفحهٔ خبر به آن‌ها پیوند می‌دهد)

## مجوز

MIT — ببینید [LICENSE](LICENSE).

---

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
