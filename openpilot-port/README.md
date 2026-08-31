# Ranger EV — openpilot port

A custom openpilot **car port** for the 1986 Ford Ranger EV conversion
(Hyper9 X1 motor controller + Thunderstruck MCU/BMS). Built from the truck's
real CAN signals — see `spec/ranger_carstate_spec.md` and the DBCs in
`ranger-dashboard/dbc/`.

## Where this is going (the reality ladder)

openpilot does two jobs: **steer** and **control speed**. For this truck:

| phase | goal | status |
|---|---|---|
| **1. read-only** | openpilot *sees* the car — `carState` from CAN | **this scaffold** |
| **2. longitudinal** | control speed via Hyper9 torque / regen | not started |
| **3. lateral (steer)** | steer the truck | ⛔ **blocked: no EPS** (manual/hydraulic steering) |

Full hands-off openpilot needs a **steering actuator (EPS) retrofit** the truck
doesn't have — that's a separate hardware project. Everything up to
**longitudinal** is reachable without it.

## Files (`opendbc/ranger/`)

| file | role |
|---|---|
| `values.py` | platform (`CAR.RANGER_EV`), `CarSpecs`, `dbc_dict`, `CarControllerParams` (inert in phase 1) |
| `fingerprints.py` | arbitration-ID fingerprint (`FINGERPRINTS`) + `FW_VERSIONS` (empty — no UDS ECUs) |
| `carstate.py` | CAN → `structs.CarState` (vEgo, gas, gear, brake). Steering zeroed. |
| `carcontroller.py` | **no-op** in phase 1 (read-only). Hyper9 torque lands in phase 2. |
| `radar_interface.py` | stub — no radar, vision-only |
| `interface.py` | `CarInterface._get_params` — SILENT safety + `dashcamOnly` (read-only) |
| `ranger_ev.dbc` | drive-relevant subset of the two DBCs, arranged for the parser |

## What's mapped vs missing

**Mapped (from real signals):** `vEgo`, `gas` (throttle), `brakePressed`,
`gearShifter` (D/R/N from signed `MOTOR_RPM`), standstill.
**Zeroed / missing:** all steering (no sensor, no EPS), cruise (no stalk mapped),
radar. EV data (SoC, pack V/I, temps) openpilot doesn't model — stays on the
dashboard + Home Assistant.

**Two known issues to fix before phase 2** (both in the spec):
- **`vEgo` is gear-dependent** — the X1 speed is `rpm × fixed ratio`, only right
  in one gear (~3rd; ~half in 4th). Replace with **comma GPS or a tailshaft VSS**.
- **`CarSpecs`** (mass / wheelbase / steerRatio) are placeholders — **measure them**.

## ⚠️ VERSION PIN — read before installing

The opendbc car API changed in the 2024 standalone split, and signatures/field
names drift between revisions. Pin against the opendbc on **your comma** first:

```bash
OP=$(python3 -c "import opendbc,os;print(os.path.dirname(opendbc.__file__))")
echo "$OP"
ls "$OP/car/"                      # confirm structs.py, interfaces.py
sed -n '1,80p' "$OP/car/body/interface.py"   # a tiny real port to mirror
grep -n "_get_params\|def update" "$OP/car/interfaces.py"
```

Each source file lists the specific things that move (e.g. `ret.brand` vs
`ret.carName`, `SafetyModel.silent` vs `noOutput`, the `update()` signatures).
Adapt those, then drop `opendbc/ranger/` into `$OP/car/ranger/`.

## Install (phase 1, read-only) — the short version

1. **Foundation:** comma dev-mode + SSH; plug CAN into the comma; set the panda
   bus to **250k** (the Ranger bus is 250k, panda defaults to 500k); confirm the
   comma sees `0x181` / `0x183`.
2. **Pin + drop in:** run the version-pin checks above; copy `opendbc/ranger/`
   into the comma's opendbc `car/ranger/`.
3. **Fingerprint:** with the bus live, openpilot should match `FINGERPRINTS` and
   populate `carState` — openpilot now "sees" the truck. Safety stays **SILENT**
   (logs everything, sends nothing).

Phase 2 (longitudinal) requires a `safety_ranger.h` panda hook + real
`CarControllerParams` + a lot of bench/driveway testing — not before phase 1 is
solid and `vEgo` is on a gear-independent source.
