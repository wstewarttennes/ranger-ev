from opendbc.car import get_safety_config, structs
from opendbc.car.ranger.carcontroller import CarController
from opendbc.car.ranger.carstate import CarState
from opendbc.car.interfaces import CarInterfaceBase


class CarInterface(CarInterfaceBase):
  CarState = CarState
  CarController = CarController

  @staticmethod
  def _get_params(ret: structs.CarParams, candidate, fingerprint, car_fw, alpha_long, is_release, docs) -> structs.CarParams:
    ret.brand = "ranger"

    # PHASE 1 = READ-ONLY: observe the bus, transmit nothing.
    # SILENT safety = panda logs all frames, blocks all TX. dashcamOnly keeps the
    # planner from expecting to actuate.
    ret.safetyConfigs = [get_safety_config(structs.CarParams.SafetyModel.silent)]
    ret.dashcamOnly = True

    # No EPS (manual/hydraulic steering) and no longitudinal control yet.
    ret.steerControlType = structs.CarParams.SteerControlType.angle
    ret.steerActuatorDelay = 0.0
    ret.steerLimitTimer = 1.0
    ret.radarUnavailable = True
    ret.openpilotLongitudinalControl = False

    return ret
