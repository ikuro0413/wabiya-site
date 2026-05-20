"""
ポスターHTMLをPlaywright経由で高解像度PNGにエクスポート
- Google Fonts / QR画像がすべて読み込まれるまで待機
- A4 3x解像度（1785 x 2526）で出力

使い方:
    # デフォルト(survey)
    python scripts/export-poster-png.py

    # 別ポスター
    python scripts/export-poster-png.py poster-reimen.html "わびや_冷麺ポスター.png"
    python scripts/export-poster-png.py poster-dinner.html
"""
import sys
from playwright.sync_api import sync_playwright
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# CLI引数: 1=html名, 2=出力PNGファイル名（デスクトップ配下）
DEFAULT_HTML = "poster-survey.html"
DEFAULT_OUT_NAMES = {
    "poster-survey.html":  "わびや_店内アンケートポスター.png",
    "poster-reimen.html":  "わびや_冷麺ポスター.png",
    "poster-dinner.html":  "わびや_ディナーポスター.png",
    "poster-lunch.html":   "わびや_ランチポスター.png",
    "poster-concept.html": "わびや_コンセプトポスター.png",
    "poster-joukarubi.html": "わびや_上カルビポスター.png",
}

html_name = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HTML
out_name  = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUT_NAMES.get(html_name, html_name.replace(".html", ".png"))

POSTER_HTML = ROOT / "posters" / html_name
OUT_PNG = Path("C:/Users/ikuro/OneDrive/デスクトップ") / out_name

if not POSTER_HTML.exists():
    print(f"ERROR: ファイルが見つかりません: {POSTER_HTML}")
    sys.exit(1)

# body の背景色調整用 JS（多くのポスターで余白排除）
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

        # QRコード画像があれば読込完了を待つ（無ければスキップ）
        has_qr = page.evaluate("() => !!document.querySelector('.qr-wrap img')")
        if has_qr:
            page.wait_for_function("""
                () => {
                    const img = document.querySelector('.qr-wrap img');
                    return img && img.complete && img.naturalHeight !== 0;
                }
            """, timeout=15000)

        # 全画像の読込完了を待つ（あれば）
        page.evaluate("""
            () => Promise.all(
                Array.from(document.images)
                    .filter(img => !img.complete)
                    .map(img => new Promise(res => { img.onload = res; img.onerror = res; }))
            )
        """)

        # 念のため1秒待ってからスクショ
        page.wait_for_timeout(1000)

        # .poster 要素があればそれだけクリップ、無ければページ全体
        OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
        poster_locator = page.locator(".poster")
        if poster_locator.count() > 0:
            poster_locator.first.screenshot(path=str(OUT_PNG), omit_background=False)
        else:
            page.screenshot(path=str(OUT_PNG), full_page=True, omit_background=False)

        browser.close()

    size = OUT_PNG.stat().st_size
    print(f"入力: {POSTER_HTML.name}")
    print(f"出力: {OUT_PNG}")
    print(f"容量: {size:,} bytes ({size/1024/1024:.2f} MB)")


if __name__ == "__main__":
    main()
