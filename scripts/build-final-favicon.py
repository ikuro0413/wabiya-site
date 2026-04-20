"""
最終版ファビコン全サイズ生成
- マスター: images/brand/v-white-noring.png (書道「和」白字・黒丸背景・枠なし)
- 出力: favicon.ico (16/32/48/64), apple-touch-icon.png (180),
       images/brand/favicon-*.png (各サイズ),
       images/brand/instagram-profile.png (320),
       images/brand/tiktok-profile.png (200)
"""
from PIL import Image
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRAND = ROOT / "images" / "brand"
MASTER = BRAND / "favicon-master.png"

SIZES = [16, 32, 48, 64, 120, 180, 200, 320, 512, 1024]


def main():
    master = Image.open(MASTER).convert("RGBA")
    print(f"master: {master.size}")

    # 各サイズPNG (丸背景付きRGBA) → 16/32はJPEG風に背景付け
    for s in SIZES:
        img = master.resize((s, s), Image.LANCZOS)
        img.save(BRAND / f"favicon-{s}.png")
        print(f"  favicon-{s}.png")

    # apple-touch-icon
    master.resize((180, 180), Image.LANCZOS).save(ROOT / "apple-touch-icon.png")
    print("  apple-touch-icon.png")

    # favicon.ico (多サイズ内包)
    ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
    master.save(ROOT / "favicon.ico", format="ICO", sizes=ico_sizes)
    print(f"  favicon.ico {ico_sizes}")

    # SNS用 (最終版)
    master.resize((320, 320), Image.LANCZOS).save(BRAND / "instagram-profile.png")
    master.resize((200, 200), Image.LANCZOS).save(BRAND / "tiktok-profile.png")
    print("  instagram-profile.png / tiktok-profile.png")


if __name__ == "__main__":
    main()
