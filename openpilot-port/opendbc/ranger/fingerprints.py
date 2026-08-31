"""Ranger EV port — fingerprints.

openpilot identifies the car by the SET of CAN arbitration IDs on the bus. There
are no UDS/ISO-TP ECUs here to firmware-fingerprint, so matching is purely by the
Hyper9 X1 + Thunderstruck MCU broadcast IDs (from the DBCs).

VERSION PIN: the harness discovers FINGERPRINTS / FW_VERSIONS by module name, so
they live here (not values.py). If your opendbc expects them elsewhere, mirror
whatever an existing brand does.
"""

from opendbc.car.ranger.values import CAR

# {arb_id: dlc}. openpilot matches the live bus against this when it can't
# firmware-fingerprint. Capture the real set with the bus live:
#   candump can1   (or the dashboard /api/can/raw)  -> confirm these IDs + DLCs.
FINGERPRINTS = {
  CAR.RANGER_EV: [{
    # Hyper9 X1 (drive bus): 385=0x181, 386=0x182, 387=0x183, 388=0x184
    385: 8, 386: 8, 387: 8, 388: 8,
    # Thunderstruck MCU/BMS: 849=0x351, 853=0x355, 854=0x356
    849: 8, 853: 6, 854: 6,
  }],
}

# No UDS/ISO-TP ECUs to query -> no firmware-version fingerprinting.
FW_VERSIONS = {}
