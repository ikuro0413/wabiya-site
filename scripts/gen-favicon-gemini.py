"""
Gemini生成の書道「和」画像をもとにファビコン合成
- 白背景 → 透明化
- 墨(黒) → 指定色(金/白/えんじ)
- 黒丸円背景に重ねる
- 円枠あり/なし両対応
"""
from PIL import Image
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRAND = ROOT / "images" / "brand"
SRC = BRAND / "gemini-wa-0.png"  # AI生成元画像（書道・白背景・黒墨）

BLACK_BG = (26, 26, 26, 255)   # wabi-black
GOLD = (197, 165, 90)          # wabi-gold
WHITE = (245, 240, 230)        # 温かみのある白
ENJI = (168, 36, 52)           # 臙脂 (Japanese traditional dark crimson)
WABI_RED = (139, 20, 40)       # wabi-red (#8b1428) - サイトブランド色


def ink_to_color_rgba(src: Image.Image, color_rgb: tuple) -> Image.Image:
    """
    白背景＋黒墨の画像を、「透明背景＋指定色の墨」に変換。
    墨の濃さはアルファチャンネルで表現。
    """
    gray = src.convert("L")
    arr = np.array(gray, dtype=np.uint8)
    ink = 255 - arr  # 黒ければ濃い = 高い
    h, w = ink.shape
    out = np.zeros((h, w, 4), dtype=np.uint8)
    out[..., 0] = color_rgb[0]
    out[..., 1] = color_rgb[1]
    out[..., 2] = color_rgb[2]
    out[..., 3] = ink
    return Image.fromarray(out, mode="RGBA")


def circle_mask(size: int) -> Image.Image:
    """正方形画像に円形のアルファマスク (L)"""
    from PIL import ImageDraw
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([0, 0, size - 1, size - 1], fill=255)
    return m


def compose(src_ink: Image.Image, ring: bool, ring_color_rgb: tuple, out_name: str,
            canvas_size: int = 1024, padding: float = 0.08):
    """
    src_ink: 透明背景+色付き墨のRGBA画像
    ring: 金色の円枠を描くか
    """
    # 元画像は1024x1024想定だが、少し余白を入れて縮小してから黒丸に合成
    base = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    # 黒丸
    from PIL import ImageDraw
    d = ImageDraw.Draw(base)
    d.ellipse([0, 0, canvas_size - 1, canvas_size - 1], fill=BLACK_BG)

    # 墨を中央にフィット（少し内側にパディング）
    inner = int(canvas_size * (1 - padding * 2))
    ink_fitted = src_ink.resize((inner, inner), Image.LANCZOS)
    offset = (canvas_size - inner) // 2

    # 円形でクロップ（丸の外にはみ出す飛沫は切る）
    crop_mask = circle_mask(inner)
    ink_rgba = Image.new("RGBA", (inner, inner), (0, 0, 0, 0))
    ink_rgba.paste(ink_fitted, (0, 0), ink_fitted)
    # 円マスクをアルファと合成
    ia = np.array(ink_rgba.split()[3])
    cm = np.array(crop_mask)
    ia = np.minimum(ia, cm)
    ink_rgba.putalpha(Image.fromarray(ia))

    base.alpha_composite(ink_rgba, (offset, offset))

    # 金の円枠
    if ring:
        d2 = ImageDraw.Draw(base)
        stroke = max(4, canvas_size // 90)
        inset = canvas_size // 22
        d2.ellipse([inset, inset, canvas_size - 1 - inset, canvas_size - 1 - inset],
                   outline=(*ring_color_rgb, 255), width=stroke)

    base.save(BRAND / f"{out_name}.png")
    # preview sizes
    base.resize((120, 120), Image.LANCZOS).save(BRAND / f"{out_name}-120.png")
    base.resize((32, 32), Image.LANCZOS).save(BRAND / f"{out_name}-32.png")
    print(f"wrote {out_name}")


def main():
    src = Image.open(SRC).convert("RGBA")

    # 白バージョン
    white_ink = ink_to_color_rgba(src, WHITE)
    compose(white_ink, ring=True, ring_color_rgb=GOLD, out_name="v-white-ring")
    compose(white_ink, ring=False, ring_color_rgb=GOLD, out_name="v-white-noring")

    # えんじ(臙脂)バージョン
    enji_ink = ink_to_color_rgba(src, ENJI)
    compose(enji_ink, ring=True, ring_color_rgb=GOLD, out_name="v-enji-ring")
    compose(enji_ink, ring=False, ring_color_rgb=GOLD, out_name="v-enji-noring")

    # wabi-red バージョン (ブランド赤)
    wabired_ink = ink_to_color_rgba(src, WABI_RED)
    compose(wabired_ink, ring=True, ring_color_rgb=GOLD, out_name="v-wabired-ring")
    compose(wabired_ink, ring=False, ring_color_rgb=GOLD, out_name="v-wabired-noring")

    # 参考: 金色も引き続き並べる
    gold_ink = ink_to_color_rgba(src, GOLD)
    compose(gold_ink, ring=True, ring_color_rgb=GOLD, out_name="v-gold-ring")


if __name__ == "__main__":
    main()
