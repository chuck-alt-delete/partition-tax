<!-- Prevent — 4 slide(s). "---" starts a new slide (Down). -->

<!-- .slide: class="center-slide" data-state="act" -->

<p class="kicker">Layer one</p>

# Prevent

<div class="spine" data-act="1"></div>

Stop making new waste
<!-- .element: class="mute pad-top" -->

---

## The trap this layer walks into

<div class="cols pad-top">
    <div class="panel bad">
      <h4>Review every topic</h4>
      <p>You become a ticket queue. Teams route around you, or ship late and resent you for it. Neither outcome survives contact with a deadline.</p>
    </div>
    <div class="panel good">
      <h4>Encode the rule once</h4>
      <p>The policy <em>is</em> the review. Teams self-serve at full speed inside a boundary you set, and you are not in the loop.</p>
    </div>
  </div>

<strong>If prevention costs the platform team a meeting per topic, it will not happen.</strong>
<!-- .element: class="pad-top fragment" -->

Note:
Every platform engineer in the room has lived the left-hand box. Name it
plainly and they'll trust the rest.

---

## Guardrails at creation time

<pre><code data-trim data-noescape class="language-yaml">apiVersion: self-serve/v1
kind: ResourcePolicy
metadata:
  name: partition-budget
spec:
  targetKind: Topic
  description: "Partitions get justified, not inherited"
  rules:
    - condition: spec.partitions &lt;= 6
      errorMessage: "More than 6 partitions needs a measured throughput number"
    - condition: metadata.labels.owner != ""
      errorMessage: "Every topic has a named owner"</code></pre>

Three properties that matter more than the syntax: it runs at creation, it fails with a <em>reason</em>, and it lives in git next to everything else.
<!-- .element: class="small mute" -->

Note:
This is Conduktor's self-service policy format because that's what I use
with customers, but the shape is the point, not the vendor. If you're
building this yourself with an admission controller or a Terraform policy
module, same three properties.

The error message is doing real work. "Denied" makes people open a ticket.
"Needs a measured throughput number" makes them go measure.

---

## Change the default, not just the ceiling

<div class="cols">
    <div class="panel bad">
      <h4>Template starts at 30</h4>
      <p>Every copy-pasted topic inherits 30 partitions forever. Nobody chose 30. Somebody chose it once, in 2019, for a different topic.</p>
    </div>
    <div class="panel good">
      <h4>Template starts at 1</h4>
      <p>Going up requires a sentence of justification. Most topics never need one.</p>
    </div>
  </div>

<strong>The ceiling stops the worst case. The default decides the median.</strong>
<!-- .element: class="pad-top fragment" -->

Note:
Most of the waste I find isn't a team gaming the limit. It's a template
default nobody has looked at in years, multiplied by a thousand topics.
Fixing the default is the single highest-leverage hour in this entire talk.
