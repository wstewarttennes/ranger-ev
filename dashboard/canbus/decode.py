"""Decode raw CAN frames into named engineering signals, driven by messages.yaml.

The map file is the source of truth (see messages.yaml). This module stays
generic: give it an arbitration id + data bytes, it returns a dict of
{signal_name: (value, unit, verified)} for every signal defined on that id.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import yaml

_MAP_PATH = os.path.join(os.path.dirname(__file__), "messages.yaml")


@dataclass
class Decoded:
    value: float | int | bool
    unit: str
    verified: bool


class Decoder:
    def __init__(self, map_path: str = _MAP_PATH):
        with open(map_path) as f:
            self._map = yaml.safe_load(f)
        # index messages by arbitration id for O(1) lookup
        self._by_id: dict[int, dict[str, Any]] = {}
        for name, msg in self._map["messages"].items():
            msg = dict(msg)
            msg["name"] = name
            self._by_id[int(msg["id"])] = msg

    @property
    def known_ids(self) -> set[int]:
        return set(self._by_id)

    def message_name(self, arb_id: int) -> str | None:
        m = self._by_id.get(arb_id)
        return m["name"] if m else None

    def decode(self, arb_id: int, data: bytes) -> dict[str, Decoded]:
        """Return {signal_name: Decoded} for a frame, or {} if id is unknown."""
        msg = self._by_id.get(arb_id)
        if not msg:
            return {}
        verified = bool(msg.get("verified", False))
        out: dict[str, Decoded] = {}
        for sig_name, spec in msg["signals"].items():
            try:
                val = _extract(data, spec)
            except (IndexError, ValueError):
                continue  # frame shorter than the map expects — skip this signal
            out[sig_name] = Decoded(value=val, unit=spec.get("unit", ""), verified=verified)
        return out


def _extract(data: bytes, spec: dict[str, Any]) -> float | int | bool:
    start = spec["start"]

    # Flag/bit signal: single bit within one byte -> bool
    if "bit" in spec:
        if start >= len(data):
            raise IndexError
        return bool(data[start] & (1 << spec["bit"]))

    length = spec["length"]
    if start + length > len(data):
        raise IndexError
    chunk = data[start:start + length]
    endian = "big" if spec.get("endian", "big") == "big" else "little"
    raw = int.from_bytes(chunk, byteorder=endian, signed=bool(spec.get("signed", False)))

    scale = spec.get("scale", 1.0)
    offset = spec.get("offset", 0.0)
    val = raw * scale + offset
    # keep ints clean when scaling is trivial
    if scale == 1.0 and offset == 0.0:
        return int(val)
    return round(val, 3)
