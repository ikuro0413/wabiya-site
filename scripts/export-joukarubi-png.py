"""
上カルビポスターHTMLをPlaywright経由で高解像度PNGにエクスポート
"""
from playwright.sync_api import sync_playwright
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTER_HTML = ROOT / "posters" / "poster-joukarubi.html"
OUT_PNG = ROOT / "posters" / "poster-joukarubi.png"

CLEAN_CSS = """
body {
  margin: 0 !important;
  padding: 0 !important;
  background: #0a0a0a !important;
  display: block !important;
  min-height: auto !important;
}
"""

SCALE = 3


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": 595, "height": 842},
            device_scale_factor=SCALE,
        )
        page = context.new_page()
        url = "file:///" + str(POSTER_HTML).replace("\\", "/")
        page.goto(url, wait_until="networkidle")

        page.add_style_tag(content=CLEAN_CSS)
        page.evaluate("() => document.fonts.ready")

        page.wait_for_function("""
            () => {
                const el = document.querySelector('.bg-photo');
                if (!el) return false;
                const bg = window.getComputedStyle(el).backgroundImage;
                if (!bg || bg === 'none') return false;
                const m = bg.match(/url\\(["']?(.*?)["']?\\)/);
                if (!m) return false;
                const img = new Image();
                img.src = m[1];
                return img.complete && img.naturalHeight !== 0;
            }
        """, timeout=15000)

        page.wait_for_timeout(1500)

        poster = page.locator(".poster")
        OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
        poster.screenshot(path=str(OUT_PNG), omit_background=False)

        browser.close()

    size = OUT_PNG.stat().st_size
    print(f"出力完了: {OUT_PNG}")
    print(f"ファイル容量: {size:,} bytes ({size/1024/1024:.2f} MB)")


if __name__ == "__main__":
    main()
