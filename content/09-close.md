<!-- Close — 6 slide(s). "---" starts a new slide (Down). -->

<!-- .slide: class="center-slide" data-state="act" -->

<p class="kicker">To take away</p>

# Two things

<div class="spine" data-act="done"></div>

A checklist, and a way to choose
<!-- .element: class="mute pad-top" -->

---

<p class="kicker">Takeaway one</p>

## Audit your own partition waste

<ol class="checklist">
    <li>List every topic by partition count, descending.</li>
    <li>For each, pull <strong>peak</strong> producer throughput over 7 days — peak, not average.</li>
    <li>For each, pull the <strong>maximum member count</strong> across all its consumer groups.</li>
    <li>Flag any topic where <code>throughput &lt; 1 MB/s</code> <em>and</em> <code>partitions &gt; max group members</code>.</li>
    <li>Sum the excess partitions on flagged topics. Multiply by replication factor.</li>
    <li class="fragment">Self-managed: divide by your replicas-per-broker ceiling. That's brokers you run for nothing.</li>
    <li class="fragment">Managed: multiply by your partition-hour rate × 8,760. That's an annual line item.</li>
  </ol>

Steps 2 and 3 are the ones people skip, and they're the ones that make the number defensible.
<!-- .element: class="small mute fragment" -->

Note:
Tell them to photograph this one. Then make the promise explicit: this is
an afternoon of work, and the number at the end is theirs, not mine.

Emphasise PEAK not average on step 2 — averaging over a week hides the
daily batch spike and someone will correctly challenge the result.

---

<p class="kicker">Takeaway two</p>

## Which layer do you reach for?

<table class="small">
    <tr><th>Your situation</th><th>Reach for</th></tr>
    <tr><td>Topics still being created</td><td class="lime">Prevent — fix the template default, then the ceiling</td></tr>
    <tr><td>Sprawl exists, teams are responsive</td><td class="lime">Clean — attribute it, then let them act</td></tr>
    <tr><td>Consumer too slow · per-key order matters · you can change the app</td><td class="lime">Fix — per-key concurrent consumer</td></tr>
    <tr><td>Consumer too slow · ordering genuinely irrelevant</td><td class="lime">Share groups — the right tool for this one</td></tr>
    <tr><td>Consumer too slow · you cannot change the app</td><td class="lime">Patch — proxy, and accept the trade</td></tr>
    <tr><td>Long tail of tiny topics · non-prod sprawl</td><td class="lime">Patch — virtualisation and concentration</td></tr>
  </table>

Two questions get you to a row: <strong>does per-key order matter</strong>, and <strong>can you change the app?</strong>
<!-- .element: class="small mute pad-top fragment" -->

Note:
The second screenshot slide. This is the artifact the abstract promised, so
make sure it's on screen long enough to photograph.

If you only remember two questions from this talk: does per-key ordering
matter, and can you change the code. Everything else follows.

---

## If you do one thing on Monday

Run steps 1 to 4 of that checklist. It takes an afternoon.
<!-- .element: class="pad-top" -->

Most teams are genuinely surprised by the answer — and you cannot make the case for any of the other three layers without it.
<!-- .element: class="pad-top fragment" -->

Then change one template default from 30 to 1. That's the cheapest structural fix in this entire talk, and it stops the bleeding while you deal with the rest.
<!-- .element: class="pad-top small mute fragment" -->

Note:
End on something that costs them nothing and needs nobody's approval.
Never end a cost talk with "buy something".

---

<!-- .slide: class="center-slide" -->

# Thank you

<div class="title-rule"></div>

Chuck Larrieu Casias · Conduktor<br> <span class="mute">Slides, checklist and sources:</span><br> <a href="https://chuck-alt-delete.github.io/partition-tax">chuck-alt-delete.github.io/partition-tax</a>
<!-- .element: class="title-meta" -->

Ask me about the virtual partition idea. I still think there's something there.
<!-- .element: class="tiny mute pad-top" -->

Note:
Leave this up for Q and A. Expect: "what about tiered storage", "does this
apply to Kafka Streams" (yes, and worse — internal topics inherit the input
partition count), and at least one person who wants to argue about share
groups. Welcome that argument, don't win it rudely.

---

## Sources

<ul class="tiny">
    <li>Confluent Cloud partition limits per CKU — Confluent Cloud documentation</li>
    <li>4,000–6,000 replicas per broker; ~12,000 on a tuned <code>m7g.8xlarge</code> — AWS MSK quotas documentation</li>
    <li>"Replicating 1000 partitions… about 20 ms latency" — Jun Rao, <em>How to Choose the Number of Topics/Partitions in a Kafka Cluster</em>, Confluent</li>
    <li>KRaft metadata and startup improvements — Confluent Developer; Instaclustr KRaft benchmarks</li>
    <li>"Records in a share-partition can be delivered out of order" — KIP-932, Queues for Kafka</li>
    <li>KIP-X, <em>Introduce a cooperative consumer processing semantic</em> (2019) — Apache Kafka wiki</li>
    <li>Parallel Consumer — <code>github.com/astubbs/parallel-consumer</code> (fork of the deprecated <code>confluentinc/parallel-consumer</code>)</li>
    <li>kpipe — <code>github.com/eschizoid/kpipe</code> · llingr-demux — <code>llingr.io</code></li>
    <li>Background posts — <em>The Surprising Cost of Kafka Partition Waste</em> and <em>Kafka Partitions are the Wrong Ordering Abstraction, Keys Are</em>, conduktor.io/blog</li>
  </ul>

Note:
Backup slide — don't present it. It exists so the published deck is
citable and so anyone who challenges a number can check it themselves.
