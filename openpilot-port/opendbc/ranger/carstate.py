"""Ranger EV port — CarState. Parses the Hyper9 + MCU bus into openpilot's
structs.CarState. Implements the mapping in spec/ranger_carstate_spec.md.

Phase 1 = read-only: everything drive-related is populated, everything
steering/cruise is zeroed (no EPS, no stalk mapped yet).

VERSION PIN: the update() signature changed in the opendbc refactor. Recent
opendbc passes a dict of CANParsers keyed by bus: update(self, can_parsers).
Older openpilot passed (self, cp, cp_cam). The parsing in _parse() below is
signature-agnostic — adapt update() to whatever your revision uses and hand it
the Hyper9 parser.
"""

from opendbc.can.parser import CANParser
from opendbc.car import structs
from opendbc.car.interfaces import CarStateBase
from opendbc.car.ranger.values import DBC, CAR

GearShifter = structs.CarState.GearShifter

# SYSTEM_FLAGS bit positions (from ranger-dashboard/src/state/vehicle.py)
FLAG_PARK_BRAKE = 1 << 4
FLAG_PEDAL_BRAKE = 1 << 5
FLAG_RUNNING = 1 << 9

# Bus indices in the port (see spec). Hyper9 drive bus is where the essentials live.
BUS_HYPER9 = 0
BUS_MCU = 1


class CarState(CarStateBase):
  def __init__(self, CP):
    super().__init__(CP)

  # --- signature-agnostic core: give it the parsed Hyper9 CANParser ---
  def _parse(self, ret: structs.CarState, cp: CANParser) -> structs.CarState:
    # Speed -------------------------------------------------------------------
    # ⚠️ GEAR-DEPENDENT (fix before phase 2 / longitudinal). The X1's
    # VEHICLE_SPEED is motor_rpm x a fixed internal ratio, so it's only correct
    # in ONE gear on this manual gearbox — measured 2026-08, ~right in 3rd,
    # reads ~half in 4th. For a trustworthy vEgo, replace this with a
    # gear-independent source (comma GPS, or a tailshaft VSS) and derive the
    # forward gear from motor_rpm / true_speed. See spec/ranger_carstate_spec.md.
    v_kmh = abs(cp.vl["HYPER9_STATUS"]["VEHICLE_SPEED"])
    v_ego_raw = v_kmh / 3.6  # m/s
    # openpilot wants per-wheel; we have one number. Feed all four the same.
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

    # Gear — signed motor RPM is the source of truth (firmware F/R bits frozen) -
    rpm = cp.vl["HYPER9_MOTOR"]["MOTOR_RPM"]
    if flags & FLAG_PARK_BRAKE:
      ret.gearShifter = GearShifter.park
    elif rpm > 20:
      ret.gearShifter = GearShifter.drive
    elif rpm < -20:
      ret.gearShifter = GearShifter.reverse
    else:
      ret.gearShifter = GearShifter.neutral

    # Steering — ZEROED until a steering-angle sensor + EPS exist (phase 1.5+) -
    ret.steeringAngleDeg = 0.0
    ret.steeringRateDeg = 0.0
    ret.steeringTorque = 0.0
    ret.steeringPressed = False

    # Cruise / misc — nothing engaged in phase 1 --------------------------------
    ret.cruiseState.available = False
    ret.cruiseState.enabled = False
    ret.espDisabled = False
    ret.doorOpen = False
    ret.seatbeltUnlatched = False

    return ret

  def update(self, can_parsers) -> structs.CarState:
    ret = structs.CarState()
    # NOTE adapt to your opendbc: can_parsers may be a dict keyed by bus, or you
    # may receive cp/cp_cam positionally. Hand _parse the Hyper9 pt parser.
    cp = can_parsers[BUS_HYPER9] if isinstance(can_parsers, dict) else can_parsers
    return self._parse(ret, cp)

  @staticmethod
  def get_can_parsers(CP):
    # Drive signals all live on the Hyper9 pt bus. MCU parser can be added when
    # we choose to surface pack data inside openpilot (phase 2).
    pt_msgs = [
      ("HYPER9_STATUS", 50),   # 0x181, 20ms
      ("HYPER9_MOTOR", 50),    # 0x183, 50ms
    ]
    return {BUS_HYPER9: CANParser(DBC[CAR.RANGER_EV]["pt"], pt_msgs, BUS_HYPER9)}
