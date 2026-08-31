"""Ranger EV port — CarController.

Phase 1 = NO-OP. openpilot is read-only, so this sends nothing to the bus.
Real actuation (Hyper9 torque for accel/regen) arrives in phase 2, and only
behind a panda safety_ranger.h hook that enforces per-message limits.

VERSION PIN: CarControllerBase.update() varies by opendbc revision. Recent:
    def update(self, CC, CS, now_nanos) -> tuple[actuators, can_sends]
Older openpilot passed (self, CC, CS, frame, ...) and returned only can_sends.
Confirm against an existing port (e.g. opendbc/car/body/carcontroller.py) before
adding real sends.
"""

from opendbc.car.interfaces import CarControllerBase


class CarController(CarControllerBase):
  def __init__(self, dbc_names, CP):
    super().__init__(dbc_names, CP)

  def update(self, CC, CS, now_nanos):
    can_sends = []

    # --- PHASE 1: intentionally send NOTHING. --------------------------------
    # Phase 2 will build the Hyper9 torque RPDO frame(s) here, clamped by
    # CarControllerParams (values.py) and re-checked by panda safety. Until the
    # safety hook exists, this must stay empty — SILENT safety would block TX
    # anyway, but we keep the controller inert as a second line of defense.

    new_actuators = CC.actuators.as_builder()
    new_actuators.steeringAngleDeg = 0.0
    return new_actuators, can_sends
