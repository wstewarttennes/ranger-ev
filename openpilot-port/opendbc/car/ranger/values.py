"""Ranger EV port — platform config + specs. Matches the opendbc car API on the
comma's openpilot v0.11.1 (Bus.main DBC map, Platforms/PlatformConfig/CarSpecs).
"""
from opendbc.car import Bus, CarSpecs, PlatformConfig, Platforms
from opendbc.car.docs_definitions import CarDocs
from opendbc.car.structs import CarParams

Ecu = CarParams.Ecu


class CarControllerParams:
  # Phase 1 = READ-ONLY: no actuation, so no limits yet. Real values land in
  # phase 2 when carcontroller.py drives the Hyper9 torque RPDO.
  def __init__(self, CP):
    pass


class CAR(Platforms):
  RANGER_EV = PlatformConfig(
    [CarDocs("Ford Ranger EV (1986 conversion)", package="All")],
    # 1986 Ranger, 2.9L V6 auto originally, reg cab 7-ft (long) bed -> wheelbase
    # ~114 in = 2.90 m. mass ESTIMATE ~1430 kg (stock ~3000 lb V6 long-bed, minus
    # engine/fuel/exhaust/auto-trans, plus Tesla pack + Hyper9 + controllers).
    # steerRatio placeholder (no EPS). TODO: real mass on a CAT scale.
    CarSpecs(mass=1430.0, wheelbase=2.90, steerRatio=18.0, centerToFrontRatio=0.44),
    {Bus.main: 'ranger_ev'},
  )


DBC = CAR.create_dbc_map()
