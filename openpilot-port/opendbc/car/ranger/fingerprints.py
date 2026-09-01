from opendbc.car.structs import CarParams
from opendbc.car.ranger.values import CAR

Ecu = CarParams.Ecu

# openpilot IDs the car by the SET of arbitration IDs on the bus. These are the
# Hyper9 X1 + Thunderstruck MCU broadcast IDs. No UDS/ISO-TP ECUs -> no FW query.
FINGERPRINTS = {
  CAR.RANGER_EV: [{
    # Hyper9 X1 (drive bus): 385=0x181, 386=0x182, 387=0x183, 388=0x184
    385: 8, 386: 8, 387: 8, 388: 8,
    # Thunderstruck MCU/BMS: 849=0x351, 853=0x355, 854=0x356
    849: 8, 853: 6, 854: 6,
  }],
}

FW_VERSIONS = {}
