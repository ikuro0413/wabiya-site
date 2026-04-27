"""
ポスターHTMLをPlaywright経由で高解像度PNGにエクスポート
- Google Fonts / QR画像がすべて読み込まれるまで待機
- A4 3x解像度（1785 x 2526）で出力
"""
from playwright.sync_api import sync_playwright
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTER_HTML = ROOT / "posters" / "poster-survey.html"
OUT_PNG = Path("C:/Users/ikuro/OneDrive/デスクトップ/わびや_店内アンケートポスター.png")

# body の背景色調整用 JS
CLEAN_CSS = """
body {
  margin: 0 !important;
  padding: 0 !important;
  background: #0a0a0a !important;
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

        # body余白を除去
        page.add_style_tag(content=CLEAN_CSS)

        # Google Fonts 読込完了を待つ
        page.evaluate("() => document.fonts.ready")

        # QRコード画像の読込完了を待つ
        page.wait_for_function("""
            () => {
                const img = document.querySelector('.qr-wrap img');
                return img && img.complete && img.naturalHeight !== 0;
            }
        """, timeout=15000)

        # 念のため1秒待ってからスクショ
        page.wait_for_timeout(1000)

        # .poster 要素だけクリップしてスクリーンショット
        poster = page.locator(".poster")
        OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
        poster.screenshot(path=str(OUT_PNG), omit_background=False)

        browser.close()

    size = OUT_PNG.stat().st_size
    print(f"出力完了: {OUT_PNG}")
    print(f"ファイル容量: {size:,} bytes ({size/1024/1024:.2f} MB)")


if __name__ == "__main__":
    main()
