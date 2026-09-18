<!-- Audience poll — 3 slide(s). "---" starts a new slide (Down). -->

<p class="kicker">Audience poll</p>

## Every topic needs at least one partition.

So your topic count is the <em>floor</em> on your partition count.
<!-- .element: class="mute pad-top" -->

<strong>How many topics do you run?</strong>
<!-- .element: class="pad-top fragment" -->

A hundred? A thousand? More?
<!-- .element: class="mute small fragment" -->

Note:
ASK THE ROOM. Get an actual number shouted out. Anchor on whatever the
biggest confident answer is — aim to land on ~1,000 so the next slide's
arithmetic is clean. If someone shouts 10,000, even better, the gap gets
wider. Wait for the answer. Don't rush this.

---

<!-- .slide: data-state="poll" -->

<p class="kicker">Two shows of hands</p>

## 1,000 partitions <span class="faint">×</span> 10 MB/s per partition <span class="faint">=</span> <span class="lime">10 GB/s</span>
<!-- .element: class="nomargin" -->

<p class="small mute" style="margin:0.35em 0 0.2em 0">864 terabytes a day. That is the workload 1,000 partitions is sized for.</p>

<figure class="poll-figure">
<svg class="poll-bar" viewBox="0 0 1000 140" role="img"
       aria-label="A bar representing the 10 GB/s that 1,000 partitions can carry. A genuinely busy cluster at 1 GB/s fills only a tenth of it.">
    <rect x="2" y="8" width="996" height="86" rx="10" fill="rgba(188,254,104,0.08)" stroke="#bcfe68" stroke-width="2"/>
    <text x="2" y="126" font-family="ui-monospace,Menlo,monospace" font-size="18" fill="#5d777c">capacity 1,000 partitions can carry</text>
    <g class="fragment" data-fragment-index="3">
      <rect class="sliver-rect" x="2" y="8" width="100" height="86" rx="10" fill="rgba(226,114,91,0.62)" stroke="#e2725b" stroke-width="2"/>
      <text x="120" y="44" font-family="ui-monospace,Menlo,monospace" font-size="20" fill="#e2725b">a genuinely busy cluster: 1 GB/s</text>
      <text x="120" y="74" font-family="ui-monospace,Menlo,monospace" font-size="20" fill="#5d777c">the other 90% is headroom nobody asked for</text>
    </g>
  </svg>
</figure>

<div class="poll-asks">
    <p class="fragment fade-up" data-fragment-index="1">
      <span class="hand up">&#8593;</span>Hands up if you run more than <strong>1,000 partitions</strong>.
    </p>
    <p class="fragment fade-up" data-fragment-index="2">
      <span class="hand down">&#8595;</span>Keep them up if you push more than <strong>10 GB/s</strong>.
    </p>
  </div>

Note:
Ten MB/s per partition is a deliberately conservative per-partition figure —
a single partition on decent hardware does considerably better. Say so; I am
being generous on purpose.

CLICK 1 — "Hands up if you run more than 1,000 partitions." Most of the room
goes up. Look around, acknowledge it.

CLICK 2 — "Now keep them up if you push more than 10 GB/s." Almost every hand
drops. WAIT. Do not fill the silence, the silence is the argument.

CLICK 3 — the bar fills in to a tenth. "This is what a genuinely busy cluster
actually does."

CLICK 4 — the line. Then move on; do not over-explain it.

---

<!-- .slide: class="center-slide" -->

## Your partition count is not set by producer throughput.
<!-- .element: class="lime" -->

If it were, partition count would be much closer to topic count.
<!-- .element: class="mute pad-top" -->

So what <em>is</em> setting it?
<!-- .element: class="pad-top fragment" -->

Note:
This is the hinge of the whole talk. Everything after this is answering
that question, and then doing something about the answer.
