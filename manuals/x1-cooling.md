# Hyper9 X1 Inverter Cooling — 1986 Ford Ranger EV

**Controller:** NetGain Hyper9 X1 inverter, conduction-cooled (no internal liquid loop).
All heat exits the flat aluminum base → thermal grease → the finned heatsink you've bolted on.
**Status:** heatsink attached. Missing piece = airflow + a control trigger. The X1 has the trigger built in.

> **Do this first:** pull the heatsink and check the thermal grease — an even, thin layer across
> the whole X1 base. The manual calls the thermal coupling "essential." Bad/patchy grease reads as a
> false overtemp and derates you for no reason. Fix this before chasing fans.

---

## 1. What the manual actually requires

- **Heatsink operating range:** −40 to +95 °C
- **Derating:** starts at **80 °C**, ramps 100 % → 50 % current by **95 °C**, thermal shutdown at 95 °C
- **Faults:** `AL10` = >80 °C (limiting), `AL8` = >100 °C (blocking)
- **NetGain's suggested fan control:** activate **55 °C** / deactivate **45 °C**

The whole game is keeping the heatsink comfortably under 80 °C under sustained load. On a street
Ranger, a fan across the fins almost certainly does it — liquid is the fallback, not the plan.

---

## 2. The move — fan on the heatsink, switched by the X1 itself

The X1 has a generic digital output you can assign to **Controller Cooling**. It watches its own
heatsink temp and switches the fan. **No Pi needed for this.**

### SmartView setup
`Configure → System → Generic Outputs`
- Function = **Motor and/or Controller Cooling**
- Assign to **Digital Output 1 or 2**
- Activation **55 °C** / deactivation **45 °C**

The output energizes a **relay coil** (relay **not** included). The relay switches 12 V to the fan.

> ⚠️ **Wire the relay BEFORE assigning the output in software.** The X1 faults if an output is
> assigned with no matching load wired to it.

### Wiring
```
X1 Digital Output ──▶ relay coil (85/86)
Switched 12V ──[fuse]──▶ relay common (30)
Relay N.O. (87) ──▶ fan (+)
Fan (−) ──▶ chassis ground
```

### Parts list (tiny)
- **12 V fan** sized to blow across the fins.
  - Axial (puller/pusher) if the fins are open to a clear air path.
  - Squirrel-cage **blower** if the fins are tucked in tight and need forced flow.
  - Fins ideally run vertical-ish so natural convection helps when the fan's off.
- **Automotive relay** (Bosch-style, 30–40 A is overkill-safe) + **inline fuse** on the 12 V feed.
- Switched 12 V source (so the fan can't run with the truck off).

That's a full closed-loop system: X1 reads heatsink temp → kicks the fan on at 55 °C → off at 45 °C.

---

## 3. Prove it before spending more

You already have inverter temp on CAN → it's on the dash. So don't buy liquid parts on spec:

1. Wire the fan + relay, assign the output, set 55/45.
2. **Drive it** — hills, sustained load, hot day. Watch the heatsink temp.
3. **Holds under ~70–75 °C → done forever.** The fan is the whole cooling system.
4. **Heat-soaks past 80 °C and starts derating (`AL10`) → go to the liquid fallback.**

---

## 4. Fallback — liquid loop (only if the fan can't keep up)

Swap the finned heatsink for a liquid cold plate and build a small loop:

- **Aluminum liquid cold plate** bolted to the X1 base (same thermal-grease rule — even, thin layer).
- **12 V pump** (small EV/PC-grade circulation pump).
- **Compact radiator** + **12 V fan** on the radiator.
- **Reservoir**, mounted highest point so it self-primes and you can bleed air.
- 50/50 coolant, standard hose + clamps (low pressure — not brake-line territory).

Reuse the same X1 Controller Cooling output to switch the **pump + radiator fan** on the same
55/45 thresholds. Everything else in section 2 carries over.

---

## OPEN TODOs
- [ ] Pull heatsink, verify even thermal-grease layer on the X1 base
- [ ] Photograph heatsink + fin orientation in the bay → decides axial fan vs. blower
- [ ] Wire relay + fused 12 V feed to the fan
- [ ] SmartView: assign Generic Output → Controller Cooling, 55 °C on / 45 °C off (wire relay FIRST)
- [ ] Shakedown drive watching heatsink temp on the dash — under 75 °C = done
- [ ] Only if it derates past 80 °C: source cold plate + pump + radiator + reservoir for liquid loop
