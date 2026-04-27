"""
単一ポスターHTMLをPNG出力する汎用スクリプト
使い方: python export-single-poster.py <html名(拡張子なし)>
"""
import sys
from playwright.sync_api import sync_playwright
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def export(stem):
    poster_html = ROOT / "posters" / f"{stem}.html"
    out_png = ROOT / "posters" / f"{stem}.png"
    if not poster_html.exists():
        print(f"NOT FOUND: {poster_html}")
        return
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": 595, "height": 842},
            device_scale_factor=3,
        )
        page = context.new_page()
        url = "file:///" + str(poster_html).replace("\\", "/")
        page.goto(url, wait_until="networkidle")
        page.add_style_tag(content="body{margin:0!important;padding:0!important;display:block!important;min-height:auto!important}")
        page.evaluate("() => document.fonts.ready")
        page.wait_for_function("""
            () => {
                const targets = document.querySelectorAll('[style*="background-image"], .bg-photo, .hero, .hero-photo, .kanban, .photo');
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
    print(f"出力: {out_png.name} ({out_png.stat().st_size/1024/1024:.2f} MB)")

if __name__ == "__main__":
    for s in sys.argv[1:]:
        export(s)
