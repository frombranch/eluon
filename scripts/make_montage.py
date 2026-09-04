#!/usr/bin/env python3
"""
make_montage.py — 전체 자산을 라벨과 함께 한 장으로 합칩니다. (몽타주 시트)

개별 이미지 22장을 첨부하는 것보다, 라벨이 박힌 시트 1장을 첨부하는 쪽이
에이전트가 라이브러리 전체를 파악하고 정확한 ID로 지목하는 데 훨씬 유리합니다.

사용:
    python3 scripts/make_montage.py                 # 테마별 전체 시트
    python3 scripts/make_montage.py --theme eluo
    python3 scripts/make_montage.py --group button --theme eluo
"""
import argparse
import json
import pathlib
import sys
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "eluon.config.json").read_text(encoding="utf-8"))
S = CONFIG["sheet"]

HOME = pathlib.Path.home()

# 컴포넌트 PNG와 같은 서체(Pretendard)를 우선 씁니다. 없으면 한글이 있는 시스템 폰트로,
# 그것도 없으면 마지막에 기본 비트맵 폰트로 떨어지는데 — 그 경우 한글이 두부(□)로 깨집니다.
BOLD = [str(HOME / "Library/Fonts/Pretendard-Bold.otf"),
        str(HOME / "Library/Fonts/Pretendard-Bold.ttf"),
        "/root/.fonts/Pretendard-Bold.otf",
        "/usr/share/fonts/truetype/pretendard/Pretendard-Bold.ttf",
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        "/System/Library/Fonts/Supplemental/AppleSDGothicNeo.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"]
REG = [str(HOME / "Library/Fonts/Pretendard-Regular.otf"),
       str(HOME / "Library/Fonts/Pretendard-Regular.ttf"),
       "/root/.fonts/Pretendard-Regular.otf",
       "/usr/share/fonts/truetype/pretendard/Pretendard-Regular.ttf",
       "/System/Library/Fonts/AppleSDGothicNeo.ttc",
       "/System/Library/Fonts/Supplemental/AppleSDGothicNeo.ttc",
       "/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc"]


def font(cands, size):
    for path in cands:
        if pathlib.Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    # 여기까지 오면 한글이 깨집니다. 조용히 넘어가지 않고 알립니다.
    print("⚠ 한글 폰트를 찾지 못했습니다 — 시트의 한글이 깨집니다. "
          "Pretendard를 설치하거나 make_montage.py의 폰트 후보 경로를 확인하세요.",
          file=sys.stderr)
    return ImageFont.load_default()


def contain(im, box_w, box_h):
    """비율 유지하며 박스 안에 맞춥니다. 자르거나 늘이지 않습니다."""
    ratio = min(box_w / im.width, box_h / im.height, 1.0)
    if ratio < 1.0:
        im = im.resize((max(1, round(im.width * ratio)),
                        max(1, round(im.height * ratio))), Image.LANCZOS)
    return im


def sheet_for(assets, theme, out_rel, subtitle):
    cols, cw, ch = S["columns"], S["cellWidth"], S["cellHeight"]
    pad, header, label_h = 40, 132, 64
    rows = (len(assets) + cols - 1) // cols
    W = pad * 2 + cw * cols
    H = header + pad + rows * ch + pad

    sheet = Image.new("RGB", (W, H), S["background"])
    d = ImageDraw.Draw(sheet)
    f_title, f_sub = font(BOLD, 34), font(REG, 18)
    f_id, f_meta = font(BOLD, 19), font(REG, 15)

    d.text((pad, 42), f"Eluon — {theme}", font=f_title, fill=S["labelColor"])
    d.text((pad, 88), subtitle, font=f_sub, fill=S["mutedColor"])
    d.line([(pad, header - 8), (W - pad, header - 8)], fill="#2A2A32", width=1)

    for i, a in enumerate(assets):
        r, c = divmod(i, cols)
        x0, y0 = pad + c * cw, header + pad + r * ch
        d.rounded_rectangle([x0 + 6, y0 + 6, x0 + cw - 6, y0 + ch - 6],
                            radius=14, fill="#17171C", outline="#2A2A32")
        # 자산은 투명 배경이므로 밝은 면 위에 올려 미리보기합니다.
        top, bot = y0 + 18, y0 + ch - label_h - 6
        d.rounded_rectangle([x0 + 18, top, x0 + cw - 18, bot],
                            radius=10, fill=S.get("previewSurface", "#F4F5F8"))

        img = ROOT / a["renders"][theme]
        if img.exists():
            thumb = contain(Image.open(img).convert("RGBA"), cw - 72, (bot - top) - 28)
            sheet.paste(thumb, (x0 + (cw - thumb.width) // 2,
                                top + ((bot - top) - thumb.height) // 2), thumb)

        ly = y0 + ch - label_h
        d.text((x0 + 22, ly), a["id"], font=f_id, fill=S["labelColor"])
        s = a.get("spec", {})
        bits = [a["name"]]
        if "height" in s:
            bits.append(f"h{s['height']}")
        if "radius" in s:
            bits.append(f"r:{s['radius']}")
        d.text((x0 + 22, ly + 26), "  ·  ".join(bits), font=f_meta, fill=S["mutedColor"])

    out = ROOT / out_rel
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, "PNG")
    print(f"✓ {out_rel}  ({W}x{H}, 자산 {len(assets)}개)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--theme", choices=CONFIG["themes"])
    ap.add_argument("--group")
    args = ap.parse_args()

    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    base = [a for a in manifest["assets"]
            if a.get("status") != "deprecated" and not a.get("variantOf")]
    if args.group:
        base = [a for a in base if a["group"] == args.group]
    base.sort(key=lambda a: (a["group"], a["id"]))
    if not base:
        raise SystemExit("출력할 자산이 없습니다.")

    for theme in ([args.theme] if args.theme else CONFIG["themes"]):
        suffix = f"-{args.group}" if args.group else ""
        sheet_for(base, theme, f"index/sheet-{theme}{suffix}.png",
                  f'{manifest["version"]} · 자산 {len(base)}개 · '
                  f'아래 라벨의 ID로 지목하세요 (예: "btn-primary-lg 로 CTA 만들어줘")')


if __name__ == "__main__":
    main()
