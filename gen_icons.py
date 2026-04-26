"""アイコンPNG生成スクリプト（Pillow不要・標準ライブラリのみ）"""
import struct, zlib, os, math

def make_png(size):
    """紫背景に音波アイコンのPNGを生成"""
    w = h = size
    # RGBA pixels
    pixels = []

    bg_r, bg_g, bg_b = 26, 26, 46       # #1a1a2e (dark navy)
    acc_r, acc_g, acc_b = 124, 58, 237   # #7c3aed (purple)
    icon_r, icon_g, icon_b = 226, 232, 240  # #e2e8f0 (light)

    # コーナー半径
    corner_r = size // 5

    for y in range(h):
        row = []
        for x in range(w):
            # 角丸マスク
            in_corner = False
            dx = min(x, w-1-x)
            dy = min(y, h-1-y)
            if dx < corner_r and dy < corner_r:
                dist = math.sqrt((corner_r-dx-1)**2 + (corner_r-dy-1)**2)
                if dist > corner_r:
                    in_corner = True

            if in_corner:
                row.extend([0, 0, 0, 0])  # 透明
                continue

            # 背景
            r, g, b, a = bg_r, bg_g, bg_b, 255

            # 中央アクセント円
            cx, cy = w / 2, h / 2
            circle_r = size * 0.38
            d = math.sqrt((x - cx)**2 + (y - cy)**2)
            if d <= circle_r:
                r, g, b = acc_r, acc_g, acc_b

            # 中央縦線（マイク/音シンボル）
            line_w = max(2, size // 30)
            line_h = size * 0.52
            ly1 = cy - line_h / 2
            ly2 = cy + line_h / 2
            lx1 = cx - line_w / 2
            lx2 = cx + line_w / 2
            if lx1 <= x <= lx2 and ly1 <= y <= ly2:
                r, g, b = icon_r, icon_g, icon_b

            # 音波1（内側）
            arc1_cx, arc1_cy = cx, cy
            arc1_r_inner = size * 0.18
            arc1_r_outer = size * 0.24
            arc1_d = math.sqrt((x - arc1_cx)**2 + (y - arc1_cy)**2)
            arc1_w = max(1, size // 40)
            # 左右の半円弧
            if arc1_r_inner <= arc1_d <= arc1_r_outer:
                if abs(x - cx) > size * 0.04:
                    r, g, b = icon_r, icon_g, icon_b

            # 音波2（外側）
            arc2_r_inner = size * 0.28
            arc2_r_outer = size * 0.33
            if arc2_r_inner <= arc1_d <= arc2_r_outer:
                if abs(x - cx) > size * 0.06:
                    r, g, b = icon_r, icon_g, icon_b

            row.extend([r, g, b, a])
        pixels.append(bytes(row))

    # PNGエンコード
    def chunk(tag, data):
        c = tag + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)

    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))

    raw = b''.join(b'\x00' + row for row in pixels)
    idat = chunk(b'IDAT', zlib.compress(raw, 9))
    iend = chunk(b'IEND', b'')

    return sig + ihdr + idat + iend


os.makedirs('icons', exist_ok=True)
for size in [192, 512]:
    data = make_png(size)
    path = f'icons/icon-{size}.png'
    with open(path, 'wb') as f:
        f.write(data)
    print(f'Generated {path} ({len(data)} bytes)')

print('Done.')
