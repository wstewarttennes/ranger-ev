"""Ranger EV port — platform config, fingerprint, control limits.

Ported for the 1986 Ford Ranger EV conversion (Hyper9 X1 + Thunderstruck MCU).

VERSION PIN: the opendbc car API (Platforms / PlatformConfig / CarSpecs / DbcDict)
was introduced/renamed in the 2024 opendbc split-out. Confirm the exact imports
against the opendbc revision on the comma 4 before wiring into the tree:
    python3 -c "import opendbc, os; print(os.path.dirname(opendbc.__file__))"
    ls <that>/car/   # look for structs.py, interfaces.py, an existing brand to copy
"""

from dataclasses import dataclass, field
from enum import StrEnum

from opendbc.car import CarSpecs, PlatformConfig, Platforms, DbcDict
from opendbc.car.structs import CarParams
from opendbc.car.docs_definitions import CarDocs

Ecu = CarParams.Ecu


@dataclass
class RangerCarDocs(CarDocs):
  package: str = "All"


@dataclass
class RangerPlatformConfig(PlatformConfig):
  dbc_dict: DbcDict = field(default_factory=lambda: {
    # Both buses decode against the one combined port DBC.
    "pt": "ranger_ev",
    "radar": None,
  })


class CAR(Platforms):
  RANGER_EV = RangerPlatformConfig(
    [RangerCarDocs("Ford Ranger EV (1986 conversion)")],
    # TODO measure: wheelbase ~2.86 m (reg cab), steerRatio placeholder (no EPS yet),
    # mass is curb + pack — weigh it. These don't affect phase-1 read-only.
    CarSpecs(mass=1600.0, wheelbase=2.86, steerRatio=18.0),
  )


# Fingerprints (arbitration-ID set) + FW_VERSIONS now live in fingerprints.py,
# per the modern opendbc layout. values.py = platforms / specs / control limits.


class CarControllerParams:
  """Actuation limits — INERT in phase 1 (read-only). Real values land when we
  wire carcontroller.py to the Hyper9 torque RPDO and the EPS retrofit."""
  # Longitudinal (Hyper9 torque %): keep tiny/zero until bench-validated.
  ACCEL_MIN = 0.0
  ACCEL_MAX = 0.0
  # Lateral: no EPS yet.
  STEER_MAX = 0
  STEER_STEP = 1

  def __init__(self, CP):
    pass


DBC = CAR.create_dbc_map()
