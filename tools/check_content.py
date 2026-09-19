#!/usr/bin/env python3
"""Catch silent authoring faults in content/*.md.

Both of these fail QUIETLY — the deck still renders, it is just wrong:

  1. a bare "---" inside a <pre> block. Reveal splits slides on "---" before
     any HTML is parsed, so a multi-document YAML sample silently cuts the
     slide in half.
  2. "<!--" or "-->" nested inside an HTML comment. The first inner "-->"
     closes the comment early and the remainder renders as visible text.
"""
import glob, re, sys

problems = []
for f in sorted(glob.glob('content/*.md')):
    src = open(f).read()
    for m in re.finditer(r'<pre>.*?</pre>', src, re.S):
        for i, ln in enumerate(m.group(0).split('\n')):
            if ln.strip() == '---':
                line = src[:m.start()].count('\n') + 1 + i
                problems.append(f"{f}:{line}  bare '---' inside <pre> — splits the slide in two")
    for m in re.finditer(r'<!--(.*?)-->', src, re.S):
        if '<!--' in m.group(1) or '-->' in m.group(1):
            line = src[:m.start()].count('\n') + 1
            problems.append(f"{f}:{line}  nested comment marker — closes the comment early")

for p in problems:
    print(f"  {p}")
print(f"{'content OK' if not problems else str(len(problems)) + ' problem(s)'}")
sys.exit(1 if problems else 0)
