<!-- Clean — 3 slide(s). "---" starts a new slide (Down). -->

<!-- .slide: class="center-slide" data-state="act" -->

<p class="kicker">Layer two</p>

# Clean

<div class="spine" data-act="2"></div>

Deal with the waste you already have
<!-- .element: class="mute pad-top" -->

---

## You cannot clean what you cannot attribute

One shared cluster. One line on the cloud bill. Forty teams.
<!-- .element: class="pad-top" -->

<div class="cols pad-top">
    <div class="panel bad">
      <h4>Cloud tags</h4>
      <p>Tags stop at the resource boundary. The cluster is one resource. There is no tag that says which team's topics are holding those replicas.</p>
    </div>
    <div class="panel good">
      <h4>Kafka-level allocation</h4>
      <p>Attribute partition-hours, bytes and storage to the application that owns the topic. This is the only layer where the question is answerable.</p>
    </div>
  </div>

This is why FinOps teams stall on Kafka specifically. Their entire toolchain works at the resource boundary, and Kafka hides forty tenants behind one.
<!-- .element: class="pad-top fragment small mute" -->

Note:
If there are FinOps people in the room this is the slide they photograph.
It explains a frustration they've had for two years and couldn't articulate.

---

## Show each team their own number

Not the cluster's waste. <em>Theirs.</em> With their name on it.
<!-- .element: class="pad-top" -->

<ul class="pad-top">
    <li class="fragment">Partition-hours by application, not by cluster</li>
    <li class="fragment">Trended, so growth is visible before it's structural</li>
    <li class="fragment">Delivered where budget conversations already happen</li>
  </ul>

<strong>Most teams clean up without being asked.</strong>
<!-- .element: class="pad-top fragment" -->

The ones that don't now have a number attached to them, which is a different and much easier conversation to have.
<!-- .element: class="small mute fragment" -->

Note:
Be honest about the mechanism: this works because of embarrassment and
budget, not because of dashboards. A team that can see its own line item
next to its peers' will act. A team looking at a cluster-wide number will
not, because it isn't theirs.

I've watched this recover more partitions than any technical fix in this
talk, and it requires no engineering at all.
