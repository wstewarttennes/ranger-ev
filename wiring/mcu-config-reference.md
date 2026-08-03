# Thunderstruck MCU — Config Reference (verify-then-set)

For the Ranger build: 36S Tesla NMC, 2× BMSS18 (LTC18), TSM2500 charger, OUT5→relay→X1 interlock.
Connect via PuTTY (115200 8-N-1). **Always check the current value first, then only `set` what's off.**

## How to SEE current values (do this first, per context)
`show config` is **context-dependent** — run it in each context to see that context's settings.

| Command | Where | Shows |
|---|---|---|
| `show config` | each context | current settings for that context |
| `show cells` | bms | live cell voltages C1..Cn |
| `show thermistor` | bms | thermistor temps + enabled state |
| `sh cmap` | bms | cell map; dots = detected, X = locked |
| `show out` | sys | output states + assigned functions |

Workflow: `mcu` → `show config`; `bms` → `show config` + `show cells` + `show thermistor` + `sh cmap`;
`sys` → `show config` + `show out`. Compare to the tables below; set only mismatches.

---

## MCU context (`mcu`)
| Setting | Meaning | Target (this build) | Check | Set |
|---|---|---|---|---|
| arch | BMS architecture | **ltc18** | `show config` | `set arch ltc18` |
| in1 / in2 | current-sensor inputs | **hall1 / hall2** ✅ already | `show config` | (already set) |
| can1br | CAN1 baud | **250** ✅ (charger bus) | `show config` | `set can1br 250` |
| can2br | CAN2 baud | 500 (confirm what's on it) | `show config` | `set can2br 500` |
| services | obcharge/canopen | **obcharge can1** ✅ | `show config` | — |

## BMS context (`bms`)
⚠️ **FOUND 2026-06-30: voltage cutoffs were set for LFP, not NMC** (hvc 3.4 / lvc 2.4). These are
WRONG for Tesla NMC and hvc 3.4 caused a live HVC fault (cells at 3.61 > 3.4). Corrected to NMC.

| Setting | Meaning | Found | Target (36S NMC) | Set |
|---|---|---|---|---|
| hvc | per-cell HIGH cutoff | ❌ 3.4 (LFP) | **4.2** (4.1 = longevity) | `set hvc 4.2` |
| lvc | per-cell LOW cutoff | ❌ 2.4 (too low) | **3.0** | `set lvc 3.0` |
| hvcc | HVC clear threshold | check | ~4.15 | `set hvcc 4.15` |
| lvcc | LVC clear threshold | check | ~3.1 | `set lvcc 3.1` |
| hipackv | pack HIGH threshold | check | **155** (above full ~151V) | `set hipackv 155` |
| lowpackv | pack LOW threshold | check | **100** (below empty ~108V) | `set lowpackv 100` |
| bvmin | balance start voltage | 3.00 | **3.9** (balance near top) | `set bvmin 3.9` |
| thmax | over-temp limit | 50 ✅ ok | 50–55 | `set thmax 55` (optional) |
| thmin | under-temp limit | 0 ✅ ok | **0** | (already correct) |
| thermistors | enable temp sensors | enabled | **all 6 enabled** | `enable thermistor all` |
| cell lock | configure cell census | — | **locked (X)** | `lock` |

## SYS context (`sys`)
| Setting | Meaning | Target | Check | Set |
|---|---|---|---|---|
| out5 | BMS-OK → interlock | active when no faults | `show out` | `set out5 -(hvc lvc hipack lowpack hitemp lowtemp notlocked)` |

*(Cold-weather driving: omit `lowtemp` from the OUT5 list — charging stays temp-protected automatically.)*

---

## EVCC context (`evcc`) — CHARGING setup (required before first charge)
⚠️ Default `maxv` ships at **20.0V** (placeholder) — MUST set to pack voltage or charging fails/is unsafe.
Manual: "responsibility of the user to configure charge parameters appropriate for the pack."

| Setting | Meaning | Target (36S NMC + TSM2500 + J1772) | Set |
|---|---|---|---|
| plug | charge plug protocol | **J1772** (Type 1, US) | `set plug J1772` |
| charger | charger type | **tsm2500** | `set charger tsm2500` |
| maxv | **max charge voltage** | **151** (4.2V/cell full) or 147.6 (4.1V longevity) | `set maxv 151` |
| maxc | **max charge current** | **15** (TSM2500 max out) | `set maxc 15` |
| termc | termination current (finish) | **2** (1–20A range) | `set termc 2` |
| termt | max charge time (hr, safety) | **12** | `set termt 12` |
| linec | available line current | **J1772** (from pilot; protects outlet) | `set linec J1772` |
| options | pack balancing | topbalance (optional) | `set options topbalance` |

Already set/verified: `obcharge can1` ✅, `hvc 4.2` (bms, per-cell backstop) ✅, prox/pilot→MCU Conn C ✅.
Charge target current = min(maxc, line-current-derived). Charge stops on: termc reached, any cell hvc (4.2V),
plug removed, CAN lost, or termt reached. Verify: `evcc`→`show config`; `show inputs` (prox/pilot).
Output funcs: `charge` (charging), `plugin` (plugged in) — mappable to a light/gauge.

## Verify-then-set procedure
1. `mcu` → `show config` — confirm `arch ltc18`, can1br 250.
2. `bms` → `show config` — note current hvc/lvc/hipackv/lowpackv/thmax/thmin; `set` only mismatches.
3. `bms` → `show cells` (all healthy), `show thermistor` (6 reading ~ambient).
4. `bms` → `sh cmap` (dots) → `lock` → `sh cmap` (X). Do this AFTER cells + thermistors confirmed.
5. `sys` → `show out` → set out5 if not already → `show out` (OUT5 should be active).
6. Confirm no unexpected active faults.

## Pass = OUT5 active
With cells healthy + locked + temps OK + pack in range, OUT5 goes active → relay clicks → X1
interlock enabled. If OUT5 stays off, run `show` to find which condition is still true (usually
`lowpack`/`hipack` thresholds, or a thermistor).
