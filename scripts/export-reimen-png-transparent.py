"""
冷麺ポスターHTMLをPlaywright経由で「背景画像なし・透過PNG」で出力
- 背景写真とオーバーレイを非表示にして、テキスト・装飾のみを透過背景でキャプチャ
"""
from playwright.sync_api import sync_playwright
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTER_HTML = ROOT / "posters" / "poster-reimen.html"
OUT_PNG = ROOT / "posters" / "poster-reimen-transparent.png"

TRANSPARENT_CSS = """
html, body {
  margin: 0 !important;
  padding: 0 !important;
  background: transparent !important;
  display: block !important;
  min-height: auto !important;
}
.poster {
  background: transparent !important;
}
.bg-photo {
  display: none !important;
}
.overlay {
  display: none !important;
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

        page.add_style_tag(content=TRANSPARENT_CSS)

        page.evaluate("() => document.fonts.ready")
        page.wait_for_timeout(1000)

        poster = page.locator(".poster")
        OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
        poster.screenshot(path=str(OUT_PNG), omit_background=True)

        browser.close()

    size = OUT_PNG.stat().st_size
    print(f"出力完了: {OUT_PNG}")
    print(f"ファイル容量: {size:,} bytes ({size/1024/1024:.2f} MB)")


if __name__ == "__main__":
    main()
