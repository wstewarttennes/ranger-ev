# Ranger ESP32 gatekeeper

Tiny always-on ESP32 that (1) remote-powers the truck by pulsing the on/off
button, and (2) passively reads the battery CAN bus so SoC/pack data hits Home
Assistant whenever the bus is awake — without keeping the Pi on.

Why an ESP32 and not the Pi: it idles at ~half a watt, so it can live on
**constant 12V** and be the thing that wakes everything else on command. The Pi
stays the in-truck kiosk + full dashboard; it boots when the ESP turns the truck on.

## Wiring

Power from **constant/standby 12V** (not switched) → buck → **5V into VIN**. Fuse the
12V feed at ~1A.

| ESP32 pin | to | notes |
|-----------|----|-------|
| GPIO23 | opto-relay module IN | relay dry contacts wire **across the physical button contacts** (parallel). No polarity — it just "presses" the button. |
| GPIO25 | opto **feedback** | is-it-on sense. Opto LED from **switched-12V** (through ~2k2 resistor); transistor pulls GPIO25 LOW when the system is on. Internal pullup, inverted in config. |
| GPIO5 (TX) / GPIO4 (RX) | SN65HVD230 D / R | CAN transceiver |
| 3V3 | SN65HVD230 VCC | transceiver runs on 3.3V |
| GND | common ground | tie ESP GND, buck GND, transceiver GND, truck GND together |

**CAN tap:** SN65HVD230 CANH/CANL onto the **Thunderstruck battery bus @ 250k**
(the one on Pi `can0` — MCU ↔ charger ↔ Pi). Keep the stub short. The ESP32 is a
**middle node → NO terminator**: the bus is already 60Ω (MCU 120Ω + Pi HAT 120Ω),
so **remove the 120Ω on the SN65HVD230 board** (jumper or desolder) or you'll drop
the bus to 40Ω and cause errors.

Use **opto-isolation on both the relay and the feedback** — automotive 12V is
noisy and you don't want to backfeed the ESP.

## Flash

Needs a `secrets.yaml` next to the config:

```yaml
wifi_ssid: "..."
wifi_password: "..."
api_key: "..."       # esphome generates one; or `openssl rand -base64 32`
ota_password: "..."
```

Then:

```bash
esphome run ranger-esp32.yaml
```

It'll show up in HA (ESPHome integration auto-discovers) as device **Ranger ESP32**
with: `switch.ranger_power`, `binary_sensor.ranger_system_on`,
`binary_sensor.ranger_can_bus_live`, and `sensor.ranger_soc / _pack_voltage /
_pack_current / _pack_temp`.

## How you'd actually use it

Two modes, and **passive is the default** — no polling needed:

- **Passive capture:** any time you drive or plug in to charge, the bus wakes and
  the ESP catches SoC/V/I/temp → HA. Free, zero contactor cycling.
- **On-demand check:** flip `switch.ranger_power` from your phone → truck powers up
  → Pi boots the full dashboard → flip it back off when done.

### Optional: periodic auto-poll

Only if you want a guaranteed fresh reading on a schedule. **Tradeoff:** the button
wakes the *whole* system, so this cycles the HV contactor each time just to read
SoC. Fine occasionally; not something to run every 15 min. Gear rests in N and
throttle at 0, so it's a safe non-moving state.

```yaml
# Home Assistant automation
alias: Ranger periodic poll
trigger:
  - platform: time_pattern
    hours: "/6"
condition:
  - condition: state
    entity_id: switch.ranger_power
    state: "off"                      # don't poke it if it's already on
action:
  - service: switch.turn_on
    target: { entity_id: switch.ranger_power }
  - wait_template: "{{ is_state('binary_sensor.ranger_can_bus_live','on') }}"
    timeout: "00:01:30"
  - delay: "00:00:20"                 # let a few frames flow / Pi publish
  - service: switch.turn_off
    target: { entity_id: switch.ranger_power }
```

## Notes / gotchas

- **Feedback matters** because your button is momentary-toggle: a blind pulse
  would turn the truck *off* if it happened to already be on. The template switch
  reads `system_on` first and only pulses when it needs to flip state.
- If the bus is silent when you expect data, it's asleep — the MCU broadcasts when
  KSI is on or on charge plug-in, not when fully off. That's why "data all the
  time" = "wake briefly and snapshot," which is the mode above.
- Byte layouts pulled from `ranger-dashboard/dbc/thunderstruck_mcu.dbc`
  (0x355 SoC, 0x356 V/I/temp). If those ever move, update the `on_frame` lambdas.
