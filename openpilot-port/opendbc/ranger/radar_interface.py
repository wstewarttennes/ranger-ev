"""Ranger EV port — RadarInterface.

No radar on the truck (phase 1 & 2), so this reports no radar points and
openpilot runs vision-only. `radarUnavailable = True` is set in interface.py.

Adding radar later (e.g. a Continental ARS408 on CAN1 at 500k): implement
update() to parse the radar's DBC into RadarData.points, set the "radar" DBC in
values.py's dbc_dict, and flip radarUnavailable off in interface.py.

VERSION PIN: RadarInterfaceBase.update(can_strings) return type varies; recent
opendbc returns a structs.RadarData or None. None is always safe for "no radar".
"""

from opendbc.car.interfaces import RadarInterfaceBase


class RadarInterface(RadarInterfaceBase):
  def __init__(self, CP):
    super().__init__(CP)

  def update(self, can_strings):
    # No radar hardware -> no points. Vision-only.
    return None
