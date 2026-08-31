"""Ranger EV port — CarInterface.

Ties carstate.py + values.py together and hands openpilot a CarParams.
Phase 1 = READ-ONLY: openpilot sees the car (carState), but sends nothing —
SILENT panda safety + dashcamOnly. No steering (no EPS), no longitudinal.

VERSION PIN: the opendbc car API was reworked in the 2024 standalone split.
The `_get_params` signature and several CarParams field names vary by revision.
Confirm against the opendbc on your comma before wiring in:
    OP=$(python3 -c "import opendbc,os;print(os.path.dirname(opendbc.__file__))")
    grep -n "_get_params" $OP/car/interfaces.py        # exact signature + arg names
    sed -n '1,60p' $OP/car/body/interface.py           # a tiny real port to mirror
Things that move between revisions: `ret.brand` vs `ret.carName`;
`alpha_long` vs `experimental_long` arg; SafetyModel.silent vs noOutput.
"""

from opendbc.car import get_safety_config, structs
from opendbc.car.interfaces import CarInterfaceBase


class CarInterface(CarInterfaceBase):
  @staticmethod
  def _get_params(ret: structs.CarParams, candidate, fingerprint, car_fw,
                  alpha_long, docs) -> structs.CarParams:
    # --- identity -----------------------------------------------------------
    # Recent opendbc uses ret.brand (matches the opendbc/car/<brand>/ folder).
    # Older revisions used ret.carName — set whichever exists on your comma.
    ret.brand = "ranger"

    # --- PHASE 1: read-only. openpilot observes, transmits nothing. ----------
    # SILENT = panda logs the bus and blocks all TX. dashcamOnly stops the
    # stack from expecting to actuate anything.
    ret.safetyConfigs = [get_safety_config(structs.CarParams.SafetyModel.silent)]
    ret.dashcamOnly = True

    # --- lateral: NONE. Manual/hydraulic steering, no EPS to command. --------
    # Left as torque type so the struct is well-formed; nothing is ever sent.
    ret.steerControlType = structs.CarParams.SteerControlType.torque
    ret.steerActuatorDelay = 0.0
    ret.steerLimitTimer = 0.0

    # --- longitudinal: OFF in phase 1. Hyper9 torque control lands phase 2. --
    ret.openpilotLongitudinalControl = False
    ret.radarUnavailable = True

    # mass / wheelbase / steerRatio come from CarSpecs in values.py — MEASURE
    # them on the real truck; the placeholders there don't affect read-only.
    return ret
