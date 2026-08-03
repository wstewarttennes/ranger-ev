# Ranger EV → openpilot `carState` — custom spec

The mapping from the Ranger's real CAN signals (Hyper9 X1 + Thunderstruck MCU)
onto openpilot's `structs.CarState`. This is the source of truth for
`carstate.py`. Every row is grounded in `ranger-dashboard/dbc/*.dbc` and
`ranger-dashboard/src/state/vehicle.py`.

Buses (from `ranger-dashboard/config.yaml`):
- **can0** — Thunderstruck MCU/BMS + TSM2500 charger, 250k (ZEVCCS, `0x351/0x355/0x356/...`)
- **can1** — X1 / Hyper9 motor bus, 250k (CANopen TPDOs `0x181/0x182/0x183/0x184/...`)

In the port these become openpilot bus indices: **Hyper9 = bus 0**, **MCU = bus 1**.
(openpilot bus numbering is per-port; we pick it, panda routes it.)

---

## Drive signals openpilot NEEDS (populate these)

| carState field | source msg (id) | signal | transform | status |
|---|---|---|---|---|
| `vEgo`, `vEgoRaw` | HYPER9_STATUS `0x181` | `VEHICLE_SPEED` (km/h, signed ×0.1) | `abs(kmh) / 3.6` → m/s | ✅ have it |
| `wheelSpeeds.{fl,fr,rl,rr}` | — | — | all four = `vEgoRaw` (no per-wheel sensors yet) | ⚠️ faked |
| `standstill` | derived | — | `vEgoRaw < 0.1` | ✅ |
| `gas` | HYPER9_MOTOR `0x183` | `THROTTLE_REQUEST` (−100..100 %) | `clip(req,0,100)/100` → 0..1 | ✅ |
| `gasPressed` | derived | — | `gas > 1e-3` | ✅ |
| `brakePressed` | HYPER9_STATUS `0x181` | `SYSTEM_FLAGS` bit5 (`FLAG_PEDAL_BRAKE`) | bool | ✅ |
| `gearShifter` | HYPER9_MOTOR `0x183` | `MOTOR_RPM` (signed) + park-brake flag | rpm>20→drive, <−20→reverse, else neutral; `FLAG_PARK_BRAKE`→park | ✅ (RPM sign — firmware F/R flags are frozen, see vehicle.py note) |
| `steeringAngleDeg` | — | — | **0.0** until SAS added | ❌ needs sensor |
| `steeringRateDeg` | — | — | **0.0** | ❌ |
| `steeringTorque` | — | — | **0.0** (no EPS) | ❌ |
| `steeringPressed` | — | — | **False** | ❌ |
| `cruiseState.available` | — | — | `False` for now (no stalk/buttons mapped) | ⏳ phase 3 |
| `cruiseState.enabled` | — | — | `False` | ⏳ |
| `espDisabled` | — | — | `False` | — |
| `doorOpen`, `seatbeltUnlatched` | — | — | `False` (no sensors) | — |

### Notes on the gaps
- **Steering** is zeroed everywhere. openpilot will happily build a full
  `carState` and fingerprint the truck with these at 0 — it just can't steer.
  That's exactly phase 1 (read-only). Steering angle sensor is the first thing
  to add for phase-1.5 so lateral has feedback later.
- **wheelSpeeds** faked from vEgo is fine for read-only + longitudinal. Lateral
  tuning eventually wants real per-wheel — add later.

---

## EV / diagnostic signals openpilot does NOT model (expose out-of-band)

openpilot's `carState` has no pack-voltage / SoC / motor-temp fields — that's
what your FastAPI dashboard is for. These stay on the dashboard + MQTT; the port
does NOT need them. Listed here so we don't lose them:

| signal | source | already shown by |
|---|---|---|
| `BATTERY_SOC` | `0x181` / MCU `0x355` | dashboard SoC gauge |
| `DC_BUS_VOLTAGE/CURRENT`, `power_kw` | HYPER9_POWER `0x182` | dashboard power gauge |
| `MOTOR_TEMP`, `INVERTER_TEMP` | HYPER9_MOTOR `0x183` | dashboard temps |
| pack V / I / temp, cell min/max | MCU `0x356` etc. | dashboard + Home Assistant |
| fault levels + system flags | `0x181` / MCU `0x35a` | dashboard diagnostics |

If we later want these *inside* openpilot (e.g. show SoC on the comma UI or gate
engagement on pack faults), the clean path is a couple of custom fields on a
forked `carState` or a side cereal message — decide in phase 2.

---

## Actuation targets (phase 3+ — carController, NOT phase 1)

For when we command the truck. All zeroed / disabled in phase 1.

| openpilot output | Ranger target | how |
|---|---|---|
| longitudinal `accel` | Hyper9 torque | map accel setpoint → `MOTOR_TORQUE` command RPDO to X1 |
| lateral `steer` (torque) | retrofit EPS | drive EPS motor over CAN (donor column) — hardware TBD |
| `brake` authority | regen (+ friction later) | negative torque / regen command; measure regen decel ceiling first |

**panda safety**: none of the above actuates until a `safety_ranger.h` hook
exists in panda firmware enforcing per-message limits. Phase 1 runs a read-only
safety mode (SILENT/NOOUTPUT) — logs everything, sends nothing.
