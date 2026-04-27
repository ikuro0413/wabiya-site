"""
ディナーおすすめメニューHTMLをPlaywright経由でA4高解像度PNGにエクスポート
"""
from playwright.sync_api import sync_playwright
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTER_HTML = ROOT / "posters" / "menu-recommended-dinner.html"
OUT_PNG = ROOT / "posters" / "menu-recommended-dinner.png"

CLEAN_CSS = """
body {
  margin: 0 !important;
  padding: 0 !important;
  background: #0d0c0a !important;
  display: block !important;
  min-height: auto !important;
}
"""

SCALE = 3  # A4 @216dpi


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

        # 全ての .photo の background-image が読み込まれるまで待つ
        page.wait_for_function("""
            () => {
                const photos = document.querySelectorAll('.photo');
                if (photos.length === 0) return false;
                return [...photos].every(el => {
                    const bg = window.getComputedStyle(el).backgroundImage;
                    if (!bg || bg === 'none') return false;
                    const m = bg.match(/url\\(["']?(.*?)["']?\\)/);
                    if (!m) return false;
                    const img = new Image();
                    img.src = m[1];
                    return img.complete && img.naturalHeight !== 0;
                });
            }
        """, timeout=20000)

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
