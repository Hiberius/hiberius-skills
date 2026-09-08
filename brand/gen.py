#!/usr/bin/env python3
"""Liquid Glass Brutalist - the visual system for the Hiberius skill set.

One script draws every banner and every diagram in the set, which is what makes ten
repositories look like one hand. The structure is brutalist: an exposed grid, hard
corners, hairline rules, monospace labels. The surfaces are glass: layered translucent
panels with a specular sweep and one accent glow bleeding from an edge.

Each skill varies exactly one thing, its accent hue, plus a signature motif drawn from
its own subject. Everything else is shared.

  python3 gen.py            write every asset into ../../<repo>/assets/
  python3 gen.py --check    render to /tmp and validate, write nothing

Pure standard library. The SVGs use no external font, no script and no remote asset,
because GitHub sanitises SVG and refuses anything else.
"""
from __future__ import annotations

import os
import sys
import xml.etree.ElementTree as ET

# --------------------------------------------------------------------------
# tokens
# --------------------------------------------------------------------------

W = 1200
SANS = ('system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif')
MONO = ('ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace')

THEME = {
    "dark": {
        "ground": "#050709",
        "ground2": "#101619",
        "grid": "#FFFFFF",
        "grid_op": 0.075,
        "panel_a": 0.115,          # glass fill, top
        "panel_b": 0.032,          # glass fill, bottom
        "tint": 0.075,             # how much colour the glass picks up
        "hairline": "#FFFFFF",
        "hairline_op": 0.20,
        "sheen": 0.17,
        "ink": "#F1F5F7",
        "ink_soft": "#A6B1B8",
        "ink_faint": "#7A868E",
        "glow_op": 0.55,
        "shadow": 0.0,
    },
    "light": {
        "ground": "#E7EBEE",
        "ground2": "#FBFCFD",
        "grid": "#0A0C0E",
        "grid_op": 0.07,
        "panel_a": 0.95,
        "panel_b": 0.74,
        "tint": 0.055,
        "hairline": "#0A0C0E",
        "hairline_op": 0.15,
        "sheen": 0.85,
        "ink": "#0A0F13",
        "ink_soft": "#48545B",
        "ink_faint": "#6E7A81",
        "glow_op": 0.30,
        "shadow": 0.16,
    },
}


def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def panel_fill(mode, a=None, b=None):
    """Glass is white in the dark theme and white in the light theme; only the alpha
    changes. Keeping one fill colour is what makes the two themes feel like one object."""
    t = THEME[mode]
    a = t["panel_a"] if a is None else a
    b = t["panel_b"] if b is None else b
    return a, b


class Canvas:
    def __init__(self, mode, width, height, accent):
        self.mode = mode
        self.t = THEME[mode]
        self.w = width
        self.h = height
        self.accent = accent
        self.defs = []
        self.body = []
        self._uid = 0

    def uid(self, prefix="g"):
        self._uid += 1
        return "%s%d" % (prefix, self._uid)

    def add(self, s):
        self.body.append(s)

    def add_def(self, s):
        self.defs.append(s)

    # ---- primitives -------------------------------------------------------

    def ground(self):
        t = self.t
        gid = self.uid("bg")
        self.add_def(
            '<linearGradient id="%s" x1="0" y1="0" x2="0.35" y2="1">'
            '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/>'
            '</linearGradient>' % (gid, t["ground2"], t["ground"]))
        self.add('<rect width="%d" height="%d" fill="url(#%s)"/>' % (self.w, self.h, gid))

    def grid(self, step=40, fade=True):
        """The exposed grid. Brutalism's structural honesty, kept faint so it reads as
        paper rather than as decoration."""
        t = self.t
        pid = self.uid("grid")
        self.add_def(
            '<pattern id="%s" width="%d" height="%d" patternUnits="userSpaceOnUse">'
            '<path d="M %d 0 L 0 0 0 %d" fill="none" stroke="%s" stroke-opacity="%.3f" '
            'stroke-width="1"/></pattern>' % (pid, step, step, step, step,
                                              t["grid"], t["grid_op"]))
        if fade:
            mid = self.uid("gmask")
            self.add_def(
                '<radialGradient id="%s" cx="0.42" cy="0.5" r="0.75">'
                '<stop offset="0" stop-color="#fff" stop-opacity="1"/>'
                '<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
                '<mask id="%sm"><rect width="%d" height="%d" fill="url(#%s)"/></mask>'
                % (mid, mid, self.w, self.h, mid))
            self.add('<rect width="%d" height="%d" fill="url(#%s)" mask="url(#%sm)"/>'
                     % (self.w, self.h, pid, mid))
        else:
            self.add('<rect width="%d" height="%d" fill="url(#%s)"/>'
                     % (self.w, self.h, pid))

    def glow(self, cx, cy, r, opacity=None, color=None):
        t = self.t
        gid = self.uid("glow")
        op = t["glow_op"] if opacity is None else opacity
        col = color or self.accent
        self.add_def(
            '<radialGradient id="%s" cx="0.5" cy="0.5" r="0.5">'
            '<stop offset="0" stop-color="%s" stop-opacity="%.3f"/>'
            '<stop offset="0.55" stop-color="%s" stop-opacity="%.3f"/>'
            '<stop offset="1" stop-color="%s" stop-opacity="0"/></radialGradient>'
            % (gid, col, op, col, op * 0.35, col))
        self.add('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="url(#%s)"/>'
                 % (cx, cy, r, gid))

    def glass(self, x, y, w, h, r=2, sheen=True, a=None, b=None, stroke_op=None):
        """A pane. Layered fill, a top edge highlight, one diagonal specular sweep,
        and a hairline that does not soften at the corners."""
        t = self.t
        fa, fb = panel_fill(self.mode, a, b)
        gid = self.uid("pane")
        self.add_def(
            '<linearGradient id="%s" x1="0" y1="0" x2="0.2" y2="1">'
            '<stop offset="0" stop-color="#FFFFFF" stop-opacity="%.3f"/>'
            '<stop offset="1" stop-color="#FFFFFF" stop-opacity="%.3f"/>'
            '</linearGradient>' % (gid, fa, fb))
        out = []
        if t["shadow"] > 0:
            fid = self.uid("sh")
            self.add_def('<filter id="%s" x="-20%%" y="-20%%" width="140%%" height="160%%">'
                         '<feDropShadow dx="0" dy="6" stdDeviation="10" '
                         'flood-color="#0A0C0E" flood-opacity="%.3f"/></filter>'
                         % (fid, t["shadow"]))
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%d" '
                       'fill="url(#%s)" filter="url(#%s)"/>' % (x, y, w, h, r, gid, fid))
        else:
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%d" '
                       'fill="url(#%s)"/>' % (x, y, w, h, r, gid))
        if sheen:
            sid = self.uid("sheen")
            cid = self.uid("clip")
            self.add_def(
                '<linearGradient id="%s" x1="0" y1="0" x2="1" y2="0.8">'
                '<stop offset="0" stop-color="#FFFFFF" stop-opacity="0"/>'
                '<stop offset="0.42" stop-color="#FFFFFF" stop-opacity="%.3f"/>'
                '<stop offset="0.56" stop-color="#FFFFFF" stop-opacity="0"/>'
                '</linearGradient>'
                '<clipPath id="%s"><rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                'rx="%d"/></clipPath>' % (sid, t["sheen"] * 0.9, cid, x, y, w, h, r))
            out.append('<g clip-path="url(#%s)"><rect x="%.1f" y="%.1f" width="%.1f" '
                       'height="%.1f" fill="url(#%s)"/></g>'
                       % (cid, x, y, w, h, sid))
        eid = self.uid("edge")
        self.add_def(
            '<linearGradient id="%s" x1="0" y1="0" x2="1" y2="0">'
            '<stop offset="0" stop-color="#FFFFFF" stop-opacity="0"/>'
            '<stop offset="0.25" stop-color="#FFFFFF" stop-opacity="%.3f"/>'
            '<stop offset="0.75" stop-color="#FFFFFF" stop-opacity="%.3f"/>'
            '<stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient>'
            % (eid, t["sheen"] * 2.2, t["sheen"] * 0.8))
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="1" fill="url(#%s)"/>'
                   % (x, y, w, eid))
        # the glass picks up colour from what is behind it: that is the liquid part
        tid = self.uid("tint")
        self.add_def(
            '<linearGradient id="%s" x1="1" y1="0" x2="0" y2="1">'
            '<stop offset="0" stop-color="%s" stop-opacity="%.3f"/>'
            '<stop offset="0.7" stop-color="%s" stop-opacity="0"/></linearGradient>'
            % (tid, self.accent, t["tint"], self.accent))
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%d" '
                   'fill="url(#%s)"/>' % (x, y, w, h, r, tid))
        so = t["hairline_op"] if stroke_op is None else stroke_op
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%d" fill="none" '
                   'stroke="%s" stroke-opacity="%.3f" stroke-width="1"/>'
                   % (x + .5, y + .5, w - 1, h - 1, r, t["hairline"], so))
        self.add("".join(out))

    def marks(self, x, y, w, h, size=13, inset=9):
        """Registration marks at the corners. Print-shop brutalism: the crop marks
        stay visible on the finished piece."""
        t = self.t
        op = t["hairline_op"] * 2.2
        for cx, cy, dx, dy in ((x, y, 1, 1), (x + w, y, -1, 1),
                               (x, y + h, 1, -1), (x + w, y + h, -1, -1)):
            self.add('<path d="M %.1f %.1f h %.1f M %.1f %.1f v %.1f" stroke="%s" '
                     'stroke-opacity="%.3f" stroke-width="1"/>'
                     % (cx + dx * inset, cy + dy * inset, dx * size,
                        cx + dx * inset, cy + dy * inset, dy * size,
                        t["hairline"], op))

    def spine(self, x, y, h, op=0.95):
        """The accent bar every pane in this set carries on its left edge."""
        self.add('<rect x="%.1f" y="%.1f" width="3" height="%.1f" fill="%s" '
                 'fill-opacity="%.2f"/>' % (x + 1, y + 1, h - 2, self.accent, op))

    def text(self, x, y, s, size=14, family="mono", color=None, weight=400,
             anchor="start", tracking=0, opacity=1.0):
        t = self.t
        col = color or t["ink"]
        fam = MONO if family == "mono" else SANS
        ls = ' letter-spacing="%.2f"' % tracking if tracking else ""
        op = ' opacity="%.2f"' % opacity if opacity < 1 else ""
        self.add('<text x="%.1f" y="%.1f" font-family=\'%s\' font-size="%.1f" '
                 'font-weight="%d" fill="%s" text-anchor="%s"%s%s>%s</text>'
                 % (x, y, fam, size, weight, col, anchor, ls, op, esc(s)))

    def rule(self, x1, y1, x2, y2, color=None, op=None, width=1, dash=None):
        t = self.t
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        self.add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-opacity="%.3f" stroke-width="%.1f"%s/>'
                 % (x1, y1, x2, y2, color or t["hairline"],
                    t["hairline_op"] if op is None else op, width, d))

    def chip(self, x, y, label, accent=False):
        """A mono tag on a hairline box. Returns the width consumed."""
        t = self.t
        pad = 9
        cw = len(label) * 6.3 + pad * 2
        col = self.accent if accent else t["ink_soft"]
        self.add('<rect x="%.1f" y="%.1f" width="%.1f" height="22" rx="2" fill="none" '
                 'stroke="%s" stroke-opacity="%.3f"/>'
                 % (x, y, cw, col, 0.45 if accent else t["hairline_op"] * 1.6))
        self.text(x + pad, y + 15, label, size=9.5, color=col, tracking=0.8)
        return cw + 8

    def arrow(self, x1, y1, x2, y2, op=0.75, dash=None):
        mid = self.uid("ar")
        self.add_def(
            '<marker id="%s" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" '
            'markerHeight="6" orient="auto-start-reverse">'
            '<path d="M 0 0 L 10 5 L 0 10 z" fill="%s" fill-opacity="%.2f"/></marker>'
            % (mid, self.accent, op))
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        self.add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-opacity="%.2f" stroke-width="1.4" marker-end="url(#%s)"%s/>'
                 % (x1, y1, x2, y2, self.accent, op, mid, d))

    def elbow(self, x1, y1, x2, y2, op=0.75):
        """Right-angled connector. Brutalist routing: no curves."""
        mx = (x1 + x2) / 2
        mid = self.uid("ar")
        self.add_def(
            '<marker id="%s" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" '
            'markerHeight="6" orient="auto-start-reverse">'
            '<path d="M 0 0 L 10 5 L 0 10 z" fill="%s" fill-opacity="%.2f"/></marker>'
            % (mid, self.accent, op))
        self.add('<path d="M %.1f %.1f H %.1f V %.1f H %.1f" fill="none" stroke="%s" '
                 'stroke-opacity="%.2f" stroke-width="1.4" marker-end="url(#%s)"/>'
                 % (x1, y1, mx, y2, x2, self.accent, op, mid))

    def render(self):
        return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
                'viewBox="0 0 %d %d" role="img">\n<defs>%s</defs>\n%s\n</svg>\n'
                % (self.w, self.h, self.w, self.h,
                   "".join(self.defs), "\n".join(self.body)))


# --------------------------------------------------------------------------
# signature motifs: a miniature of what the skill actually does
#
# Each one draws inside a band the frame gives it. The frame owns the label and
# the caption, which is what keeps ten different graphics looking like one set.
# --------------------------------------------------------------------------

def _box(c, x, y, w, h, op=0.5):
    c.add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="1" fill="%s" '
          'fill-opacity="%.2f"/>' % (x, y, w, h, c.accent, op))


def _ghost(c, x, y, w, h):
    c.add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="1" fill="none" '
          'stroke="%s" stroke-opacity="0.75" stroke-width="1" stroke-dasharray="2 2"/>'
          % (x, y, w, h, c.accent))


def motif_unicode(c, x, y, w, h):
    base = y + h * 0.62
    widths = [19, 13, 16, 0, 15, 20, 0, 14, 17, 0, 16]
    cx = x + 8
    for i, gw in enumerate(widths):
        if gw:
            _box(c, cx, base - 40, gw, 40, 0.78 if i % 3 else 0.45)
            cx += gw + 6
        else:
            _ghost(c, cx, base - 40, 8, 40)
            c.text(cx + 4, base + 16, "U+", size=7.5, color=c.accent, anchor="middle")
            cx += 14
    c.rule(x + 4, base + 5, x + w - 4, base + 5, op=0.28)


def motif_profit(c, x, y, w, h):
    base = y + h - 20
    labels = ["FR", "IT", "MA", "AE"]
    spend = [62, 46, 40, 68]
    rev = [104, 88, 52, 58]
    step = (w - 16) / len(labels)
    for i, lab in enumerate(labels):
        bx = x + 12 + i * step
        c.add('<rect x="%.1f" y="%.1f" width="17" height="%.1f" fill="%s" '
              'fill-opacity="0.26"/>' % (bx, base - spend[i], spend[i], c.accent))
        c.add('<rect x="%.1f" y="%.1f" width="17" height="%.1f" fill="%s" '
              'fill-opacity="0.85"/>' % (bx + 21, base - rev[i], rev[i], c.accent))
        c.text(bx + 19, base + 15, lab, size=9, color=c.t["ink_faint"],
               anchor="middle", tracking=0.8)
    c.rule(x + 4, base, x + w - 4, base, op=0.35)


def motif_chain(c, x, y, w, h):
    cy = y + h * 0.46
    names = ["AD", "LP", "OFFER", "PB"]
    step = (w - 46) / 3
    pts = []
    for i, n in enumerate(names):
        px = x + 23 + i * step
        pts.append(px)
        alive = i < 2
        c.add('<rect x="%.1f" y="%.1f" width="42" height="42" rx="1" fill="%s" '
              'fill-opacity="%.2f" stroke="%s" stroke-opacity="%.2f"/>'
              % (px - 21, cy - 21, c.accent, 0.55 if alive else 0.10,
                 c.accent, 0.9 if alive else 0.35))
        c.text(px, cy + 4, n, size=9.5, color=c.t["ink"] if alive else c.t["ink_faint"],
               anchor="middle", tracking=0.4)
    for i in range(3):
        broken = i == 1
        c.add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
              'stroke-opacity="%.2f" stroke-width="1.6"%s/>'
              % (pts[i] + 23, cy, pts[i + 1] - 23, cy, c.accent,
                 0.85 if not broken else 0.3,
                 ' stroke-dasharray="3 3"' if broken else ""))
        if broken:
            mx = (pts[i] + pts[i + 1]) / 2
            c.add('<path d="M %.1f %.1f l 11 11 M %.1f %.1f l -11 11" stroke="%s" '
                  'stroke-opacity="1" stroke-width="2"/>'
                  % (mx - 5.5, cy - 5.5, mx + 5.5, cy - 5.5, c.accent))
    c.text(x + w / 2, cy + 44, "clickid", size=9, color=c.t["ink_faint"],
           anchor="middle", tracking=1.2)


def motif_window(c, x, y, w, h):
    import math
    cx, cy, r = x + 62, y + h * 0.5, 56
    c.add('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
          'stroke-opacity="0.25" stroke-width="12"/>' % (cx, cy, r, c.t["hairline"]))
    frac = 0.76
    a = -math.pi / 2 + 2 * math.pi * frac
    large = 1 if frac > 0.5 else 0
    c.add('<path d="M %.2f %.2f A %.1f %.1f 0 %d 1 %.2f %.2f" fill="none" stroke="%s" '
          'stroke-opacity="0.95" stroke-width="12"/>'
          % (cx, cy - r, r, r, large, cx + r * math.cos(a), cy + r * math.sin(a),
             c.accent))
    c.text(cx, cy + 2, "18h", size=25, family="sans", weight=700, color=c.t["ink"],
           anchor="middle")
    c.text(cx, cy + 20, "LEFT", size=8.5, color=c.t["ink_faint"], anchor="middle",
           tracking=1.6)
    tx = x + 148
    c.add('<rect x="%.1f" y="%.1f" width="10" height="10" fill="%s" '
          'fill-opacity="0.95"/>' % (tx, cy - 34, c.accent))
    c.text(tx + 18, cy - 25, "free-form", size=11, color=c.t["ink"], tracking=0.3)
    c.text(tx + 18, cy - 11, "inside the window", size=9, color=c.t["ink_faint"])
    c.rule(tx, cy + 4, x + w - 6, cy + 4, op=0.2)
    c.add('<rect x="%.1f" y="%.1f" width="10" height="10" fill="none" stroke="%s" '
          'stroke-opacity="0.6"/>' % (tx, cy + 18, c.accent))
    c.text(tx + 18, cy + 27, "template only", size=11, color=c.t["ink_soft"],
           tracking=0.3)
    c.text(tx + 18, cy + 41, "after 24 hours", size=9, color=c.t["ink_faint"])


def motif_match(c, x, y, w, h):
    lx, rx = x + 18, x + w - 18
    rows = [(0, 0, True), (1, 1, True), (2, None, False), (3, 2, True), (4, 3, False)]
    top = y + 14
    gap = 30
    for a, b, paid in rows:
        ay = top + a * gap
        _box(c, lx - 14, ay - 8, 16, 16, 0.65)
        if b is None:
            c.add('<circle cx="%.1f" cy="%.1f" r="5" fill="none" stroke="%s" '
                  'stroke-opacity="0.45" stroke-dasharray="2 2"/>' % (rx + 6, ay,
                                                                     c.accent))
            continue
        by = top + b * gap
        op = 0.9 if paid else 0.28
        c.add('<path d="M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f" fill="none" '
              'stroke="%s" stroke-opacity="%.2f" stroke-width="1.5"%s/>'
              % (lx + 4, ay, lx + 70, ay, rx - 70, by, rx - 16, by, c.accent, op,
                 "" if paid else ' stroke-dasharray="3 3"'))
        _box(c, rx - 2, by - 8, 16, 16, 0.85 if paid else 0.14)
    c.text(lx - 14, top - 16, "SENT", size=8.5, color=c.t["ink_faint"], tracking=1.4)
    c.text(rx + 14, top - 16, "PAID", size=8.5, color=c.t["ink_faint"], tracking=1.4,
           anchor="end")


def motif_lineage(c, x, y, w, h):
    left = x + 6
    span = w - 12
    rows = [(0.10, 0.42), (0.36, 0.68), (0.60, 1.00)]
    top = y + 10
    for i, (a, b) in enumerate(rows):
        ry = top + i * 24
        c.add('<rect x="%.1f" y="%.1f" width="%.1f" height="12" rx="1" fill="%s" '
              'fill-opacity="0.3"/>' % (left + span * a, ry, span * (b - a), c.accent))
    merged_y = top + 96
    c.add('<rect x="%.1f" y="%.1f" width="%.1f" height="18" rx="1" fill="%s" '
          'fill-opacity="0.9"/>' % (left + span * 0.10, merged_y, span * 0.90, c.accent))
    for i, (a, _b) in enumerate(rows):
        c.add('<path d="M %.1f %.1f V %.1f" stroke="%s" stroke-opacity="0.35" '
              'stroke-width="1" stroke-dasharray="2 3"/>'
              % (left + span * a, top + 12 + i * 24, merged_y, c.accent))
    c.text(left, top - 14, "3 CREATIVES", size=8.5, color=c.t["ink_faint"], tracking=1.4)
    c.text(left + span, merged_y - 6, "1 LINEAGE, 99 DAYS", size=8.5, color=c.accent,
           tracking=1.2, anchor="end")


def motif_peek(c, x, y, w, h):
    left, right = x + 6, x + w - 34
    base, topy = y + h - 12, y + 16
    alpha_y = base - (base - topy) * 0.22
    c.rule(left, alpha_y, right + 28, alpha_y, op=0.35, dash="4 4")
    c.text(right + 28, alpha_y - 7, "alpha", size=8.5, color=c.t["ink_faint"],
           anchor="end", tracking=0.8)
    fixed = [0.95, 0.7, 0.5, 0.62, 0.34, 0.18, 0.3, 0.12, 0.22, 0.06]
    valid = [0.99, 0.93, 0.86, 0.89, 0.72, 0.64, 0.68, 0.57, 0.62, 0.54]
    step = (right - left) / (len(fixed) - 1)

    def path(vals, op, dash=None):
        pts = " ".join("%.1f,%.1f" % (left + i * step, base - (base - topy) * (1 - v))
                       for i, v in enumerate(vals))
        c.add('<polyline points="%s" fill="none" stroke="%s" stroke-opacity="%.2f" '
              'stroke-width="2"%s/>' % (pts, c.accent, op,
                                        ' stroke-dasharray="4 3"' if dash else ""))
    path(fixed, 0.34, dash=True)
    path(valid, 0.95)
    c.text(left, topy - 4, "always valid", size=9, color=c.accent, tracking=0.4)
    c.text(left, base + 2, "fixed horizon", size=9, color=c.t["ink_faint"], tracking=0.4)


def motif_moderation(c, x, y, w, h):
    left = x + 4
    top = y + 12
    rows = [("hide", 0.9), ("hide", 0.75), ("keep", 0), ("hide", 0.6), ("keep", 0)]
    for i, (verdict, op) in enumerate(rows):
        ry = top + i * 27
        wdt = w - 62 - (i % 3) * 20
        if verdict == "hide":
            c.add('<rect x="%.1f" y="%.1f" width="%.1f" height="16" rx="1" fill="%s" '
                  'fill-opacity="0.16"/>' % (left, ry, wdt, c.accent))
            c.rule(left, ry + 8, left + wdt, ry + 8, color=c.accent, op=op, width=1.8)
        else:
            c.add('<rect x="%.1f" y="%.1f" width="%.1f" height="16" rx="1" fill="none" '
                  'stroke="%s" stroke-opacity="0.65"/>' % (left, ry, wdt, c.accent))
            c.text(left + wdt + 10, ry + 12.5, "KEPT", size=8.5, color=c.accent,
                   tracking=1.2)


def motif_ledger(c, x, y, w, h):
    left = x + 16
    top = y + 8
    vals = ["2 740,55", "2 658,15", "2 538,25", "1 898,25"]
    for i, v in enumerate(vals):
        ry = top + i * 33
        ok = i != 2
        c.add('<rect x="%.1f" y="%.1f" width="%.1f" height="23" rx="1" fill="%s" '
              'fill-opacity="%.2f"/>' % (left, ry, w - 34, c.accent,
                                         0.12 if ok else 0.3))
        c.text(left + 12, ry + 16, v, size=12, color=c.t["ink"], tracking=0.2)
        if i:
            c.add('<path d="M %.1f %.1f V %.1f" stroke="%s" stroke-opacity="%.2f" '
                  'stroke-width="1.3"/>' % (left - 10, ry - 10, ry, c.accent,
                                            0.75 if ok else 1))
            c.text(left - 10, ry - 13, "+" if ok else "x", size=11, color=c.accent,
                   anchor="middle")


def motif_layers(c, x, y, w, h):
    left = x + 6
    top = y + 6
    layers = [("FACE", 0.22), ("BRAIN", 0.6), ("PROFILE", 0.38), ("VAULT", 0.95)]
    for i, (name, op) in enumerate(layers):
        ry = top + i * 34
        sealed = name == "VAULT"
        c.add('<rect x="%.1f" y="%.1f" width="%.1f" height="26" rx="1" fill="%s" '
              'fill-opacity="%.2f" stroke="%s" stroke-opacity="%.2f"/>'
              % (left, ry, w - 12, c.accent, op * 0.32, c.accent, op))
        c.text(left + 14, ry + 17, name, size=10,
               color=c.t["ink"] if op > 0.4 else c.t["ink_soft"], tracking=1.6)
        if sealed:
            bx = left + w - 44
            c.add('<rect x="%.1f" y="%.1f" width="11" height="9" rx="1" fill="%s"/>'
                  % (bx, ry + 12, c.accent))
            c.add('<path d="M %.1f %.1f a 5.5 5.5 0 0 1 11 0" fill="none" stroke="%s" '
                  'stroke-width="1.6"/>' % (bx, ry + 12, c.accent))


MOTIFS = {
    "unicode": motif_unicode, "profit": motif_profit, "chain": motif_chain,
    "window": motif_window, "match": motif_match, "lineage": motif_lineage,
    "peek": motif_peek, "moderation": motif_moderation, "ledger": motif_ledger,
    "layers": motif_layers,
}


MOTIF_DY = {"unicode": 30, "chain": 16, "lineage": 8, "profit": 4, "window": 4}


def motif_frame(c, skill, x, y, w, h):
    """The pane a motif lives in: label at the top, caption at the foot, graphic
    between them. Identical on all ten, which is the point."""
    c.glass(x, y, w, h, r=2)
    c.spine(x, y, h, op=0.55)
    c.add('<rect x="%.1f" y="%.1f" width="7" height="7" fill="%s"/>'
          % (x + 18, y + 20, skill["accent"]))
    c.text(x + 32, y + 27, skill["motif_label"], size=8.5, color=c.t["ink"],
           tracking=1.8)
    c.rule(x + 18, y + 38, x + w - 18, y + 38, op=0.16)
    dy = MOTIF_DY.get(skill["motif"], 0)
    MOTIFS[skill["motif"]](c, x + 24, y + 48 + dy, w - 48, h - 48 - 34 - dy)
    c.rule(x + 18, y + h - 30, x + w - 18, y + h - 30, op=0.16)
    c.text(x + 18, y + h - 13, skill["motif_caption"], size=9.5,
           color=c.t["ink_soft"], tracking=0.3)


# --------------------------------------------------------------------------
# hero
# --------------------------------------------------------------------------

def wrap(text, limit):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        if len(cur) + len(wd) + 1 > limit and cur:
            lines.append(cur)
            cur = wd
        else:
            cur = (cur + " " + wd).strip()
    if cur:
        lines.append(cur)
    return lines


def hero(skill, mode):
    c = Canvas(mode, W, 400, skill["accent"])
    c.ground()
    c.grid(40)
    c.glow(960, 200, 340)
    c.glow(110, 372, 300, opacity=THEME[mode]["glow_op"] * 0.45)

    c.glass(48, 44, 1104, 312, r=2)
    c.spine(48, 44, 312)
    c.marks(48, 44, 1104, 312)

    c.text(92, 106, "AGENT SKILL", size=10, color=c.t["ink_faint"], tracking=2.6)
    c.rule(188, 102, 236, 102, op=0.4)
    c.text(246, 106, skill["index"], size=10, color=skill["accent"], tracking=2.6)

    name = skill["title"]
    size = 46 if len(name) <= 21 else (40 if len(name) <= 27 else 35)
    c.text(90, 170, name, size=size, family="sans", weight=700, color=c.t["ink"],
           tracking=-1.1)
    c.text(92, 198, skill["repo"], size=11.5, color=skill["accent"], tracking=0.6)

    for i, line in enumerate(wrap(skill["promise"], 52)[:3]):
        c.text(92, 236 + i * 21, line, size=12.5, color=c.t["ink_soft"], tracking=0.15)

    cx = 92
    for i, ch in enumerate(skill["chips"]):
        cx += c.chip(cx, 302, ch, accent=(i == 0))

    c.rule(780, 92, 780, 308, op=0.14)
    motif_frame(c, skill, 812, 92, 300, 216)
    return c.render()


# --------------------------------------------------------------------------
# diagram
# --------------------------------------------------------------------------

COLX = [76, 358, 640, 922]
NODEW = 202
NODEH = 72
ROW0 = 152
ROWGAP = 100


def _node_rect(n):
    return COLX[n["col"]], ROW0 + n["row"] * ROWGAP, NODEW, NODEH


def diagram(skill, mode):
    spec = skill["diagram"]
    rows = max(n["row"] for n in spec["nodes"]) + 1
    grid_bottom = ROW0 + (rows - 1) * ROWGAP + NODEH
    note_y = grid_bottom + 48
    note_h = 76
    height = note_y + note_h + 36

    c = Canvas(mode, W, height, skill["accent"])
    c.ground()
    c.grid(40)
    c.glow(170, 100, 340, opacity=THEME[mode]["glow_op"] * 0.6)
    c.glow(1070, height - 120, 340, opacity=THEME[mode]["glow_op"] * 0.45)

    c.text(76, 62, "HOW IT WORKS INSIDE", size=10, color=c.t["ink_faint"], tracking=2.6)
    c.rule(272, 58, 320, 58, op=0.4)
    c.text(330, 62, skill["repo"], size=10, color=skill["accent"], tracking=1.6)
    c.text(74, 102, spec["title"], size=25, family="sans", weight=700,
           color=c.t["ink"], tracking=-0.6)
    c.rule(76, 124, 1124, 124, op=0.14)

    nodes = {n["id"]: n for n in spec["nodes"]}

    for e in spec["edges"]:
        a, b = nodes[e[0]], nodes[e[1]]
        ax, ay, aw, ah = _node_rect(a)
        bx, by, bw, bh = _node_rect(b)
        label = e[2] if len(e) > 2 else None
        if a["col"] == b["col"]:
            x = ax + aw / 2
            if b["row"] > a["row"]:
                c.arrow(x, ay + ah + 2, x, by - 8)
                ly = (ay + ah + by) / 2
            else:
                c.arrow(x, ay - 2, x, by + bh + 8)
                ly = (ay + by + bh) / 2
            if label:
                c.text(x + 10, ly + 3, label, size=9, color=c.t["ink_faint"])
        elif a["row"] == b["row"]:
            c.arrow(ax + aw + 2, ay + ah / 2, bx - 8, by + bh / 2)
            if label:
                c.text((ax + aw + bx) / 2, ay + ah / 2 - 10, label, size=9,
                       color=c.t["ink_faint"], anchor="middle")
        else:
            c.elbow(ax + aw + 2, ay + ah / 2, bx - 8, by + bh / 2)
            if label:
                c.text((ax + aw + bx) / 2 + 8, by + bh / 2 - 10, label, size=9,
                       color=c.t["ink_faint"], anchor="middle")

    for n in spec["nodes"]:
        x, y, w, h = _node_rect(n)
        kind = n.get("kind", "step")
        c.glass(x, y, w, h, r=2, stroke_op=0.0 if kind == "gate" else None)
        if kind == "gate":
            c.add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="none" '
                  'stroke="%s" stroke-opacity="0.8" stroke-width="1.4"/>'
                  % (x + .5, y + .5, w - 1, h - 1, skill["accent"]))
            c.spine(x, y, h)
        elif kind == "out":
            c.spine(x, y, h)
        elif kind == "in":
            c.spine(x, y, h, op=0.45)
        c.text(x + 18, y + 28, n["label"], size=11.5, color=c.t["ink"], tracking=0.5)
        if n.get("sub"):
            for i, line in enumerate(wrap(n["sub"], 28)[:2]):
                c.text(x + 18, y + 47 + i * 14, line, size=9.5, color=c.t["ink_faint"])

    c.glass(76, note_y, 1048, note_h, r=2)
    c.spine(76, note_y, note_h)
    c.marks(76, note_y, 1048, note_h, size=9, inset=7)
    c.text(104, note_y + 26, "THE RULE", size=9, color=skill["accent"], tracking=2.0)
    for i, line in enumerate(wrap(spec["note"], 96)[:2]):
        c.text(104, note_y + 47 + i * 18, line, size=12.5, color=c.t["ink_soft"],
               tracking=0.15)
    return c.render()


# --------------------------------------------------------------------------
# marketplace grid
# --------------------------------------------------------------------------

def family(skills, mode):
    c = Canvas(mode, W, 640, "#8B5CF6")
    c.ground()
    c.grid(40)
    c.glow(600, 300, 620, opacity=THEME[mode]["glow_op"] * 0.30, color="#8B5CF6")
    c.text(76, 62, "HIBERIUS SKILLS", size=10, color=c.t["ink_faint"], tracking=2.6)
    c.rule(238, 58, 286, 58, op=0.35)
    c.text(296, 62, "10 AGENT SKILLS", size=10, color="#8B5CF6", tracking=1.6)
    c.text(74, 106, "One hand, ten subjects", size=30, family="sans", weight=700,
           color=c.t["ink"], tracking=-0.8)
    c.text(76, 134, "Zero dependencies  ·  offline  ·  tested in CI on 3.8 and 3.12  ·  MIT",
           size=12, color=c.t["ink_soft"], tracking=0.2)
    cols, cw, ch = 5, 202, 150
    for i, s in enumerate(skills):
        col, row = i % cols, i // cols
        x = 76 + col * (cw + 12)
        y = 176 + row * (ch + 14)
        c.accent = s["accent"]
        c.glass(x, y, cw, ch, r=2)
        c.add('<rect x="%.1f" y="%.1f" width="%.1f" height="3" fill="%s" '
              'fill-opacity="0.95"/>' % (x + 1, y + 1, cw - 2, s["accent"]))
        c.text(x + 14, y + 34, s["index"], size=10, color=s["accent"], tracking=1.8)
        for j, line in enumerate(wrap(s["title"], 15)[:3]):
            c.text(x + 14, y + 58 + j * 17, line, size=13, family="sans", weight=600,
                   color=c.t["ink"], tracking=-0.2)
        c.text(x + 14, y + ch - 16, s["tag"], size=9, color=c.t["ink_faint"],
               tracking=0.6)
    c.accent = "#8B5CF6"
    c.glass(76, 508, 1048, 56, r=2)
    c.add('<rect x="77" y="509" width="3" height="54" fill="#8B5CF6" fill-opacity="0.95"/>')
    c.text(102, 531, "INSTALL", size=9, color="#8B5CF6", tracking=2.0)
    c.text(102, 550, "/plugin marketplace add Hiberius/hiberius-skills", size=12.5,
           color=c.t["ink_soft"], tracking=0.2)
    return c.render()


# --------------------------------------------------------------------------
# the ten
# --------------------------------------------------------------------------

def chips(n_tests):
    return ["%d TESTS" % n_tests, "ZERO DEPS", "PYTHON 3.8+", "OFFLINE", "MIT"]


SKILLS = [
    {
        "index": "01", "repo": "invisible-text-forensics", "accent": "#8B5CF6",
        "title": "Invisible Text Forensics", "tag": "SECURITY · TEXT", "motif": "unicode",
        "motif_label": "SCAN", "motif_caption": "3 hidden characters between 8 visible ones",
        "promise": "Every humanizer rewrites style. None of them read the bytes. "
                   "This finds and removes what renders as nothing.",
        "chips": chips(31),
        "diagram": {
            "title": "One pass over the code points, with the neighbours in hand",
            "nodes": [
                {"id": "in", "col": 0, "row": 1, "kind": "in", "label": "TEXT",
                 "sub": "document, prompt, CV, source file"},
                {"id": "cls", "col": 1, "row": 1, "kind": "gate", "label": "classify(cp)",
                 "sub": "with prev and next code point"},
                {"id": "crit", "col": 2, "row": 0, "label": "critical / high",
                 "sub": "tag chars, bidi, PUA, zero-width, VS"},
                {"id": "keep", "col": 2, "row": 1, "kind": "gate", "label": "legitimate joiner",
                 "sub": "ZWJ in emoji, ZWNJ in Arabic"},
                {"id": "load", "col": 2, "row": 2, "label": "carrier run",
                 "sub": "tag ASCII, VS bytes, ZW binary"},
                {"id": "clean", "col": 3, "row": 0, "kind": "out", "label": "removed",
                 "sub": "three levels, with a diff"},
                {"id": "intact", "col": 3, "row": 1, "kind": "out", "label": "untouched",
                 "sub": "the word still means what it meant"},
                {"id": "pay", "col": 3, "row": 2, "kind": "out", "label": "payload decoded",
                 "sub": "read it before you clean it"},
            ],
            "edges": [["in", "cls"], ["cls", "crit"], ["cls", "keep"], ["cls", "load"],
                      ["crit", "clean"], ["keep", "intact"], ["load", "pay"]],
            "note": "The neighbour check is the whole difference: a blanket strip corrupts "
                    "family emoji and changes the spelling of Arabic and Hindi words.",
        },
    },
    {
        "index": "02", "repo": "cpa-profit-ops", "accent": "#10B981",
        "title": "CPA Profit Ops", "tag": "MEDIA BUYING", "motif": "profit",
        "motif_label": "PROFIT BY COUNTRY", "motif_caption": "spend against revenue, one currency",
        "promise": "Platforms know what you spent. They do not know what a lead is "
                   "worth, so they cannot tell you if you made money.",
        "chips": chips(31),
        "diagram": {
            "title": "profit = leads x payout(country) - spend, inside one currency",
            "nodes": [
                {"id": "spend", "col": 0, "row": 0, "kind": "in", "label": "SPEND",
                 "sub": "in the ad account currency"},
                {"id": "leads", "col": 0, "row": 1, "kind": "in", "label": "LEADS BY COUNTRY",
                 "sub": "delivered, from the platform"},
                {"id": "pay", "col": 0, "row": 2, "kind": "in", "label": "PAYOUTS",
                 "sub": "in the network currency"},
                {"id": "fx", "col": 1, "row": 1, "kind": "gate", "label": "convert the PAYOUT",
                 "sub": "never the spend, which is a fact"},
                {"id": "calc", "col": 2, "row": 1, "label": "profit and ROI",
                 "sub": "currency is part of the group key"},
                {"id": "rank", "col": 3, "row": 0, "kind": "out", "label": "RANK",
                 "sub": "country, campaign, account, operator"},
                {"id": "health", "col": 3, "row": 1, "kind": "out", "label": "TRIAGE",
                 "sub": "per country, never blended"},
                {"id": "be", "col": 3, "row": 2, "kind": "out", "label": "TARGET CPL",
                 "sub": "payout x accepted rate x margin"},
            ],
            "edges": [["spend", "fx"], ["leads", "fx"], ["pay", "fx"], ["fx", "calc"],
                      ["calc", "rank"], ["calc", "health"], ["calc", "be"]],
            "note": "A missing payout and a missing FX rate are different failures. "
                    "Reporting both as zero turns a configuration gap into a fake loss.",
        },
    },
    {
        "index": "03", "repo": "affiliate-tracker-ops", "accent": "#06B6D4",
        "title": "Affiliate Tracker Ops", "tag": "TRACKING", "motif": "chain",
        "motif_label": "THE CHAIN", "motif_caption": "the click id dies between LP and OFFER",
        "promise": "A conversion that does not attribute is a broken parameter chain, "
                   "not a tracker bug. Find the hop where it dies.",
        "chips": chips(26),
        "diagram": {
            "title": "Follow the click id by value, because the key gets renamed",
            "nodes": [
                {"id": "ad", "col": 0, "row": 1, "kind": "in", "label": "AD URL",
                 "sub": "macro replaced by the platform"},
                {"id": "trk", "col": 1, "row": 1, "label": "TRACKING DOMAIN",
                 "sub": "redirect, DNS, certificate"},
                {"id": "lp", "col": 2, "row": 1, "label": "LANDER",
                 "sub": "must forward the parameter"},
                {"id": "off", "col": 3, "row": 1, "label": "OFFER",
                 "sub": "expects its own parameter name"},
                {"id": "net", "col": 3, "row": 2, "label": "NETWORK",
                 "sub": "judges the lead hours later"},
                {"id": "pb", "col": 1, "row": 2, "kind": "gate", "label": "POSTBACK",
                 "sub": "click id token, payout token"},
                {"id": "stat", "col": 0, "row": 2, "kind": "out", "label": "ATTRIBUTED",
                 "sub": "the visit that earned the money"},
                {"id": "capi", "col": 0, "row": 0, "kind": "out", "label": "BACK TO PLATFORM",
                 "sub": "fbclid, ttclid, gclid, event id"},
            ],
            "edges": [["ad", "trk"], ["trk", "lp"], ["lp", "off"], ["off", "net"],
                      ["net", "pb"], ["pb", "stat"], ["stat", "capi"]],
            "note": "The click id is renamed from clickid to sub1 to aff_sub along the "
                    "way, so the chain is followed by its value and never by its key.",
        },
    },
    {
        "index": "04", "repo": "whatsapp-receptionist-builder", "accent": "#22C55E",
        "title": "WhatsApp Receptionist Builder", "tag": "BUILD", "motif": "window",
        "motif_label": "SERVICE WINDOW", "motif_caption": "the clock starts at their last message",
        "promise": "The webhook acknowledges, the worker thinks. Everything else in "
                   "a WhatsApp receptionist follows from that one decision.",
        "chips": chips(32),
        "diagram": {
            "title": "Accept in under a second, decide afterwards",
            "nodes": [
                {"id": "meta", "col": 0, "row": 1, "kind": "in", "label": "META WEBHOOK",
                 "sub": "text, voice note, delivery status"},
                {"id": "sig", "col": 1, "row": 0, "kind": "gate", "label": "VERIFY SIGNATURE",
                 "sub": "HMAC over the RAW body, then parse"},
                {"id": "idem", "col": 1, "row": 1, "kind": "gate", "label": "SEEN THIS wamid?",
                 "sub": "unique index, replay is a no-op"},
                {"id": "q", "col": 1, "row": 2, "label": "ENQUEUE, RETURN 200",
                 "sub": "same transaction as the insert"},
                {"id": "work", "col": 2, "row": 1, "label": "WORKER",
                 "sub": "intent, availability, booking"},
                {"id": "db", "col": 2, "row": 2, "kind": "gate", "label": "EXCLUDE OVERLAP",
                 "sub": "the database refuses the double book"},
                {"id": "out", "col": 3, "row": 1, "kind": "out", "label": "OUTBOX",
                 "sub": "SKIP LOCKED, backoff, dead letter"},
                {"id": "esc", "col": 3, "row": 0, "kind": "out", "label": "HUMAN HANDOFF",
                 "sub": "state, notify, tell the customer"},
            ],
            "edges": [["meta", "sig"], ["sig", "idem"], ["idem", "q"], ["q", "work"],
                      ["work", "db"], ["work", "out"], ["work", "esc"]],
            "note": "Free-form messages die 24 hours after the customer's last inbound. "
                    "Your replies do not extend it, so every reminder is a template.",
        },
    },
    {
        "index": "05", "repo": "lead-delivery-reconciliation", "accent": "#3B82F6",
        "title": "Lead Delivery Reconciliation", "tag": "LEAD GEN", "motif": "match",
        "motif_label": "RECONCILIATION", "motif_caption": "3 of 5 paid, effective payout 10.20",
        "promise": "Received is a format check, not money. Only the buyer's register "
                   "says what the day was actually worth.",
        "chips": chips(49),
        "diagram": {
            "title": "Deliver on your own id, then go and ask what happened to it",
            "nodes": [
                {"id": "lead", "col": 0, "row": 1, "kind": "in", "label": "META LEAD AD",
                 "sub": "raw fields, as typed"},
                {"id": "norm", "col": 1, "row": 1, "kind": "gate", "label": "NORMALISE",
                 "sub": "email, phone, zip stays a STRING"},
                {"id": "dedup", "col": 2, "row": 1, "label": "DEDUPE AND CAP",
                 "sub": "email and phone, cap on SENT date"},
                {"id": "send", "col": 3, "row": 1, "label": "DELIVER",
                 "sub": "your delivery_id is the reference"},
                {"id": "rej", "col": 1, "row": 2, "kind": "out", "label": "RESALE QUEUE",
                 "sub": "rejects with the reason attached"},
                {"id": "reg", "col": 3, "row": 2, "label": "BUYER REGISTER",
                 "sub": "sold, unsold, pending, payout"},
                {"id": "rec", "col": 2, "row": 2, "kind": "gate", "label": "RECONCILE",
                 "sub": "your id first, theirs as fallback"},
                {"id": "out", "col": 0, "row": 2, "kind": "out", "label": "EFFECTIVE PAYOUT",
                 "sub": "revenue over delivered leads"},
            ],
            "edges": [["lead", "norm"], ["norm", "dedup"], ["dedup", "send"],
                      ["norm", "rej"], ["send", "reg"], ["reg", "rec"], ["rec", "out"]],
            "note": "A lead you rejected locally can still have been accepted and paid. "
                    "Left unrealigned, that payout sits on a rejected row for a month.",
        },
    },
    {
        "index": "06", "repo": "competitor-ad-intelligence", "accent": "#F59E0B",
        "title": "Competitor Ad Intelligence", "tag": "COMPETITIVE", "motif": "lineage",
        "motif_label": "LINEAGE", "motif_caption": "three re-uploads, one concept, 99 days",
        "promise": "Nobody publishes competitor spend. Score the signals a losing ad "
                   "cannot fake for long, and group the re-uploads first.",
        "chips": chips(35),
        "diagram": {
            "title": "Group first, score second. In that order the ranking inverts",
            "nodes": [
                {"id": "lib", "col": 0, "row": 1, "kind": "in", "label": "AD LIBRARIES",
                 "sub": "Meta, Google, TikTok, LinkedIn"},
                {"id": "arch", "col": 0, "row": 2, "label": "YOUR ARCHIVE",
                 "sub": "ended, not deleted; file, not URL"},
                {"id": "lin", "col": 1, "row": 1, "kind": "gate", "label": "LINEAGE",
                 "sub": "same advertiser, same concept"},
                {"id": "score", "col": 2, "row": 1, "label": "WINNER SCORE",
                 "sub": "35 25 20 10 10, each saturating"},
                {"id": "stage", "col": 3, "row": 0, "kind": "out", "label": "STAGE",
                 "sub": "battle-tested, traction, new test"},
                {"id": "short", "col": 3, "row": 1, "kind": "out", "label": "SHORTLIST",
                 "sub": "what deserves ten minutes"},
                {"id": "gap", "col": 3, "row": 2, "kind": "out", "label": "ANGLE GAPS",
                 "sub": "working for them, absent for you"},
            ],
            "edges": [["lib", "lin"], ["arch", "lin"], ["lin", "score"],
                      ["score", "stage"], ["score", "short"], ["score", "gap"]],
            "note": "An advertiser who re-uploads every fortnight looks like three short "
                    "tests and is one concept that has been running for six weeks.",
        },
    },
    {
        "index": "07", "repo": "incrementality-testing", "accent": "#6366F1",
        "title": "Incrementality Testing", "tag": "EXPERIMENTS", "motif": "peek",
        "motif_label": "TWENTY PEEKS", "motif_caption": "under a true null, only one holds",
        "promise": "Platform ROAS credits conversions that would have happened anyway. "
                   "This answers the causal question, and survives being watched.",
        "chips": chips(49),
        "diagram": {
            "title": "Check the split, then read the p-value you are allowed to read",
            "nodes": [
                {"id": "arms", "col": 0, "row": 1, "kind": "in", "label": "TWO ARMS",
                 "sub": "user, geo, holdout or ghost ad"},
                {"id": "srm", "col": 1, "row": 1, "kind": "gate", "label": "SRM CHECK",
                 "sub": "chi square at alpha 0.001"},
                {"id": "stop", "col": 1, "row": 0, "kind": "out", "label": "STOP",
                 "sub": "a broken split reads as nothing"},
                {"id": "rule", "col": 2, "row": 1, "kind": "gate", "label": "STOP RULE?",
                 "sub": "fixed N, or watching daily"},
                {"id": "fix", "col": 3, "row": 0, "kind": "out", "label": "FIXED HORIZON",
                 "sub": "valid once, at that N only"},
                {"id": "msp", "col": 3, "row": 1, "kind": "out", "label": "ALWAYS VALID",
                 "sub": "mSPRT, peek as often as you like"},
                {"id": "cup", "col": 2, "row": 2, "label": "CUPED",
                 "sub": "pre-period covariate, unbiased"},
                {"id": "dec", "col": 3, "row": 2, "kind": "out", "label": "DECISION",
                 "sub": "the interval decides, not the point"},
            ],
            "edges": [["arms", "srm"], ["srm", "stop", "mismatch"], ["srm", "rule"],
                      ["rule", "fix"], ["rule", "msp"], ["cup", "dec"],
                      ["msp", "dec"]],
            "note": "Checking a fixed-horizon p-value daily and stopping when it dips "
                    "under 0.05 puts the real false positive rate near 30%.",
        },
    },
    {
        "index": "08", "repo": "ad-comment-moderation", "accent": "#F43F5E",
        "title": "Ad Comment Moderation", "tag": "SOCIAL OPS", "motif": "moderation",
        "motif_label": "VERDICTS", "motif_caption": "spam hidden, criticism left visible",
        "promise": "Most scripts hide everything new. This one states a reason for "
                   "every verdict, and leaves honest criticism visible.",
        "chips": chips(40),
        "diagram": {
            "title": "The comments are on the post behind the ad, not on the ad",
            "nodes": [
                {"id": "ad", "col": 0, "row": 1, "kind": "in", "label": "THE AD",
                 "sub": "often a dark post you cannot find"},
                {"id": "res", "col": 1, "row": 1, "kind": "gate", "label": "RESOLVE",
                 "sub": "effective_object_story_id"},
                {"id": "post", "col": 2, "row": 1, "label": "PAGE POST",
                 "sub": "one post can back many ads"},
                {"id": "cm", "col": 3, "row": 1, "label": "COMMENTS",
                 "sub": "stream filter, replies included"},
                {"id": "allow", "col": 3, "row": 0, "kind": "gate", "label": "ALLOW RULES",
                 "sub": "evaluated first, always"},
                {"id": "rules", "col": 2, "row": 2, "label": "SEVEN KINDS",
                 "sub": "priority order, first match wins"},
                {"id": "hide", "col": 1, "row": 2, "kind": "out", "label": "HIDE",
                 "sub": "is_hidden, reversible, quiet"},
                {"id": "keep", "col": 0, "row": 2, "kind": "out", "label": "KEEP",
                 "sub": "no rule matched, so it stays"},
            ],
            "edges": [["ad", "res"], ["res", "post"], ["post", "cm"], ["cm", "allow"],
                      ["cm", "rules"], ["rules", "hide"], ["rules", "keep"]],
            "note": "An allow list that can be outranked by a higher-priority hide rule "
                    "is not an allow list, which is why allow runs first.",
        },
    },
    {
        "index": "09", "repo": "bank-statement-to-table", "accent": "#84CC16",
        "title": "Bank Statement to Table", "tag": "DOCUMENTS", "motif": "ledger",
        "motif_label": "BALANCE CHAIN", "motif_caption": "row three does not follow from row two",
        "promise": "Extraction is guessing. A statement carries its own proof, so a "
                   "parse is either verified against the balance chain or wrong.",
        "chips": chips(50),
        "diagram": {
            "title": "Two decisions per document, then a proof per row",
            "nodes": [
                {"id": "pdf", "col": 0, "row": 1, "kind": "in", "label": "STATEMENT PDF",
                 "sub": "text layer, or a scan"},
                {"id": "det", "col": 1, "row": 0, "kind": "gate", "label": "DETECT",
                 "sub": "date order and decimal, once"},
                {"id": "txt", "col": 1, "row": 1, "label": "LAYOUT TEXT",
                 "sub": "pdftotext -layout, or OCR"},
                {"id": "cls", "col": 2, "row": 1, "kind": "gate", "label": "CLASSIFY LINES",
                 "sub": "date and amount starts a row"},
                {"id": "rows", "col": 3, "row": 1, "label": "TRANSACTIONS",
                 "sub": "descriptions merged, noise dropped"},
                {"id": "ver", "col": 3, "row": 2, "kind": "gate", "label": "VERIFY",
                 "sub": "chain per row, totals per file"},
                {"id": "ok", "col": 2, "row": 2, "kind": "out", "label": "VERIFIED",
                 "sub": "reproduces the statement exactly"},
                {"id": "bad", "col": 1, "row": 2, "kind": "out", "label": "OR THE ROW",
                 "sub": "named, with the difference explained"},
            ],
            "edges": [["pdf", "det"], ["det", "txt"], ["txt", "cls"], ["cls", "rows"],
                      ["rows", "ver"], ["ver", "ok"], ["ver", "bad"]],
            "note": "balance[i] equals balance[i-1] plus amount[i]. If the chain holds "
                    "from opening to closing, the parse is right. If not, it names the row.",
        },
    },
    {
        "index": "10", "repo": "always-on-agent", "accent": "#D946EF",
        "title": "Always-On Agent", "tag": "AGENTS", "motif": "layers",
        "motif_label": "FOUR LAYERS", "motif_caption": "key names reach the model, values never",
        "promise": "Four systems, not one. And a first pass that is incapable of harm, "
                   "not merely careful about it.",
        "chips": chips(27),
        "diagram": {
            "title": "A gateway that never sleeps, a machine that does",
            "nodes": [
                {"id": "ev", "col": 0, "row": 1, "kind": "in", "label": "EVENT",
                 "sub": "message, webhook, schedule"},
                {"id": "gw", "col": 1, "row": 1, "kind": "gate", "label": "GATEWAY",
                 "sub": "queue and sign, holds no secret"},
                {"id": "wake", "col": 2, "row": 1, "label": "WAKE THE MAC",
                 "sub": "signed POST, verified on arrival"},
                {"id": "loop", "col": 3, "row": 1, "label": "AGENT LOOP",
                 "sub": "launchd and tmux, event driven"},
                {"id": "gate", "col": 3, "row": 0, "kind": "gate", "label": "APPROVAL TIER",
                 "sub": "free, ask, never; by action"},
                {"id": "vault", "col": 3, "row": 2, "kind": "gate", "label": "VAULT",
                 "sub": "key names reach the model, values never"},
                {"id": "face", "col": 2, "row": 0, "kind": "out", "label": "FACE",
                 "sub": "reads state, cannot call the model"},
                {"id": "survey", "col": 2, "row": 2, "kind": "out", "label": "FIRST PASS",
                 "sub": "read only, before anything writes"},
            ],
            "edges": [["ev", "gw"], ["gw", "wake"], ["wake", "loop"], ["loop", "gate"],
                      ["loop", "vault"], ["gate", "face"], ["vault", "survey"]],
            "note": "Sign the wake request and verify it, or you have published an "
                    "endpoint anyone can use to make your laptop run an agent.",
        },
    },
]


def main():
    check = "--check" in sys.argv
    here = os.path.dirname(os.path.abspath(__file__))
    repos = os.path.abspath(os.path.join(here, "..", ".."))
    written = 0
    for s in SKILLS:
        out = ("/tmp/brand-check/%s" % s["repo"]) if check \
            else os.path.join(repos, s["repo"], "assets")
        os.makedirs(out, exist_ok=True)
        for mode in ("dark", "light"):
            for name, svg in (("hero", hero(s, mode)), ("diagram", diagram(s, mode))):
                path = os.path.join(out, "%s-%s.svg" % (name, mode))
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(svg)
                ET.fromstring(svg)          # fails loudly on malformed XML
                written += 1
    fam_out = "/tmp/brand-check/family" if check else os.path.join(here, "..", "assets")
    os.makedirs(fam_out, exist_ok=True)
    for mode in ("dark", "light"):
        svg = family(SKILLS, mode)
        ET.fromstring(svg)
        with open(os.path.join(fam_out, "family-%s.svg" % mode), "w",
                  encoding="utf-8") as fh:
            fh.write(svg)
        written += 1
    print("%d SVG scritti%s" % (written, " in /tmp/brand-check" if check else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
