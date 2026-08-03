# AC Build + Shopping List — 1986 Ford Ranger EV

Full from-scratch R134a air conditioning, controlled by the Raspberry Pi dashboard.
Nothing was kept from the factory AC. Cabin has **dash vents + ducting but no blower motor**.

## Design constraints (these drive every choice)
- Refrigerant: **R134a**.
- Traction pack: **36S, ~133 V nominal** (108 V empty → 151 V full).
- 12 V bus is **weak**: DC-DC is 13.8 V / 50 A (~690 W), already loaded by the EHPS steering pump.
- All control via the existing Pi FastAPI/CAN touchscreen dashboard (add an HVAC screen).

## How AC actually works (mental model)
Cold is made *in* the airflow, not piped in:
`[ blower fan ] → [ evaporator core ] → [ dash vents ]`
The evaporator + a blower must sit in the duct feeding the vents. You cannot "plug cold into a vent."

## Cabin side — reuse the dash vents
Have vents + ducting, missing the blower. Two paths:
- **Factory HVAC case still there:** new blower motor + universal evaporator core into the case → factory vents.
- **Case gone / ducts only (default assumption):** universal under-dash evaporator unit (blower built in),
  ducted into the existing dash vents. One part, its own blower.
Add an **evaporator coil temp sensor** for the Pi's anti-ice logic.

---

## SHOPPING LIST (all real/in-stock as of 2026-07; Amazon prices are typical street, confirm at checkout)

### 1. Electric AC compressor — THE critical part
Want a **144 V-nominal DC compressor** (input ~101–180 V brackets the 108–151 V pack) → runs directly
off the traction pack, spares the 12 V bus. Prefer PWM/CAN control for the Pi.

| Item | Source | ~Price | Link | Voltage / Control |
|---|---|---|---|---|
| **Inductive Autoworks 144 V kit** (best value) | inductiveauto.com | **$600–760** | https://inductiveauto.com/product/electric-ac-compressor-kit-96-144-312v/ | 101–180 V DC; **3-speed / PWM / CAN**; isolated bracket + connectors + fittings |
| **Legacy EV CANEV 144 V kit** (turnkey) | legacyev.com | **$1,235** | https://legacyev.com/products/canev-a-c-compressor | 120–144 V nom / 180 V max; incl. control module, contactor, harness, pre-charge, mounts. Confirm control input (CAN/PWM/analog) |
| Guchen GC27A144 (backup) | guchen-eac.com | quote | https://www.guchen-eac.com/what/low-voltage-electric-compressor/gc27a144.html | 110–180 V + 9–16 V logic; PWM 1000–5000 rpm; China-direct |
| Masterflux Sierra03-0982Y3 (LV alt) | Masterflux distributors | ~$70 + controller ($$$) | https://www.masterflux.com/ProductFamily/SIERRA | 24/48 V; needs Masterflux BLDC controller + dedicated 48 V supply. Only if avoiding HV-pack AC |

⚠️ **Do NOT buy a 96 V variant** — ~130 V ceiling < your 151 V full charge.
⚠️ **Tesla / Nissan Leaf salvage compressors = 350–400 V → incompatible. Do not use.**
→ Verify the exact control interface (CAN vs PWM vs analog) + startup lockout/oiling ramp with the vendor
  before buying, so we know what the Pi must emit.

### 2. Under-dash evaporator kit (w/ blower)
| Item | Source | ~Price | Link |
|---|---|---|---|
| Vintage Air 672001-VHY Mark IV underdash, cool-only, 3-speed | Summit / Speedway | $375 | https://www.summitracing.com/parts/vta-672001vhy |
| Coldmaster 432-100 universal underdash, 12V, 12.7k BTU | coldmasterinc.com | quote | https://www.coldmasterinc.com/product-page/a-c-kit-universal-underdash-evaporator-432-1-12v-w-electrical-harness |
| 12V universal under-dash evap kit, 3-speed (budget) | Amazon | ~$120–170 | ASIN B0DXKV45RF |

### 3. Separate 12V blower motor (only if reusing factory heater box)
| Item | Source | ~Price | Link |
|---|---|---|---|
| Red Dot universal blower assy, 12V dual squirrel-cage, 3-speed | acparts.com | $91 | https://www.acparts.com/product/blower-motor-assembly-12v-3/ (P/N 1001076) |
| SPAL BT3-106 12V mini squirrel-cage | btrac.com | $54 | https://btrac.com/product/bt3-106-12v-mini-squirrel-cage-blower/ |

### 4. Condenser + fan
| Item | Source | ~Price | Link |
|---|---|---|---|
| CNFP1620 universal parallel-flow condenser 16"×20", #6/#8 | Amazon | $55 | https://www.amazon.com/CNFP1620-Universal-Condenser-Parallel-ring/dp/B079M24K78 (kit+drier: B07PMTJFK7) |
| 16" slim 12V electric fan | Amazon | ~$30–45 | ASIN B07FNHFFNZ — ⚠️ pick a LOWER-draw fan; 1730 CFM units pull 15–20 A |

### 5. Receiver-drier
| Item | Source | ~Price | Link |
|---|---|---|---|
| UAC RD 8214C universal receiver-drier | Amazon | ~$15 | ASIN B003R4TBDS |
| Universal drier #6 w/ switch+service ports (#21-321) | Amazon | ~$20 | ASIN B00LEUV4F0 |

### 6. Hose + fittings
| Item | Source | ~Price | Link |
|---|---|---|---|
| Cold Hose HK920 universal R134a barrier-hose kit (beadlock) | coldhose.com | $123 | https://coldhose.com/products/universal-r-134a-hose-kit — needs beadlock crimper |
| Gates/Aeroquip EZ-Clip kit (no crimper) | various | varies | (VMACS 10-7-0002 exists but $946 = overkill; find a smaller EZ-Clip kit) |

### 7. Refrigerant + oil (POE/ESTER — NOT PAG)
| Item | Source | ~Price | Link |
|---|---|---|---|
| R-134a 12 oz can (need ~1.5–2 lb total = a few cans) | Walmart | ~$13 ea | https://www.walmart.com/ip/Super-Tech-R-134a-Refrigerant-Can-12-oz/204208343 |
| **Red Dot POE oil for R-134a ELECTRIC compressors** | VMACS | $34 | https://www.vmacs.net/products/compressor-oil-red-dot-poe-for-r-134a-electric-ac-compressors-79r4565 (79R4565) |
| Emkarate RL 68H POE ester oil (1 qt) | eBay industrial | ~$25–35 | = Denso ND-Oil 11; confirm ISO grade per compressor spec |

⚠️ **PAG oil is conductive → destroys HV brushless compressor windings. POE/ester ONLY.**

### 8. Pressure safety switch (hardware failsafe, in series with compressor enable)
| Item | Source | ~Price | Link |
|---|---|---|---|
| 7/16" female binary switch (400 psi hi / 28 psi lo cutoff) | coldhose.com | $10 | https://coldhose.com/products/7-16-female-binary-switch |
| Trinary switch SW-4082-C (adds fan trigger @255 psi) | restomodair.com | $40 | https://restomodair.com/shopproducts/trinary-pressure-switch/ |

### 9. Raspberry Pi control electronics
| Item | Source | ~Price | Link |
|---|---|---|---|
| Adafruit ADS1115 16-bit I2C ADC (Pi has no analog in) | Adafruit | $15 | https://www.adafruit.com/product/1085 (clones ~$8 on Amazon) |
| **30A** MOSFET module for blower PWM (3.3V-trigger) | Amazon | ~$10 | (30A, not 15A — 15A sits at a 15A blower's limit) |
| 5V 8-ch opto-isolated relay board | Amazon | ~$12 | ASIN B00DR9SE4A — for compressor enable / fan / cutoff, NOT the blower PWM |
| High-side pressure transducer 0–500 psi, 0.5–4.5V, 1/8"NPT | Amazon | ~$15 | ASIN B08Y76GVXM |
| Low-side pressure transducer 0–100 psi, 0.5–4.5V, 1/8"NPT | Amazon | ~$15 | ASIN B08Y756B5V |
| NTC 10K 3950 waterproof probes ×2 (cabin + coil) | Amazon | ~$8 ea | ASIN B086812PZC — match 3950 beta in firmware |

### 10. Service tools
| Item | Source | ~Price | Link |
|---|---|---|---|
| Orion Motor Tech vacuum pump + manifold gauge combo, 3.5 CFM | Amazon | ~$110–140 | ASIN B09GVTS8XF (pump+gauges+hoses+couplers) |
| — or separately: Pittsburgh 3 CFM pump / R134a gauge set | Harbor Freight | $140 / $68 | SKU 61176 / SKU 58776 |

---

## Pi control architecture (add an HVAC screen to the FastAPI dashboard)
**Outputs:** compressor speed/enable (CAN or PWM to its controller) · condenser fan (relay) · blower speed (PWM via 30A MOSFET).
**Inputs (via ADS1115):** cabin temp · evaporator coil temp · high-side + low-side pressure.
**Logic:** setpoint vs cabin temp → PID/hysteresis → compressor speed; anti-ice (back off near 0–2 °C coil);
low-pressure lockout + high-pressure cutback.

🚨 **Hardware failsafe:** put the mechanical binary/trinary pressure switch **in series with the compressor
enable line**, independent of the Pi. A software bug or frozen touchscreen must never be able to run the
compressor dry or past max pressure. Pi = smart modulation; the $10 switch = dumb failsafe.

## Install sequence
1. Pick compressor → sets controller + port fittings.
2. Mount compressor (isolated bracket) + condenser/fan up front; install evaporator in cabin, duct to vents.
3. Route/crimp hoses; new receiver-drier; correct expansion valve/orifice.
4. **Flush** any reused parts of PAG; charge system with POE oil.
5. **Pull vacuum** (~30 min, hold to prove no leaks) → **charge R134a by weight**.
6. Wire controller + failsafe switch; add HVAC screen to the Pi; test.

## OPEN TODOs
- [ ] Confirm cabin: factory HVAC case present (→ blower motor + evap core) or ducts only (→ under-dash unit)?
- [ ] Pick compressor (Inductive Autoworks 144V vs Legacy EV CANEV) → confirm control interface w/ vendor
- [ ] Budget the 12 V bus: blower + condenser fan draw vs 690 W DC-DC (already running steering) — size fan small or feed condenser fan off pack
- [ ] Buy 30 A (not 15 A) blower MOSFET
- [ ] Get beadlock crimper access (or choose EZ-Clip hose kit)
