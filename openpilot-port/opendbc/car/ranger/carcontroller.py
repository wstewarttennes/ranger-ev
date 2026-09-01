from opendbc.car.interfaces import CarControllerBase


class CarController(CarControllerBase):
  def __init__(self, dbc_names, CP):
    super().__init__(dbc_names, CP)

  def update(self, CC, CS, now_nanos):
    # PHASE 1 = READ-ONLY: send nothing. Phase 2 builds the Hyper9 torque RPDO
    # here, gated by CarControllerParams and enforced by a panda safety_ranger.h.
    new_actuators = CC.actuators.as_builder()
    self.frame += 1
    return new_actuators, []
