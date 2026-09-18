#!/usr/bin/env python3
"""One-shot migration: split index.html's slides into per-act Markdown files.

Headings and paragraphs become real Markdown; anything carrying a class keeps
it via a `<!-- .element: -->` comment. Component markup (panels, tables, SVG,
code) stays as raw HTML blocks, because Markdown has no better way to say it.
Speaker notes become `Note:` blocks, which is the bulk of the readability win.

Run once from the repo root. Verified against the rendered DOM afterwards.
"""
import re, os, sys

ACTS = [
    ("01-title",    "Title"),
    ("02-poll",     "Audience poll"),
    ("03-playbook", "The playbook"),
    ("04-tax",      "The Tax"),
    ("05-prevent",  "Prevent"),
    ("06-clean",    "Clean"),
    ("07-fix",      "Fix the root cause"),
    ("08-patch",    "Patch"),
    ("09-close",    "Close"),
]

RAW_TAGS = {'div','ul','ol','pre','figure','svg','table','blockquote','span','img','p'}


def top_level_elements(html):
    """Yield (tag, attrs, outer, inner) for each depth-0 element."""
    i, out = 0, []
    while i < len(html):
        m = re.compile(r'<([a-zA-Z][\w-]*)([^>]*?)(/?)>').search(html, i)
        if not m:
            break
        tag, attrs, selfclose = m.group(1), m.group(2).strip(), m.group(3)
        if selfclose or tag in ('img', 'br', 'hr'):
            out.append((tag, attrs, html[m.start():m.end()], ''))
            i = m.end(); continue
        # walk to the matching close tag
        depth, j = 1, m.end()
        pat = re.compile(r'</?%s\b[^>]*?(/?)>' % re.escape(tag))
        while depth and j < len(html):
            mm = pat.search(html, j)
            if not mm: break
            if mm.group(0).startswith('</'): depth -= 1
            elif not mm.group(1):            depth += 1
            j = mm.end()
        out.append((tag, attrs, html[m.start():j], html[m.end():j - len(f'</{tag}>')]))
        i = j
    return out


def dedent_block(block, keep_blanks=False):
    lines = block.split('\n') if keep_blanks else [l for l in block.split('\n') if l.strip()]
    body = [l for l in lines if l.strip()]
    if not body: return ''
    pad = min(len(l) - len(l.lstrip()) for l in body)
    out = ['' if not l.strip() else (l[pad:] if len(l) - len(l.lstrip()) >= pad else l.lstrip())
           for l in lines]
    return '\n'.join(out).strip('\n')


def spine_to_data_act(outer):
    layers = re.findall(r'<div class="layer([^"]*)"', outer)
    states = [c.strip() for c in layers]
    on = [i + 1 for i, s in enumerate(states) if 'on' in s.split()]
    if len(on) == 4:                     return 'all'
    if not on and all('done' in s for s in states): return 'done'
    return str(on[0]) if on else 'all'


def attrs_of(attrs):
    d = dict(re.findall(r'([\w-]+)="([^"]*)"', attrs))
    return d


def convert_slide(sec_attrs, inner):
    parts, notes = [], None
    a = attrs_of(sec_attrs)
    slide_attrs = ' '.join(f'{k}="{v}"' for k, v in a.items() if k in ('class', 'data-state'))
    if slide_attrs:
        parts.append(f'<!-- .slide: {slide_attrs} -->')

    for tag, at, outer, ins in top_level_elements(inner):
        cls = attrs_of(at).get('class', '')
        if tag == 'aside' and 'notes' in cls:
            notes = dedent_block(ins, keep_blanks=True).strip()
            continue
        if tag == 'div' and cls.strip().startswith('spine'):
            parts.append(f'<div class="spine" data-act="{spine_to_data_act(outer)}"></div>')
            continue
        if tag == 'span' and 'kicker' in cls:
            parts.append(f'<p class="{cls}">{ins.strip()}</p>')
            continue
        if tag in ('h1', 'h2', 'h3') and ins.strip():
            hashes = '#' * int(tag[1])
            text = ' '.join(ins.split())
            block = f'{hashes} {text}'
            other = attrs_of(at)
            if other:
                # NO blank line: Reveal applies .element to the element directly
                # above it, and a blank line makes the renderer emit a stray
                # empty <p> that carries paragraph margins.
                block += '\n<!-- .element: ' + ' '.join(f'{k}="{v}"' for k, v in other.items()) + ' -->'
            parts.append(block)
            continue
        if tag == 'p' and 'style' not in at:
            block = ' '.join(ins.split())
            other = attrs_of(at)
            if other:
                block += '\n<!-- .element: ' + ' '.join(f'{k}="{v}"' for k, v in other.items()) + ' -->'
            parts.append(block)
            continue
        parts.append(dedent_block(outer))

    md = '\n\n'.join(p for p in parts if p.strip())
    if notes:
        if re.search(r'^\s*notes?:', notes, re.I | re.M):
            print(f'  !! a note contains a line starting "Note:" — would split wrongly', file=sys.stderr)
        md += '\n\nNote:\n' + notes
    return md


def main():
    src = open('index.html').read()
    body = src[src.index('<div class="slides">') + len('<div class="slides">'):src.rindex('</div>\n</div>')]
    cols = top_level_elements(body)
    cols = [c for c in cols if c[0] == 'section']
    assert len(cols) == len(ACTS), f'expected {len(ACTS)} columns, found {len(cols)}'

    os.makedirs('content', exist_ok=True)
    for (slug, title), (_, _, outer, inner) in zip(ACTS, cols):
        leaves = [e for e in top_level_elements(inner) if e[0] == 'section']
        if not leaves:  # a column whose only slide is the wrapper itself
            leaves = [(None, outer_attrs_of(outer), outer, inner)]
        chunks = [convert_slide(at, ins) for _, at, _, ins in leaves]
        doc = f'<!-- {title} — {len(leaves)} slide(s). "---" starts a new slide (Down). -->\n\n'
        doc += '\n\n---\n\n'.join(chunks) + '\n'
        open(f'content/{slug}.md', 'w').write(doc)
        print(f'  content/{slug}.md  {len(leaves)} slides, {len(doc.splitlines())} lines')


if __name__ == '__main__':
    main()
