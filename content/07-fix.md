<!-- Fix the root cause — 17 slide(s). "---" starts a new slide (Down). -->

<!-- .slide: class="center-slide" data-state="act" -->

<p class="kicker">Layer three</p>

# Fix the root cause

<div class="spine" data-act="3"></div>

Stop needing the partitions in the first place
<!-- .element: class="mute pad-top" -->

---

<!-- .slide: class="center-slide" -->

<blockquote style="border:none;padding:0">
    <h2 class="mute">"We need more partitions.</h2>
    <h2 class="mute">Our consumer can't keep up."</h2>
  </blockquote>

This ticket is the single largest source of partition sprawl I see.
<!-- .element: class="pad-top fragment" -->

And it is almost always a correct observation with the wrong remedy attached.
<!-- .element: class="small mute fragment" -->

Note:
Everyone in the room has either written this ticket or approved it. Say so.
The team is right that they have a problem. They're reaching for the only
lever Kafka shows them.

---

## The diagnosis underneath it

Consumers that can't keep up are almost never CPU-bound. They're waiting.
<!-- .element: class="pad-top mute" -->

<ul class="pad-top small">
    <li class="fragment">An external HTTP call per record</li>
    <li class="fragment">A database write, then a read-back</li>
    <li class="fragment">An enrichment lookup against another service</li>
    <li class="fragment">ML inference, RAG retrieval, an LLM call</li>
  </ul>

<strong>One partition = one unit of work = one thread.</strong>
<!-- .element: class="pad-top fragment" -->

That model is fine when processing takes microseconds. It collapses the moment processing means <em>waiting on something else</em> — and in 2026 that is most consumers.
<!-- .element: class="fragment small mute" -->

Note:
The vanilla consumer's threading model was designed for fast, local,
CPU-bound work. Event-driven systems stopped looking like that years ago,
and AI workloads have made it dramatically worse — an LLM call is seconds,
not milliseconds.

---

## What you're actually paying for

<figure>
    <img src="assets/diagrams/head-of-line.svg" alt="Key A takes 4 seconds while keys B, C and D, needing 100 ms each, wait behind it on the same partition.">
  </figure>

Note:
This is head-of-line blocking and it's the real defect. B, C and D are
different customers, different orders, different entities. They have no
business relationship with A whatsoever. They're waiting because a hashing
function put them in the same bucket.

Adding partitions makes this statistically less likely. It never makes it
go away.

---

<!-- .slide: class="center-slide" -->

## Partitions are an infrastructure concern.
<!-- .element: class="lime" -->

## Keys are the domain concern.
<!-- .element: class="lime" -->

Nobody in your business cares whether <code>user_42</code> lives on partition 7 or partition 23.
<!-- .element: class="pad-top mute" -->

They care that events about <code>user_42</code> are processed in order.
<!-- .element: class="pad-top fragment" -->

Note:
This is the intellectual centre of the talk. Slow down.

The partition exists because Kafka needs to shard data across brokers and
distribute work across instances. It is a side effect of horizontal
scaling. The key is what the domain actually cares about.

Using partitions for ordering couples a business guarantee to a deployment
parameter. That's a leaky abstraction, and you pay for the leak in
permanent infrastructure.

---

## So what does "add partitions" actually do?

<div class="cols pad-top">
    <div class="panel">
      <h4>What you wanted</h4>
      <p>More things happening at once.</p>
    </div>
    <div class="panel bad">
      <h4>What you bought</h4>
      <p>Permanent infrastructure. More replicas to host, longer leader elections when a broker dies, more controller work, and a bigger bill on anything priced per partition.</p>
    </div>
  </div>

<strong>You converted a processing problem into an infrastructure problem — through a one-way door.</strong>
<!-- .element: class="pad-top fragment" -->

And you only get parallelism up to the partition count, so the next slow dependency starts the cycle again.
<!-- .element: class="small mute fragment" -->

Note:
Land this hard. It connects Act 4 straight back to Act 1's arithmetic:
this is where those 200 partitions came from.

---

<!-- .slide: class="center-slide" -->

## "Fine — so we use share groups.
<!-- .element: class="mute" -->

## Queues for Kafka. That's the fix, right?"
<!-- .element: class="mute" -->

Share groups are genuinely good. They are also solving a different problem.
<!-- .element: class="pad-top fragment lime" -->

Note:
Tone check: I am NOT here to trash KIP-932. It's excellent work and I'm
glad it shipped. My objection is narrow and specific: it is being pointed
at as the replacement for Parallel Consumer, and it is not that.

Say the positive part first and mean it.

---

## What share consumers actually give you

KIP-932, GA in Apache Kafka 4.2
<!-- .element: class="mute small" -->

<pre><code data-trim class="language-text">Available  ->  Acquired  ->  Acknowledged</code></pre>

<ul class="small pad-top">
    <li>Each record is individually <em>acquired</em> by a consumer, processed, then acknowledged</li>
    <li class="fragment">Per-message acks: ACCEPT, RELEASE (retry it), REJECT (dead-letter it)</li>
    <li class="fragment">Consumer count is no longer capped by partition count</li>
  </ul>

<strong>For job queues this is exactly right.</strong> Render this PDF, send this email, transform this image. Independent tasks, per-record retry, maximum throughput.
<!-- .element: class="pad-top fragment" -->

Note:
Give share groups a full, fair hearing. If the room thinks I'm strawmanning
them, I lose the next slide, which is the one that matters.

---

## And here is the line that decides it

<blockquote>
    "The records in a share-partition can be delivered <em>out of order</em> to a consumer."
    <span class="attrib">KIP-932</span>
  </blockquote>

Can, in a distributed system under load, means will.
<!-- .element: class="pad-top fragment small mute" -->

<div class="panel bad fragment pad-top">
    <h4>What that costs you in an event-driven system</h4>
    <p><code>UserUpdated(user=42)</code> arrives at offset 10.<br>
       <code>UserDeleted(user=42)</code> arrives at offset 50.</p>
    <p>Process them out of order and you have just resurrected a deleted user.</p>
  </div>

Note:
There is no per-partition order and no per-key order. That's not a bug,
it's the design — it's what buys the per-message acking.

The resurrected user is the example that makes people's faces change,
because everyone has a version of it. GDPR deletion is the one that gets
quoted back to me afterwards.

---

<!-- .slide: class="center-slide" -->

## Telling people to move from Parallel Consumer to share groups

## is like telling them to move from Postgres to Redis
<!-- .element: class="lime" -->

## because both store data.
<!-- .element: class="mute" -->

Both are excellent. The semantics are not interchangeable.
<!-- .element: class="pad-top small mute fragment" -->

Note:
This is the quotable line. Deliver it and then stop talking for two seconds.

---

<!-- .slide: class="center-slide" -->

## What you actually want

<div class="cols pad-top" style="max-width:860px;margin:0 auto">
    <div class="panel good"><h4>Parallelism</h4><p>across keys</p></div>
    <div class="panel good"><h4>Ordering</h4><p>within a key</p></div>
    <div class="panel good"><h4>Correctness</h4><p>of offset commits</p></div>
  </div>

Decoupled from how many partitions the topic happens to have.
<!-- .element: class="pad-top" -->

Two of these are easy. The third is where homegrown attempts die.
<!-- .element: class="small mute fragment" -->

Note:
Set up the next slide. Everyone thinks this is a thread pool keyed by
record key. That part takes an afternoon. Then you meet offsets.

---

## The part everyone underestimates

<figure>
    <img src="assets/diagrams/offset-commit.svg" alt="Offsets 100 to 108: 100-104 done, 105 still in flight, 106-108 done. The highest contiguous completed offset is 104.">
  </figure>

Note:
Walk the two wrong answers first, let the room feel the trap, then give the
right one.

Commit 108 and crash: 105 is gone. Silently. You will find out in a
reconciliation report next quarter.

Wait for 105: congratulations, you've rebuilt head-of-line blocking inside
your own application.

The right answer needs a completed-offset map per partition, in-memory gap
tracking, bounded memory, backpressure, and correct behaviour across
rebalances. Parallel Consumer stuffs that state into the offset commit
metadata string that nobody else was using.

---

## "Can't I just use virtual threads?"

<div class="cols pad-top">
    <div class="panel good">
      <h4>What virtual threads solve</h4>
      <p>The <em>concurrency cost</em>. Millions of them, and a blocking HTTP call no longer pins an OS thread. Genuinely great for IO-bound work.</p>
    </div>
    <div class="panel bad">
      <h4>What they don't solve</h4>
      <p>Ordering and offset-commit correctness. Those are a different layer, and they don't come for free with a cheaper thread.</p>
    </div>
  </div>

Thread per partition: about the same as the vanilla consumer. Thread per key: now you need in-flight key tracking, a completed-offset tracker, backpressure, rebalance handling and bounded memory.
<!-- .element: class="small mute pad-top fragment" -->

<strong>Which is to say: you've started writing Parallel Consumer.</strong>
<!-- .element: class="fragment" -->

Note:
I get this question every single time, and it's a good instinct, not a
stupid one. Virtual threads are the right execution layer. They are not a
contract layer.

---

## Parallel Consumer, briefly

<table>
    <tr><th>Mode</th><th>Ordering guaranteed</th><th>Use it for</th></tr>
    <tr><td class="mono lime">KEY</td><td>Records sharing a key process sequentially; different keys run concurrently</td><td>Event-driven systems, event sourcing</td></tr>
    <tr><td class="mono">UNORDERED</td><td>None</td><td>Independent tasks, order irrelevant</td></tr>
    <tr><td class="mono">PARTITION</td><td>Per-partition, same as vanilla</td><td>Vanilla semantics without multiplexing N partitions onto one thread</td></tr>
  </table>

<strong>KEY is the default, and it's the one you want.</strong> You set <code>maxConcurrency</code>, not partition count.
<!-- .element: class="pad-top small" -->

One instance assigned 10 partitions can run 10, 100 or 1,000 concurrent units of work — without touching the rebalance protocol or stealing partitions from anyone.
<!-- .element: class="small mute fragment" -->

Note:
The crucial architectural point: it parallelises WITHIN the partitions
already assigned to that instance. It doesn't change group membership and
doesn't touch rebalancing. That's why it's safe to adopt incrementally.

---

## Three to look at

<table class="small">
    <tr><th>Library</th><th>Shape</th><th>Worth knowing</th></tr>
    <tr>
      <td class="mono lime">parallel-consumer<br><span class="tiny mute">github.com/astubbs</span></td>
      <td>Java, wraps the vanilla consumer</td>
      <td>Confluent deprecated the original; Antony Stubbs, one of its original implementers, forked it and is actively improving it</td>
    </tr>
    <tr>
      <td class="mono lime">kpipe<br><span class="tiny mute">github.com/eschizoid</span></td>
      <td>Java virtual threads over the vanilla consumer</td>
      <td>Newer and smaller. I have not run it in anger — evaluate before you depend on it</td>
    </tr>
    <tr>
      <td class="mono lime">llingr-demux<br><span class="tiny mute">llingr.io</span></td>
      <td>Go core; Java/Kotlin/Scala bindings, Rust FFI, gRPC sidecar</td>
      <td>Per-key routing to workers with contiguous offset commit. Marked patent pending and the licence isn't published — check that before adopting</td>
    </tr>
  </table>

Performance figures on these projects are the maintainers' own. Benchmark against your workload before you believe any of them, mine included.
<!-- .element: class="tiny mute pad-top" -->

Note:
Be scrupulously fair here. I'm recommending a category, not a vendor. The
llingr licensing caveat is real and I should say it out loud rather than
bury it — an unlicensed dependency is a non-starter at most of the
companies in this room.

If asked which I'd start with: the astubbs fork, because it's Apache 2.0,
it's battle-tested, and the maintainer wrote the original.

---

## One question decides it

<figure>
    <img src="assets/diagrams/decision-tree.svg" alt="Decision tree: does per-key order matter? Yes leads to a per-key concurrent consumer; no with order irrelevant leads to Share Consumers; no and already fast leads to the vanilla consumer.">
  </figure>

Note:
Screenshot slide. Pause on it.

Then the point that ties Act 4 to Act 1: "add more partitions" is not an
answer to any of these three questions. It never was. It's just the only
lever that was in reach.

---

<!-- .slide: class="center-slide" -->

## This should be in Apache Kafka

Key-level parallelism belongs in <code>org.apache.kafka.clients.consumer</code>, not in a third-party library you have to know exists.
<!-- .element: class="pad-top mute" -->

Somebody proposed roughly this in <strong>2019</strong> — KIP-X, "a cooperative consumer processing semantic". It went nowhere.
<!-- .element: class="pad-top small fragment" -->

Partition-level parallelism is a poor default for event-driven systems, and an actively bad one for anything calling a model.
<!-- .element: class="small mute fragment" -->

Note:
Say this as an ask to the community, not a complaint. There are Kafka
committers in this room and at this conference. That's the point of saying
it here rather than on a blog.
