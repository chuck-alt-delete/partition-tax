#!/usr/bin/env python3
"""Catch layout faults in the deck's hand-authored SVG diagrams.

Monospace text width is estimated at 0.605em/char, which is close enough for
the ui-monospace stack the diagrams use. Checks three things:

  0. XML well-formedness (an invalid comment or unescaped & renders in browsers
     but is still malformed)
  1. text running outside the viewBox
  2. two texts overlapping on a shared baseline
  3. text straddling a <rect> border — the one that produced the mangled
     broker-math top row, where the operators sat on top of the boxes and the
     captions were wider than the boxes containing them

Usage: python3 tools/check_svg.py [file.svg ...]   (defaults to all diagrams)
"""
import re, sys, glob
from collections import defaultdict

CH = 0.605


def texts_and_rects(src):
    """Walk tags in order so each <text> inherits from its ENCLOSING <g> only.

    An earlier version took the first <g> in the file and applied its
    text-anchor to every text element, which reported nonsense for anything
    outside that group. Scope matters here.
    """
    texts, rects, stack = [], [], []
    tag = re.compile(r'<(/?)(g|text|rect)\b([^>]*?)(/?)>')
    pos = 0
    while True:
        m = tag.search(src, pos)
        if not m:
            break
        closing, name, at, selfclose = m.group(1), m.group(2), m.group(3), m.group(4)
        pos = m.end()
        if name == 'g':
            if closing:
                if stack:
                    stack.pop()
            elif not selfclose:
                f = re.search(r'font-size="([^"]+)"', at)
                a = re.search(r'text-anchor="([^"]+)"', at)
                stack.append((float(f.group(1)) if f else None, a.group(1) if a else None))
            continue
        if closing:
            continue
        g = lambda n, d=None: (re.search(n + r'="([^"]+)"', at).group(1)
                               if re.search(n + r'="([^"]+)"', at) else d)
        if name == 'rect':
            if all(g(k) for k in ('x', 'y', 'width', 'height')):
                rects.append({'x': float(g('x')), 'y': float(g('y')),
                              'w': float(g('width')), 'h': float(g('height'))})
            continue
        # <text>: content runs to the matching close tag
        end = src.find('</text>', pos)
        txt = src[pos:end] if end != -1 else ''
        if not txt.strip() or '<' in txt:
            continue
        inh_fs = next((fs for fs, _ in reversed(stack) if fs), None)
        inh_an = next((an for _, an in reversed(stack) if an), None)
        texts.append({'x': float(g('x', 0)), 'y': float(g('y', 0)),
                      'fs': float(g('font-size') or 0) or inh_fs or 16,
                      'anchor': g('text-anchor') or inh_an or 'start',
                      'txt': txt})
    return texts, rects


def resolve(texts, src):
    for t in texts:
        w = len(t['txt']) * t['fs'] * CH
        t['w'] = w
        t['x0'] = t['x'] if t['anchor'] == 'start' else (
            t['x'] - w / 2 if t['anchor'] == 'middle' else t['x'] - w)
        t['x1'] = t['x0'] + w
        t['y0'] = t['y'] - t['fs'] * 0.78
        t['y1'] = t['y'] + t['fs'] * 0.22
    return texts


def check(path):
    src = open(path).read()
    problems_xml = []
    try:
        import xml.etree.ElementTree as ET
        ET.fromstring(src)
    except Exception as e:
        problems_xml.append(f"malformed XML: {e}")
    vb = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', src)
    W, H = float(vb.group(1)), float(vb.group(2))
    texts, rects = texts_and_rects(src)
    texts = resolve(texts, src)
    problems = list(problems_xml)

    for t in texts:
        if t['x0'] < -2 or t['x1'] > W + 2:
            problems.append(f"viewBox overflow  [{t['x0']:.0f}..{t['x1']:.0f}] vs 0..{W:.0f}  {t['txt'][:44]!r}")
        if t['y'] > H + 2:
            problems.append(f"below viewBox     y={t['y']:.0f} > {H:.0f}  {t['txt'][:44]!r}")

    rows = defaultdict(list)
    for t in texts:
        rows[round(t['y'] / 10)].append(t)
    for _, items in rows.items():
        items.sort(key=lambda t: t['x0'])
        for a, b in zip(items, items[1:]):
            if a['x1'] > b['x0'] + 1:
                problems.append(f"text/text overlap {a['txt'][:26]!r} ends {a['x1']:.0f} vs {b['txt'][:26]!r} starts {b['x0']:.0f}")

    for t in texts:
        for r in rects:
            vert = t['y1'] > r['y'] and t['y0'] < r['y'] + r['h']
            if not vert:
                continue
            inside = t['x0'] >= r['x'] - 1 and t['x1'] <= r['x'] + r['w'] + 1
            outside = t['x1'] <= r['x'] + 1 or t['x0'] >= r['x'] + r['w'] - 1
            if not (inside or outside):
                problems.append(
                    f"text straddles box [{t['x0']:.0f}..{t['x1']:.0f}] vs box "
                    f"[{r['x']:.0f}..{r['x']+r['w']:.0f}]  {t['txt'][:36]!r}")
    return problems


def main():
    files = sys.argv[1:] or sorted(glob.glob('assets/diagrams/*.svg'))
    total = 0
    for f in files:
        probs = check(f)
        total += len(probs)
        print(f"{f}  {'OK' if not probs else str(len(probs)) + ' PROBLEM(S)'}")
        for p in probs:
            print(f"    {p}")
    sys.exit(1 if total else 0)


if __name__ == '__main__':
    main()
