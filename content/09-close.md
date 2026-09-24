<!-- Close — 6 slide(s). "---" starts a new slide (Down). -->

<!-- .slide: class="center-slide" data-state="act" -->

<p class="kicker">To take away</p>

# Takeaways

<div class="spine" data-act="done"></div>

---

<p class="kicker">Takeaway one</p>

## Audit your own partition waste

<ol class="checklist">
    <li class="fragment">List every topic by partition count, descending.</li>
    <li class="fragment">For each, pull <strong>peak</strong> producer throughput over 7 days — peak, not average.</li>
    <li class="fragment">For each, pull the <strong>maximum member count</strong> across all its consumer groups.</li>
    <li class="fragment">Flag any topic where <code>throughput &lt; 1 MB/s</code> <em>and</em> <code>partitions &gt; max group members</code>.</li>
    <li class="fragment">Sum the excess partitions on flagged topics. Multiply by replication factor.</li>
    <li class="fragment">Self-managed: divide by your replicas-per-broker ceiling. That's excess brokers.</li>
    <li class="fragment">Managed: multiply by your partition-hour rate × 8,760. That's an annual line item.</li>
  </ol>


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
    <tr><td>Topics still being created</td><td class="lime">Prevent — automated guardrails and templates</td></tr>
    <tr><td>Sprawl exists, teams are responsive</td><td class="lime">Clean — attribute the cost, then let them act (or pay)</td></tr>
    <tr><td>Consumer too slow · per-key order matters · you can change the app</td><td class="lime">Optimize — parallel consumer, KEY mode</td></tr>
    <tr><td>Consumer too slow · no ordering needed · batch commits are fine</td><td class="lime">Optimize — parallel consumer, UNORDERED mode</td></tr>
    <tr><td>Consumer too slow · no ordering needed · you need per-message ack</td><td class="lime">Share groups — the right tool for this one</td></tr>
    <tr><td>non-prod sprawl</td><td class="lime">Patch — virtual clusters</td></tr>
    <tr><td>Long tail of tiny topics</td><td class="lime">Patch — topic concentration</td></tr>
    <tr><td>Consumer too slow · you cannot change the app</td><td class="lime">Patch — virtual partitions (not yet implemented)</td></tr>
  </table>


Note:
The second screenshot slide. This is the artifact the abstract promised, so
make sure it's on screen long enough to photograph.

If you only remember two questions from this talk: does per-key ordering
matter, and can you change the code. Everything else follows.

---

## If you do one thing on Monday

Run steps 1 to 4 of that checklist. It doesn't take long.
<!-- .element: class="pad-top" -->

Most teams are genuinely surprised by the answer, and it helps build a business case for implementing proper governance and Kafka development practices.
<!-- .element: class="pad-top" -->

Talk to us if you're interested in Kafka governance, proxies, or developer experience.
<!-- .element: class="pad-top" -->


Note:
End on something that costs them nothing and needs nobody's approval.
Never end a cost talk with "buy something".

---

<!-- .slide: class="center-slide" -->

# Thank you

<div class="title-rule"></div>

Chuck Larrieu Casias · Conduktor<br> <span class="mute">Slides, checklist and sources:</span><br> <a href="https://chuck-alt-delete.github.io/partition-tax">chuck-alt-delete.github.io/partition-tax</a>
<!-- .element: class="title-meta" -->


Note:
Leave this up for Q and A. Expect: "what about tiered storage", "does this
apply to Kafka Streams" (yes, and worse — internal topics inherit the input
partition count), and at least one person who wants to argue about share
groups. Welcome that argument, don't win it rudely.

---

## Sources

<ul class="tiny">
    <li>Dedicated CKU: 4,500 partitions, 60 MB/s ingress, 180 MB/s egress, and a guideline of ~12 MB/s ingress per partition — <em>Confluent Cloud cluster types, partition guidelines</em> · <code>docs.confluent.io/cloud/current/clusters/cluster-types.html</code></li>
    <li>4,000–6,000 replicas per broker; ~12,000 on a tuned <code>m7g.8xlarge</code> — AWS MSK quotas documentation</li>
    <li>"One can produce at 10s of MB/sec on just a single partition" and "replicating 1000 partitions… about 20 ms latency" — Jun Rao, <em>How to Choose the Number of Topics/Partitions in a Kafka Cluster</em>, Confluent, 2015 · <code>confluent.io/blog/how-choose-number-topics-partitions-kafka-cluster</code></li>
    <li>"The input topics of the join (left side and right side) must have the same number of partitions" — Kafka Streams co-partitioning requirements, Confluent docs; ksqlDB states the same</li>
    <li>Internal topics inherit the source partition count — Apache Kafka source, <code>streams/…/processor/internals</code>: <code>RepartitionTopics.computePartitionCount</code> ("the maximum of all its source topic partitions"), <code>ChangelogTopics.setup</code> ("max value of TaskId.partition + 1"), <code>PartitionGrouper.maxNumPartitions</code>. Not stated in the published docs.</li>
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
