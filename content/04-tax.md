<!-- The Tax — 13 slide(s). "---" starts a new slide (Down). -->

<!-- .slide: class="center-slide" data-state="act" -->

<p class="kicker">Kafka's Partition Tax</p>

## Where does the waste come from?

Nobody sets out to over-provision, but Kafka encourages it.
<!-- .element: class="mute" -->

---
## Ignorance and blind approval


  <img src="assets/images/partition-cost-meme.jpg" alt="How much could a partition cost, Michael? $20?">


Note:
Teams don't know how many partitions they need, so they look for examples and pick a random number.
The platform team doesn't know the use case and don't want to slow down development.
But let's put this aside for now.

---
## Partitions limit consumer scalability (myth)

<figure>
    <img src="assets/diagrams/consumer-parallelism.svg" alt="A topic with four partitions feeds four consumers, one each. A fifth consumer has no partition to take and sits idle.">

</figure>

Note:
The structural fact everybody knows but few price: within a consumer group,
one partition goes to exactly one consumer. Add a consumer beyond the
partition count and it does nothing at all.

So the moment a team needs more consumer parallelism, the only lever Kafka
offers them is partitions. They are not being careless. They are using the
only knob on the machine.

---

## Partitions dictated by consumer *processing speed*

<figure>
    <img src="assets/diagrams/latency-math.svg" alt="50 ms per record gives 20 records per second per consumer; 1,000 records per second therefore needs 50 consumers and so 50 partitions, to carry just 1 MB/s of data.">
  </figure>

Note:
Walk this slowly, it is the most important arithmetic in the talk.

One external call per record, 50ms — a perfectly ordinary internal service
call, nothing pathological. That consumer thread now does twenty records a
second. Not twenty thousand. Twenty.

Topic does 1,000 records a second, so you need 50 consumers, so you create
50 partitions. And the data underneath is one megabyte a second — a tenth
of what a single partition handles.

Nobody in that story did anything unreasonable. That is what makes this
expensive.


---

## And you can't take it back

<pre><code data-trim data-noescape class="language-text">
hash("user-123") % 4  ->  partition 0
hash("user-123") % 6  ->  partition 2
</code></pre>

You have to decide at topic create time how many partitions you need, or else key-based ordering breaks.

---

## The stream processing tax

<figure>
  <img src="assets/diagrams/streams-fanout.svg" alt="One input topic with 24 partitions forces seven internal repartition and changelog topics to 24 partitions each — 192 partitions in total for a job carrying under 100 KB/s.">
</figure>


Note:
A real customer's job — don't name them or the industry.

One input topic at 24 partitions. By the time Streams had built the
topology there were almost 200 partitions between them, carrying under
100 KB/s in total. One partition runs at a hundred times that on its own.

CITABLE: "The input topics of the join (left side and right side) must have
the same number of partitions" — Kafka Streams docs, and ksqlDB says the
same. A join forces both sides to match.

NOT IN THE DOCS, BUT IT IS IN THE SOURCE. Confluent never wrote the
inheritance rule down, so if anyone challenges it, cite Apache Kafka trunk,
streams/src/main/java/org/apache/kafka/streams/processor/internals:

  - PartitionGrouper: one task per partition index, looping to
    maxNumPartitions(sourceTopicGroup) — the task count is the largest
    source topic in that subtopology.
  - ChangelogTopics.setup: "the expected number of partitions is the max
    value of TaskId.partition + 1" — one changelog partition per task.
  - RepartitionTopics.computePartitionCount: "use the maximum of all its
    source topic partitions as the number of partitions".

Those two quoted strings are verbatim comments in the code. This is not
folklore; it is just not in the documentation.

Worth adding out loud: changelog topics are compacted AND replicated. This
is not only a partition count, it is durable state on disk, three times over.

If someone says "so set the input topic to 3" — yes, exactly. That is the
one decision that mattered, and it is the one nobody goes back to.


---

<p class="kicker">And in fairness</p>

## Over-provisioning is the easy and popular recommendation

<blockquote class="small">
    "When in doubt, slightly over-provision."
  </blockquote>

<blockquote class="small fragment">
    "Plan for growth: if you expect 20 consumers, start with at least 20 partitions."
  </blockquote>

Both of those are on <em>our own blog</em>
<!-- .element: class="pad-top fragment mute small" -->

<strong>Another of our posts recommends 3–6 partitions for anything under 10 MB/s.</strong>
<!-- .element: class="pad-top fragment" -->

Note:
Say this cheerfully and own it. I am not here to tell anyone they were
stupid — the default advice, including ours, points one way and the
economics point the other.

Both quotes are verbatim from "Partition Count: The Decision You Can't Undo"
on conduktor.io/blog. The 3-6 figure is from a second live post, "Stop
Over-Partitioning". All of it is public right now — do NOT say we never
published it, because anyone can pull the URL up in ten seconds.

Do not name the author. It is a colleague's post, and the point is the
industry-wide reflex, not one person. "Our own blog" is the right framing.

The last line is the sharpest thing on this slide: our published guidance
contradicts the talk I am giving. Deliver it flatly, without squirming. It
buys the credibility I need for the next thirty minutes.

---

## How we defined waste

<figure>
    <img src="assets/diagrams/waste-definition.svg" alt="Fifty partitions on a 1 MB/s topic read by three consumers: three are working, forty-seven are pure overhead.">
  </figure>

Note:
I want this bar so low that nobody can argue with it. A partition only
counts as wasted if the topic does under 1 MB/s AND there are more
partitions than the largest consumer group has members.

That is not aggressive. Ten MB/s topics could usually run on one partition
too. I'm leaving that on the table so the number is unarguable.

Across the clusters we analyse, that conservative bar still finds 40 to 70
percent of infrastructure cost.

---

<p class="kicker">What is the cost?</p>

## Managed Kafka puts it right in the bill

<div class="cols pad-top">
    <div class="panel">
      <h4>What you're billed for</h4>
      <p>Per partition-hour, plus hard ceilings per unit of capacity. Confluent Cloud allows 4,500 partitions per CKU.</p>
    </div>
    <div class="panel bad">
      <h4>What that means</h4>
      <p>You buy a cluster rated for 240 MB/s produce and 720 MB/s consume to move less than 10 MB/s.</p>
    </div>
  </div>

<strong>The conservative waste measurement often equates to hundreds of thousands of dollars per year.</strong>
<!-- .element: class="pad-top fragment" -->

Note:
On managed, I don't have to work to make this argument. The bill makes it.
Move through this quickly — the self-managed case is where the room starts
arguing with me, and that's the interesting part.

---

<!-- .slide: class="center-slide" -->

## "But we self-manage.
<!-- .element: class="mute" -->

## We're not charged per partition."
<!-- .element: class="mute" -->

That doesn't make partitions free.
<!-- .element: class="pad-top fragment lime" -->

Note:
I hear this in almost every conversation. Pause here — let people who were
thinking it feel seen before I answer it.

---

## Replicas set your broker count

<figure>
    <img src="assets/diagrams/broker-math.svg" alt="100,000 partitions at replication factor 3 is 300,000 replicas; at 4,000 per broker that is 75 brokers, against about 4 needed for the actual throughput.">
  </figure>

Note:
The recommended ceiling is 4,000 to 6,000 replicas per broker, and that
counts total replicas, not leaders.

Yes, better hardware raises it. AWS publishes about 12,000 for a tuned
m7g.8xlarge. Fine — that's 25 brokers instead of 75. The throughput still
only needs about four.

On most clusters I look at, replica count is the binding constraint. Not
throughput. Not storage.

---

<!-- .slide: class="center-slide" -->

## "We upgraded to KRaft.
<!-- .element: class="mute" -->

## For us the sky is the limit."
<!-- .element: class="mute" -->

KRaft raised the cluster's partition ceiling, not the broker's.
<!-- .element: class="pad-top fragment lime" -->

Note:
Be genuinely appreciative about KRaft here — it IS a real improvement, and
I don't want to sound like I'm knocking it. It raised the cluster-wide
metadata ceiling, cut broker startup times, sped up reassignment and topic
creation enormously.

None of which touches the per-broker cost of a partition.

---

## What every partition still costs each broker

<ul class="small">
    <li><strong>File descriptors</strong> — every replica is log segment files on disk</li>
    <li class="fragment"><strong>Memory</strong> — Kafka holds an in-memory buffer per partition</li>
    <li class="fragment"><strong>Random I/O</strong> — more partitions, more scattered reads and writes</li>
    <li class="fragment"><strong>Replication latency</strong> — one fetcher thread per broker pair by default</li>
    <li class="fragment"><strong>Request handling</strong> — even empty partitions generate replication fetches</li>
  </ul>

<blockquote class="small fragment">
    "Replicating 1000 partitions from one broker to another can add about 20 ms latency, which implies that the end-to-end latency is at least 20 ms."
    <span class="attrib">Jun Rao, Confluent</span>
  </blockquote>

Note:
Don't read the list aloud item by item, that's deadly. Hit file descriptors
and memory, then land on the Jun Rao quote — it's from one of Kafka's
original authors and it's about latency, which the room cares about more
than disk.

---

<p class="kicker">Pain in the ops</p>

## Leader elections (still) aren't free

Failure, restart, routine upgrade — every partition that broker led needs a leader election.
<!-- .element: class="pad-top" -->


kRaft sped up leader elections by 10X
<!-- .element: class="pad-top fragment small mute" -->
But Kafka is still drowning if you have 20X too many partitions
<!-- .element: class="pad-top fragment small mute" -->

Note:
If I only get one point across in Act 1, make it this one. Cost arguments
get deferred to next quarter. Rolling-restart windows and failover times
get fixed.

---

<!-- .slide: class="center-slide" -->

## How do we fix it?

Note:
End of Act 1. Take a breath here. The next 30 minutes are all remedy.
