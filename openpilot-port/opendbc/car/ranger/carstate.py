from opendbc.can import CANParser
from opendbc.car import Bus, structs
from opendbc.car.interfaces import CarStateBase
from opendbc.car.ranger.values import DBC

GearShifter = structs.CarState.GearShifter

# SYSTEM_FLAGS bit positions (from ranger-dashboard/src/state/vehicle.py)
FLAG_PARK_BRAKE = 1 << 4
FLAG_PEDAL_BRAKE = 1 << 5


class CarState(CarStateBase):
  def update(self, can_parsers) -> structs.CarState:
    cp = can_parsers[Bus.main]
    ret = structs.CarState()

    # Speed -------------------------------------------------------------------
    # NOTE the X1's VEHICLE_SPEED is motor_rpm x a fixed ratio -> only correct in
    # ONE gear on the manual gearbox. For a trustworthy vEgo, feed a
    # gear-independent source (comma GPS / tailshaft VSS) before phase 2. Kept as
    # the CAN value here for the read-only phase.
    v_kmh = abs(cp.vl["HYPER9_STATUS"]["VEHICLE_SPEED"])
    v_ego_raw = v_kmh / 3.6
    ret.wheelSpeeds.fl = ret.wheelSpeeds.fr = v_ego_raw
    ret.wheelSpeeds.rl = ret.wheelSpeeds.rr = v_ego_raw
    ret.vEgoRaw = v_ego_raw
    ret.vEgo, ret.aEgo = self.update_speed_kf(v_ego_raw)
    ret.standstill = v_ego_raw < 0.1

    # Throttle / brake --------------------------------------------------------
    throttle = cp.vl["HYPER9_MOTOR"]["THROTTLE_REQUEST"]
    ret.gas = max(0.0, min(throttle, 100.0)) / 100.0
    ret.gasPressed = ret.gas > 1e-3

    flags = int(cp.vl["HYPER9_STATUS"]["SYSTEM_FLAGS"])
    ret.brakePressed = bool(flags & FLAG_PEDAL_BRAKE)

    # Gear — signed MOTOR_RPM is the source of truth (firmware F/R bits frozen) --
    rpm = cp.vl["HYPER9_MOTOR"]["MOTOR_RPM"]
    if flags & FLAG_PARK_BRAKE:
      ret.gearShifter = GearShifter.park
    elif rpm > 20:
      ret.gearShifter = GearShifter.drive
    elif rpm < -20:
      ret.gearShifter = GearShifter.reverse
    else:
      ret.gearShifter = GearShifter.neutral

    # Steering — ZEROED (no EPS / no angle sensor yet) -------------------------
    ret.steeringAngleDeg = 0.0
    ret.steeringRateDeg = 0.0
    ret.steeringTorque = 0.0
    ret.steeringPressed = False

    # Cruise / misc — nothing engaged in phase 1 -----------------------------
    ret.cruiseState.available = False
    ret.cruiseState.enabled = False
    ret.doorOpen = False
    ret.seatbeltUnlatched = False

    return ret

  @staticmethod
  def get_can_parsers(CP):
    # Drive signals live on the Hyper9 bus (Bus.main). Names come from ranger_ev.dbc.
    msgs = [
      ("HYPER9_STATUS", 50),   # 0x181
      ("HYPER9_MOTOR", 50),    # 0x183
    ]
    return {Bus.main: CANParser(DBC[CP.carFingerprint][Bus.main], msgs, 0)}
