<!-- Optimize the consumer — 17 slide(s). "---" starts a new slide (Down). -->

<!-- .slide: class="center-slide" data-state="act" -->

<p class="kicker">Layer three</p>

# Optimize the consumer

<div class="spine" data-act="3"></div>

Stop needing the partitions in the first place
<!-- .element: class="mute pad-top" -->

---

<!-- .slide: class="center-slide" -->

<blockquote style="border:none;padding:0">
    <h2 class="mute">"We need more partitions.</h2>
    <h2 class="mute">Our consumer can't keep up."</h2>
  </blockquote>



Note:
Everyone in the room has either written this ticket or approved it. Say so.
The team is right that they have a problem. They're reaching for the only
lever Kafka shows them.

---

## Beware IO-bound consumers!

Consumers that can't keep up are almost never CPU-bound. They're waiting.
<!-- .element: class="pad-top mute" -->

<ul class="pad-top small">
    <li class="fragment">An external HTTP call per record</li>
    <li class="fragment">A database write, then a read-back</li>
    <li class="fragment">An enrichment lookup against another service</li>
    <li class="fragment">ML inference, RAG retrieval, an LLM call</li>
  </ul>

<strong>One partition = one unit of work = one blocked thread.</strong>
<!-- .element: class="pad-top fragment" -->


Note:
The vanilla consumer's threading model was designed for fast, local,
CPU-bound work. It's not appropriate for IO-bound workloads.

---


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

<strong>For job queues this is exactly right.</strong> Render this PDF, send this email, transform this image. Independent tasks, per-record retry and acknowledgment.
<!-- .element: class="pad-top fragment" -->

Note:
Give share groups a full, fair hearing. If the room thinks I'm strawmanning
them, I lose the next slide, which is the one that matters.

---

## What is the cost of share groups?



<li class="fragment">No per-key ordering guarantee</li>

<div class="panel bad fragment pad-top">
    <p><code>UserUpdated(user=42)</code> arrives at offset 10.<br>
       <code>UserDeleted(user=42)</code> arrives at offset 50.</p>
    <p>Process them out of order and you have just resurrected a deleted user.</p>
  </div>

<li class="fragment">Metadata management overhead: The broker must track which records are in which state with which consumer.</li>


Just because you can scale consumers doesn't mean your throughput will be all that much better or that the overhead on the cluster will be worth it.
<!-- .element: class="pad-top fragment" -->



Note:
There is no per-partition order and no per-key order. That's not a bug,
it's the design — it's what buys the per-message acking.

The resurrected user is the example that makes people's faces change,
because everyone has a version of it. GDPR deletion is the one that gets
quoted back to me afterwards.

---

## "Can't I just use virtual threads? One per record?"

<strong>Yes!</strong>
<!-- .element: class="fragment" -->

Virtual threads in Java 21 let you create millions of threads in a developer-friendly way and delegates thread management to the OS. Awesome innovation!
<!-- .element: class="pad-top fragment muted" -->

But what about key-based ordering? And which offset should you commit?
<!-- .element: class="pad-top fragment muted" -->

Note:
I get this question every single time, and it's a good instinct, not a
stupid one. Virtual threads are the right execution layer. They are not a
contract layer.

---

<!-- .slide: class="center-slide" -->

## What you actually want your consumer to do

<div class="cols pad-top" style="max-width:860px;margin:0 auto">
    <div class="panel good"><h4>Parallelism</h4><p>per key</p></div>
    <div class="panel good"><h4>Ordering</h4><p>within a key</p></div>
    <div class="panel good"><h4>Offset management</h4></div>
  </div>

Decoupled from how many partitions the topic happens to have.
<!-- .element: class="pad-top" -->


Note:
Set up the next slide. Everyone thinks this is a thread pool keyed by
record key. That part takes an afternoon. Then you meet offsets.


---

## One consumer, one thread per key

<figure>
  <img src="assets/diagrams/key-parallelism.svg" alt="Three partitions hold records for four keys; A and C share partition 0, B is on partition 1, D on partition 2. One consumer instance is assigned all three partitions and runs four worker threads, one per key — four concurrent workers against three partitions.">
</figure>

Note:
Walk the left side first. Colour is the key, and a key always hashes to the
same partition — that is why every blue box is in p0. A and C share p0,
which is normal; partitions hold many keys.

Then the right. ONE consumer instance, assigned all three partitions, running
one worker per key. Four workers against three partitions — the number on the
right is not the number on the left, and that is the whole point.

Ordering still holds, and say why: every record for key A goes to the same
thread, so A's sequence is preserved. Nothing about B, C or D can overtake it,
and nothing about A can be reordered.

This is Parallel Consumer in KEY mode, and what kpipe and llingr-demux are
each doing in their own way.

The line to land: concurrency is a number you set in config. Partitions are
a number you provision, in a topic you cannot shrink. Stop paying for the
second when you wanted the first.

If asked "what if one key is enormous" — fair, a single hot key is still
serialised, because it has to be. Per-key ordering is the contract. What you
have bought is that every OTHER key stops waiting behind it.


---

## Offset bookkeeping

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

## Three parallel consuming libraries to consider

<table class="small">
    <tr><th>Library</th><th>Shape</th><th>Worth knowing</th></tr>
    <tr>
      <td class="mono lime">parallel-consumer<br><span class="tiny mute">github.com/astubbs</span></td>
      <td>Java, wraps the vanilla consumer</td>
      <td>Confluent deprecated the original; Antony Stubbs, one of its original implementers, forked it and is actively maintaining it</td>
    </tr>
    <tr>
      <td class="mono lime">kpipe<br><span class="tiny mute">github.com/eschizoid</span></td>
      <td>Java virtual threads over the vanilla consumer</td>
      <td>Newer and smaller. I have not run it in anger — evaluate before you depend on it</td>
    </tr>
    <tr>
      <td class="mono lime">llingr-demux<br><span class="tiny mute">llingr.io</span></td>
      <td>Go core; Java/Kotlin/Scala bindings, Rust FFI, gRPC sidecar</td>
      <td>Per-key routing to workers with contiguous offset commit. Marked patent pending and the license isn't published — check that before adopting</td>
    </tr>
  </table>

Performance figures on these projects are the maintainers' own. Benchmark against your workload.
<!-- .element: class="tiny mute pad-top" -->

Note:
Be scrupulously fair here. I'm recommending a category, not a vendor. The
llingr licensing caveat is real and I should say it out loud rather than
bury it — an unlicensed dependency is a non-starter at most of the
companies in this room.

If asked which I'd start with: the astubbs fork, because it's Apache 2.0,
it's battle-tested, and the maintainer wrote the original.

---

## Decision tree

<figure>
    <img src="assets/diagrams/decision-tree.svg" alt="Two-level decision tree. Do you need key-based ordering? Yes leads to Parallel Consumer in KEY mode. No leads to a second question: do you need per-message acknowledgement? Yes leads to Share groups, KIP-932. No leads back to Parallel Consumer in UNORDERED mode.">
  </figure>

Note:
Screenshot slide. Pause on it.

Walk both questions out loud. Key-based ordering? Parallel Consumer, KEY
mode, done. No ordering requirement? Then the question is not "how fast"
but "do I need per-message ack" — and that is the one thing Parallel
Consumer cannot give you, because Kafka commits offsets in batches.

So share groups are the answer to a narrow question, not a general
replacement. If you do not need per-message ack, UNORDERED mode already
does the job with the library you are probably going to adopt anyway.

Two of the three leaves are the same library. That is the point of the
shape, and it is worth saying out loud.

Then tie it back to Act 1: "add more partitions" is not an answer to
either question. It never was. It was just the only lever in reach.

---

<!-- .slide: class="center-slide" -->

## This should be in Apache Kafka

Key-level parallelism belongs in <code>org.apache.kafka.clients.consumer</code>, not in a third-party library you have to know exists.
<!-- .element: class="pad-top mute" -->

Somebody proposed roughly this in <strong>2019</strong> — KIP-X, "a cooperative consumer processing semantic". It went nowhere.
<!-- .element: class="pad-top small fragment" -->

Partition-level parallelism is a poor default for event-driven systems, and an actively bad one for anything calling a model.
<!-- .element: class="pad-top small mute fragment" -->

Note:
Say this as an ask to the community, not a complaint. There are Kafka
committers in this room and at this conference. That's the point of saying
it here rather than on a blog.
