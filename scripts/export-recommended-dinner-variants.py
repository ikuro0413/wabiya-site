"""
ディナーおすすめメニュー 3バリアントHTMLをまとめてA4高解像度PNGエクスポート
"""
from playwright.sync_api import sync_playwright
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

VARIANTS = [
    ("menu-recommended-dinner-v2-hero.html", "menu-recommended-dinner-v2-hero.png"),
    ("menu-recommended-dinner-v3-washi.html", "menu-recommended-dinner-v3-washi.png"),
    ("menu-recommended-dinner-v4-magazine.html", "menu-recommended-dinner-v4-magazine.png"),
]

CLEAN_CSS = """
body {
  margin: 0 !important;
  padding: 0 !important;
  display: block !important;
  min-height: auto !important;
}
"""

SCALE = 3


def export_one(p, html_name, png_name):
    poster_html = ROOT / "posters" / html_name
    out_png = ROOT / "posters" / png_name

    browser = p.chromium.launch()
    context = browser.new_context(
        viewport={"width": 595, "height": 842},
        device_scale_factor=SCALE,
    )
    page = context.new_page()
    url = "file:///" + str(poster_html).replace("\\", "/")
    page.goto(url, wait_until="networkidle")

    page.add_style_tag(content=CLEAN_CSS)
    page.evaluate("() => document.fonts.ready")

    # 全ての .photo / .thumb / .hero / .card-hero の background-image が読み込まれるまで待機
    page.wait_for_function("""
        () => {
            const targets = document.querySelectorAll('.photo, .thumb, .hero, .card-hero .photo');
            if (targets.length === 0) return true;
            return [...targets].every(el => {
                const bg = window.getComputedStyle(el).backgroundImage;
                if (!bg || bg === 'none') return true;
                const m = bg.match(/url\\(["']?(.*?)["']?\\)/);
                if (!m) return true;
                const img = new Image();
                img.src = m[1];
                return img.complete && img.naturalHeight !== 0;
            });
        }
    """, timeout=20000)

    page.wait_for_timeout(1500)

    poster = page.locator(".poster")
    out_png.parent.mkdir(parents=True, exist_ok=True)
    poster.screenshot(path=str(out_png), omit_background=False)

    browser.close()

    size = out_png.stat().st_size
    print(f"出力完了: {out_png.name} ({size/1024/1024:.2f} MB)")


def main():
    with sync_playwright() as p:
        for html_name, png_name in VARIANTS:
            export_one(p, html_name, png_name)


if __name__ == "__main__":
    main()
