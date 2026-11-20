import math
import random
import sys

import pygame

# ---------------- colours
PINK = (255, 120, 190)
RED = (235, 45, 55)
PURPLE = (170, 95, 235)
YELLOW = (255, 215, 40)
ORANGE = (255, 140, 30)
WHITE = (245, 245, 245)
GOLD_CENTER = (255, 190, 30)
DARK_CENTER = (120, 70, 20)
GREEN = (110, 220, 70)
STEM_GREEN = (60, 170, 60)
WRAP = (225, 215, 200)
RIBBON = (255, 105, 160)

FLOWER_TYPES = [
    (WHITE, GOLD_CENTER, 12),     # daisy
    (PINK, GOLD_CENTER, 8),       # pink cosmos
    (RED, DARK_CENTER, 6),        # red
    (PURPLE, GOLD_CENTER, 7),     # purple
    (YELLOW, DARK_CENTER, 12),    # sunflower-ish
    (ORANGE, DARK_CENTER, 9),     # orange
]
TULIP_COLORS = [RED, PINK, YELLOW]
SHADES = ".,-~:;=!*#$@"


# ---------------- vectors
def norm(v):
    m = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2) or 1.0
    return (v[0] / m, v[1] / m, v[2] / m)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def basis(axis):
    helper = (0.0, 1.0, 0.0) if abs(axis[1]) < 0.9 else (1.0, 0.0, 0.0)
    u = norm(cross(helper, axis))
    return u, cross(axis, u)


def add(p, d, k):
    return (p[0] + d[0] * k, p[1] + d[1] * k, p[2] + d[2] * k)


def lin(*terms):
    x = y = z = 0.0
    for v, k in terms:
        x += v[0] * k
        y += v[1] * k
        z += v[2] * k
    return (x, y, z)


# ---------------- parts
def make_flower(pts, pos, axis, petal_col, center_col, n_petals, size, rnd):
    u, v = basis(axis)
    for i in range(260):
        r = size * 0.28 * math.sqrt(rnd.random())
        a = rnd.random() * 2 * math.pi
        dome = 0.04 * size * (1 - (r / (size * 0.28)) ** 2)
        p = add(pos, lin((u, r * math.cos(a)), (v, r * math.sin(a)), (axis, dome)), 1)
        pts.append((p, axis, center_col))
    twist = rnd.random() * 2 * math.pi
    for k in range(n_petals):
        ang = twist + k * 2 * math.pi / n_petals
        dirp = lin((u, math.cos(ang)), (v, math.sin(ang)))
        side = lin((u, -math.sin(ang)), (v, math.cos(ang)))
        for i in range(150):
            t = rnd.random()
            w = math.sin(math.pi * t) * size * 0.16 * (rnd.random() * 2 - 1)
            r = size * (0.25 + 0.75 * t)
            cup = size * 0.35 * t * t
            p = add(pos, lin((dirp, r), (side, w), (axis, cup)), 1)
            n = norm(lin((axis, 1.0), (dirp, -0.5 * t)))
            pts.append((p, n, petal_col))


def make_tulip(pts, pos, axis, col, size, rnd):
    u, v = basis(axis)
    for i in range(900):
        t = rnd.random()
        a = rnd.random() * 2 * math.pi
        rad = size * 0.5 * math.sin(math.pi * (0.12 + 0.75 * t)) ** 0.7
        top = 1.0 + 0.12 * abs(math.sin(3 * a))
        h = size * 1.1 * t * top
        radial = lin((u, math.cos(a)), (v, math.sin(a)))
        p = add(pos, lin((radial, rad), (axis, h - size * 0.3)), 1)
        pts.append((p, radial, col))


def make_line(pts, a, b, col, n):
    d = norm((b[0] - a[0], b[1] - a[1], b[2] - a[2]))
    side = basis(d)[0]
    for i in range(n):
        t = i / (n - 1)
        pts.append(((a[0] + (b[0] - a[0]) * t,
                     a[1] + (b[1] - a[1]) * t,
                     a[2] + (b[2] - a[2]) * t), side, col))


def make_leaf(pts, base, direction, length, width, rnd):
    d = norm(direction)
    side = norm(cross(d, (0.0, 1.0, 0.0))) if abs(d[1]) < 0.95 else (1.0, 0.0, 0.0)
    n = norm(cross(d, side))
    for i in range(500):
        t = rnd.random()
        w = math.sin(math.pi * t) * width * (rnd.random() * 2 - 1)
        droop = -0.25 * length * t * t
        p = add(base, lin((d, length * t), (side, w), ((0, 1, 0), droop)), 1)
        pts.append((p, n, GREEN))


def build_scene():
    rnd = random.Random(21)
    pts = []
    neck = (0.0, -0.12, 0.0)

    C, R = (0.0, 0.12, 0.0), 0.64
    N = 10
    golden = math.pi * (3 - math.sqrt(5))
    heads = []
    for i in range(N):
        el = math.radians(88 - 60 * math.sqrt(i / (N - 1)))
        az = i * golden
        d = (math.cos(el) * math.cos(az), math.sin(el), math.cos(el) * math.sin(az))
        pos = add(C, d, R * rnd.uniform(0.92, 1.05))
        heads.append((pos, norm(d)))

    tulip_slots = (3, 8)
    for idx, (pos, axis) in enumerate(heads):
        make_line(pts, add(pos, axis, -0.03), neck, STEM_GREEN, 70)
        if idx in tulip_slots:
            make_tulip(pts, pos, axis, rnd.choice(TULIP_COLORS), 0.21, rnd)
        else:
            petal, center, n = FLOWER_TYPES[idx % len(FLOWER_TYPES)]
            make_flower(pts, pos, axis, petal, center, n, rnd.uniform(0.19, 0.23), rnd)

    for k in range(7):
        a = k * 2 * math.pi / 7 + 0.3
        direction = (math.cos(a), 0.55 + 0.25 * rnd.random(), math.sin(a))
        make_leaf(pts, add(neck, (0, 1, 0), 0.25), direction, 0.55, 0.09, rnd)

    apex_y, top_y, top_r = -0.8, 0.1, 0.42
    for i in range(9000):
        t = rnd.random()
        a = rnd.random() * 2 * math.pi
        rad = top_r * t
        y = apex_y + (top_y - apex_y) * t
        n = norm((math.cos(a), top_r / (top_y - apex_y), math.sin(a)))
        stripe = 0.85 if int(t * 22) % 2 else 1.0
        col = tuple(int(c * stripe) for c in WRAP)
        pts.append(((rad * math.cos(a), y, rad * math.sin(a)), n, col))

    ry = -0.56
    t_r = (ry - apex_y) / (top_y - apex_y)
    for i in range(900):
        a = rnd.random() * 2 * math.pi
        y = ry + rnd.uniform(-0.035, 0.035)
        rad = top_r * (y - apex_y) / (top_y - apex_y) + 0.012
        pts.append(((rad * math.cos(a), y, rad * math.sin(a)),
                    (math.cos(a), 0.0, math.sin(a)), RIBBON))
    front = (0.0, ry, top_r * t_r + 0.02)
    for s in (-1, 1):
        make_line(pts, front, add(front, (s * 0.10, -0.22, 0.04), 1), RIBBON, 45)
        make_line(pts, front, add(front, (s * 0.12, 0.05, 0.03), 1), RIBBON, 30)

    for k in range(5):
        x = (k - 2) * 0.025
        make_line(pts, (x, apex_y + 0.05, 0.0), (x * 2.2, apex_y - 0.22, 0.0), STEM_GREEN, 40)

    return pts


# ---------------- render
W, H = 760, 980
CELL_W, CELL_H = 7, 11
COLS, ROWS = W // CELL_W, H // CELL_H
BG = (14, 16, 30)


def project(pts, yaw, pitch):
    cy_, sy_ = math.cos(yaw), math.sin(yaw)
    cp, sp = math.cos(pitch), math.sin(pitch)
    light = norm((-0.5, 0.6, 0.9))
    cam = 2.6
    scale = H * 0.98
    cx, cy = COLS / 2, ROWS * 0.50
    cells = {}
    nshades = len(SHADES)
    for (x, y, z), (nx, ny, nz), col in pts:
        x2 = x * cy_ + z * sy_
        z2 = -x * sy_ + z * cy_
        y3 = y * cp - z2 * sp
        z3 = y * sp + z2 * cp
        ooz = 1.0 / (cam - z3)
        gx = int(cx + x2 * scale * ooz / CELL_W)
        gy = int(cy - y3 * scale * ooz / CELL_H)
        if not (0 <= gx < COLS and 0 <= gy < ROWS):
            continue
        key = gy * COLS + gx
        old = cells.get(key)
        if old is not None and old[0] >= ooz:
            continue
        nx2 = nx * cy_ + nz * sy_
        nz2 = -nx * sy_ + nz * cy_
        ny3 = ny * cp - nz2 * sp
        nz3 = ny * sp + nz2 * cp
        lum = abs(nx2 * light[0] + ny3 * light[1] + nz3 * light[2])
        fog = max(0.6, min(1.0, 0.7 + (ooz - 1 / cam) * 3.0))
        lvl = min(nshades - 1, int((0.3 + 0.7 * lum) * nshades))
        cells[key] = (ooz, lvl, col, fog)
    return cells


class GlyphCache:
    def __init__(self, font):
        self.font = font
        self.cache = {}

    def get(self, ch, rgb):
        key = (ch, rgb)
        g = self.cache.get(key)
        if g is None:
            g = self.font.render(ch, True, rgb)
            self.cache[key] = g
        return g


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("for you")
    font = pygame.font.SysFont("menlo,consolas,dejavusansmono,couriernew,monospace", 12, bold=True)
    big = pygame.font.SysFont("menlo,consolas,dejavusansmono,couriernew,monospace", 22, bold=True)
    glyphs = GlyphCache(font)
    clock = pygame.time.Clock()

    pts = build_scene()
    rnd = random.Random(7)
    sparkles = [(rnd.randrange(COLS), rnd.randrange(ROWS), rnd.random() * 6.28) for _ in range(90)]

    yaw, pitch = 0.0, 0.2
    spin = 0.015
    dragging = False
    t = 0
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                dragging = True
            if ev.type == pygame.MOUSEBUTTONUP:
                dragging = False
            if ev.type == pygame.MOUSEMOTION and dragging:
                yaw += ev.rel[0] * 0.01
                pitch = max(-0.6, min(0.9, pitch + ev.rel[1] * 0.01))

        if not dragging:
            yaw += spin
            pitch = 0.2 + 0.12 * math.sin(t * 0.02)

        screen.fill(BG)

        for gx, gy, ph in sparkles:
            b = (math.sin(t * 0.08 + ph) + 1) / 2
            if b > 0.5:
                ch = "*" if b > 0.9 else ("+" if b > 0.72 else ".")
                g = int(120 + 135 * b)
                screen.blit(glyphs.get(ch, (g, int(g * 0.8), g)), (gx * CELL_W, gy * CELL_H))

        cells = project(pts, yaw, pitch)
        for key, (ooz, lvl, col, fog) in cells.items():
            k = (0.55 + 0.45 * lvl / (len(SHADES) - 1)) * fog
            rgb = (int(col[0] * k) & 0xF8, int(col[1] * k) & 0xF8, int(col[2] * k) & 0xF8)
            screen.blit(glyphs.get(SHADES[lvl], rgb), ((key % COLS) * CELL_W, (key // COLS) * CELL_H))

        txt = big.render("te iubesc alel", True, PINK)
        screen.blit(txt, ((W - txt.get_width()) // 2, H - 48))

        pygame.display.flip()
        clock.tick(40)
        t += 1


if __name__ == "__main__":
    main()