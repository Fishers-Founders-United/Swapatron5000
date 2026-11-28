# Battery safety summary

This page is for the electrical side of a Swapatron: the sensor node, the light, and any
USB charging shelf. It is deliberately conservative. A shared box sits outdoors, is opened
by strangers, and is looked after by volunteers who did not build it, so the battery has to
be safe when nobody is thinking about it.

Nothing here is a final decision. Read it as a starting point for the power budget
(issue #103) and the sensor node design (issue #104), and correct anything that is wrong.

## 1. Pick a chemistry that fails boringly

| Option | Why we would | Why we would not |
|---|---|---|
| **LiFePO4, 12.8 V** (recommended default) | Very hard to make catch fire, 2000+ cycles, flat voltage curve, works from -20 to 60 C when discharging | Heavier and dearer than li-ion; **must not be charged below 0 C** |
| **Protected 18650 / 21700 li-ion pack** | Small and cheap per Wh | Highest energy density means highest consequence when something goes wrong; needs a real BMS, not a "protection circuit board" from a marketplace |
| **Sealed lead acid (SLA)** | Cheapest, dumbest, most forgiving charger | Killed by deep discharge; heavy; poor cold performance |
| **USB power bank** | Zero build risk, replaceable in seconds | Contains the same li-ion cells with no temperature control; a hot box in summer will swell it |

Whichever we choose: **one chemistry per box**. Never mix chemistries behind the same
charger, and never mix old and new cells in a pack.

## 2. Size it from the load, not from a guess

```
Wh needed = (daily Wh × days of no sun × 1.3 inverter/ageing loss) / usable depth of discharge
```

Use 0.8 for LiFePO4, 0.5 for SLA, 0.8 for li-ion with a BMS.

Worked example for the current sketch (sensor node 1.5 W average + light 3 W for 8 h):

- daily = 1.5 × 24 + 3 × 8 = 60 Wh
- three days without sun, 1.3 loss, DoD 0.8 → 60 × 3 × 1.3 / 0.8 = **293 Wh ≈ 23 Ah at 12.8 V**

Round up to a standard size, then check the panel can carry it: panel watts should be at
least daily Wh ÷ 3 (≈ 20 W here, more if the box is shaded in winter).

## 3. Charging and protection

- Charge at **0.2–0.3 C** at most. Faster charging buys nothing here and costs cell life.
- **Stop charging below 0 C** for LiFePO4 and li-ion. This is not optional; it is how cells
  get destroyed. Use a charge controller with a low-temperature cut-off, or a thermistor
  on the pack, rather than trusting the weather.
- Every pack needs: a BMS or a controller with over/under-voltage and over-current
  protection, a **fuse within 150 mm of the positive terminal**, and a master switch or
  breaker that a volunteer can reach without tools.
- Size cable for the fuse, not for the load. 2.5 mm² for 10 A, 4 mm² for 20 A, and keep
  runs under two metres.
- Solar input goes through a controller — never straight onto the pack.
- Label the pack with chemistry, nominal voltage, capacity, installation date, and the
  fuse rating, in marker on the case. Volunteers change; labels do not.

## 4. Where it lives inside the box

- **Not in the food compartment.** Put the battery in its own bay with a lid, so a spill,
  a leak, or a dropped jar does not reach it.
- Ventilated to the outside, but not open to rain. A small louvre or a gore vent is enough.
- **At least 300 mm from anything that gets hot**, and out of direct summer sun if the box
  is metal.
- On a metal or fire-resistant tray, not on bare wood or foam.
- Above the floor of the box, on a shelf or stand, so standing water cannot reach it.
- If the box is opened by the public, the battery bay should need a tool or a key — not
  because the battery is dangerous when handled properly, but because a loose pack with
  exposed terminals in a bag of metal objects is.

## 5. Checks a volunteer can actually do

- **Monthly, 2 minutes:** read the pack voltage, look for swelling, smell, corrosion on the
  terminals, and anything that has moved. Log it in the box check.
- **Quarterly:** capacity test (discharge at a known load, time it) and compare with the
  rating. Below 70 % of rated capacity, plan a replacement.
- **Immediately off-line:** swelling, heat with no load, a sweet or solvent smell,
  discoloured terminals, or a charger that will not stop. Isolate it outdoors, on concrete,
  away from the box, and tell a maintainer the same day.

## 6. Things we will not do

- No bare, unprotected cells anywhere in the build.
- No soldering directly to cell terminals; use spot-welded tabs or a proper holder.
- No charging below 0 C, and no charging a frozen pack "just to warm it up".
- No car starter batteries, no mixed packs, no salvaged laptop cells for the public unit.
- No battery work by one person alone on build day. Two people, one of them reading this
  page out loud.

## 7. Open questions for whoever reviews this

1. Does the first site have mains power, and if so, is a battery at all the right answer, or
   should the node run on a sealed 5 V supply with a small UPS only for the light?
2. What is the real winter minimum inside the box? That number decides LiFePO4 versus SLA.
3. Who signs off on the electrical build, and what does that person need to see to be
   comfortable — a wiring diagram, photos, a test log?
4. If the box is moved or re-sited, who is responsible for re-checking the panel shading
   and the battery temperature?

*Written as a first draft for bounty #99. It needs a read from someone who has actually
built battery systems — especially on the low-temperature charging rule and on fuse
placement — before it should be treated as the project's position.*
