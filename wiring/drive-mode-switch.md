# Drive-mode switch (3-way) → X1 operating profiles

A 3-position **ON-OFF-ON** toggle selects the X1's three built-in operating
profiles = **regen-on-neutral levels** (single-pedal-driving strength).
Confirmed working 2026-08-28 (inputs toggle Profile 2/3 in SmartView Monitor).

## The switch
Center-off SPDT toggle. Grey = common/pole, orange/brown = the two throws.
- **UP**: grey↔orange closed
- **DOWN**: grey↔brown closed
- **MIDDLE**: open (nothing)

## Wiring → X1 K1 (35-pin Ampseal) — color to color
| Switch wire | X1 harness wire | K1 pin | Selects |
|---|---|---|---|
| **orange** (UP) | **WHT/RED** | K1-18 (Digital In 7) | Profile 2 "S" |
| **brown** (DOWN) | **PURP** | K1-19 (Digital In 8) | Profile 3 "H" |
| **grey** (common) | **BLK/BLU** | K1-1 (I/O Ground) | — (active-low) |
| — (MIDDLE) | open | — | Profile 1 "E" (default) |

Inputs are **active-low** (ground to activate) — matches the F/R switches
(K1-5/6). If they'd been active-high, grey would go to K1-10 (+12V OUT, RED/BLU)
instead; orange/brown stay the same.

## The 3 modes (regen on lift-off)
| Position | Profile | Neutral regen (default) | Feel |
|---|---|---|---|
| MIDDLE | 1 "E" | **0% — coast** | rolls free like neutral |
| UP | 2 "S" | **28% — some** | moderate engine-braking |
| DOWN | 3 "H" | **40% — high** | strong 1-pedal decel |

## SmartView setup / tuning
1. **Verify** (done): Monitor → Real-Time Data → **Inputs** → Digital In 7/8
   toggle with the switch; active profile shows E/S/H (or on the compact display).
2. **Tune regen per profile**: Configure → Traction → **Torque Limits → By Other
   → "Limit By Operating Profile"** → set Neutral Regen Torque for Profile 1/2/3.
3. **Optional power modes** (true Eco/Normal/Sport): give each profile its own
   drive torque limit in the same Torque Limits area.
4. ⚠️ If you edit Torque Mode deceleration rate, **keep it ≥ 90%/s** — slower is
   a dangerous lag before decel (manual p.33).
5. **SAVE**, then re-archive the clone (Manage → Clone) as the new backup.

Source: Hyper9_X1_System_User_Manual.pdf p.31 (Operating Profiles), p.45–46 (K1 I/O table).
