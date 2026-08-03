# Electric Power Steering (EHPS) Install — 1986 Ford Ranger EV

**Pump:** oyosamnoa EHPS unit for 2013–2018 Nissan Altima (L33 chassis)
Replaces OEM 49110-3TA0B / 49110-3TA5E / 49110-3TA6E / 49110-3TA7B; aftermarket 86-03148R.
Integrated motor + controller ("brains" inside the pump housing).

> **Do this first:** bench-test the pump on a table before plumbing it into the truck.
> The electrical behavior (whether it runs without a CAN signal) is the big unknown, and
> you don't want to discover it after everything is mounted.

---

## 1. Electrical — the two plugs

The two male plugs on the pump are almost certainly:

- **High-current power connector (2-pin, heavy):** battery **+** and battery **−** for the motor.
  - Pulls ~**40–80 A** at peak (lock-to-lock). Use **8 AWG or heavier**.
  - Its own fused feed: **60–80 A fuse or breaker** straight off 12 V.
  - Solid chassis/battery ground.
  - **Do NOT switch this line** — switch the signal side instead.
- **Low-current signal connector (smaller):** ignition/"wake" 12 V, plus **CAN-High / CAN-Low**.
  - This connector decides whether the pump spins at all.

### The gotcha to resolve on the bench
Some of these Nissan EHPS units run at a **fixed default assist level** when they see power +
ignition and **no** valid CAN (limp-home mode) — perfect for a conversion. Others sit **faulted**
and refuse to spin without a CAN speed signal. Unknown which camp this exact unit is in until tested.

**Bench test:**
1. Big **+** and **−** to a 12 V battery through a fuse.
2. Switched 12 V to the ignition/enable pin on the signal connector.
3. Ground the signal-connector ground.
4. Crack the two hydraulic ports and see if it runs / builds suction.
   *(Never run it fully dry more than a second or two.)*

- **Runs → done.** Ignore CAN entirely.
- **Won't run → feed it CAN.** A ~$30–50 Arduino/Teensy + MCP2515 CAN board broadcasting a fake
  "vehicle speed = X" frame is the standard fix (and lets you dial assist up/down). The truck's
  existing CAN/Pi rig can do this too.

### Sourcing the female connectors (we only have the male plugs on the pump)
1. **Junkyard pigtail (recommended):** cut both connectors + ~8" of wire off any 2013–2018 Altima
   at a pull-a-part. Gives exact mating halves + factory wire colors to settle the pinout.
2. **Order by housing ID:** close-up photos of each male plug + any molded numbers, match on
   Corsa Technic / Ballenger Motorsports / OEM Sumitomo–Yazaki catalogs.

---

## 2. Hydraulic — the two ports

Ports per the listing: **10 mm (hose-clamp)** and **11 mm (O-ring)**.

- **10 mm clamp = suction / low-pressure feed** (from reservoir)
- **11 mm O-ring = pressure outlet** (to steering gear)

**This pump does not close its own loop** (only two ports). The gear's return fluid must go to a
**reservoir**, and the reservoir feeds the pump suction.

```
Reservoir ──(LP hose, clamp)──▶ Pump SUCTION (10mm)
Pump PRESSURE (11mm O-ring) ──(HP hose)──▶ Ranger gear PRESSURE port
Ranger gear RETURN port ──(LP hose, clamp)──▶ Reservoir
```

- If the pump came with **no reservoir**, add one (any remote PS reservoir — Saginaw/aftermarket can).
- **Mount the reservoir higher than the pump** so it gravity-primes the suction.

### Adapting to the Ranger gear
- **Pressure line:** custom high-pressure hose — see DIY section below.
- **Return / suction lines:** low pressure — standard **5/16" or 3/8" PS return hose + worm clamps**.
  Use PS-fluid/heat-rated hose (not fuel line).

### Don't-skip
- **Flush** the Ranger gear + lines before connecting (metal shavings kill new pumps).
- **Fluid:** use a PS fluid the Nissan pump is happy with (good PSF or PS-rated ATF). Don't mix types (foaming).
- **Bleed:** wheels off ground, turn lock-to-lock 10–20× to purge air.
- **Pressure/flow mismatch:** pump relief is set for an Altima rack. Usually fine; if steering feels
  twitchy/over-assisted or the pump keeps bypassing through relief, add a flow restrictor.

---

## 3. DIY high-pressure hose

**Hard rule:** the pressure side is **NOT** push-lock hose or barb-and-clamp. Relief spikes to
**~1,200–1,500 PSI** at lock; push-on/clamp hose tops out at ~250–350 PSI. Clamps = return line only.

### Option A — AN braided hose + reusable AN ends (preferred, no crimper)
- **Hose:** `-6AN` power-steering/hydraulic hose, 1500+ PSI (braided stainless PTFE, or nylon-braid
  CPE — Earl's, Fragola, Russell, Aeroquip). -6 is correct for PS pressure flow.
- **Ends:** `-6AN` **reusable / field-attachable swivel hose ends** — screw together in a vise with
  two wrenches, no crimper. Cut hose square (tape + cutoff wheel), push socket on, thread nipple in.
- Everything downstream becomes standard -6AN.

### Option B — Field-attachable hydraulic ends
Real hydraulic hose (Parker 387 / Gates) + reusable screw-together hydraulic ends. Bulkier, fussier
end selection. Only if you already have hydraulic fittings around. Otherwise use Option A.

### The two ends are the whole game — CONFIRM BOTH PORTS BEFORE BUYING
- **Pump outlet ("11 mm O-ring"):** likely the OEM hose slips over an 11 mm spigot + O-ring + retainer
  (NOT a threaded port). Best fix: **buy the OEM Nissan Altima high-pressure line** for this pump (it
  mates the spigot correctly), then cut the *far* end and fit your -6AN end / adapter there. If the
  port is actually an **SAE O-ring boss (straight thread)**, an **ORB-to-AN adapter** screws in.
- **Ranger gear pressure port:** first-gen Ranger inlets are typically **5/8-18 inverted flare** or a
  **metric O-ring boss (~16–18 mm)**. Off-the-shelf **inverted-flare-to-AN** and **metric-ORB-to-AN**
  adapters exist for this.

### Safety
- **Min bend radius:** gentle sweep near fittings; route away from heat/moving parts.
- **Pressure-test before driving:** system full, pump running, lock-to-lock, watch every joint for
  weeping. Reusable ends back off if under-tightened — snug, then verify dry.
- **Secure the hose** so it can't chafe (pinhole at 1,200 PSI atomizes fluid).

---

## OPEN TODOs before ordering parts
- [ ] Bench-test pump: does it run without CAN? (decides whether we build a fake-speed CAN sender)
- [ ] Photograph + measure the **two male electrical plugs** → ID connector housings / pin counts
- [ ] Photograph + caliper-measure the **pump 11 mm outlet** → spigot vs. threaded ORB?
- [ ] Photograph + measure the **Ranger gear pressure + return ports** → thread type
- [ ] Confirm reservoir: did pump include one? If not, source remote reservoir (mount high)
- [ ] Then: finalize -6AN hose length + 2 reusable ends + 2 adapter fittings shopping list
