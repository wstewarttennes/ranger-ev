# ranger

1986 Ford Ranger EV conversion — build files, firmware, and the openpilot port.

## layout

- **`openpilot-port/`** — openpilot car port for the conversion. `spec/` documents the
  Ranger CAN → openpilot `carState` mapping; `opendbc/ranger/` is the port (DBC, values,
  carstate). Phase 1 = read-only.
- **`wiring/`** — vehicle wiring notes (X1/Hyper9 pinouts, CAN conventions, EV harness).
- **`esp32/`** — ESPHome config for the ESP32 (secrets via gitignored `secrets.yaml`).
- **`dashboard/`** — CAN recon + decode scripts (`canbus/`, `capture/`).
- **`manuals/`** — vendor PDFs (Hyper9 X1, Thunderstruck MCU/EVCC/charger, Sevcon DC-DC).

## related

- **`ranger-dashboard/`** (not tracked here) — the FastAPI CAN dashboard that runs on the
  Pi. It has its own repo: https://github.com/wstewarttennes/ranger-dashboard
