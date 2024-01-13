from __future__ import annotations

from dataclasses import dataclass
from game_message import Vector


@dataclass
class StationAction:
    stationId: str


@dataclass
class TurretRotateAction(StationAction):
    angle: float
    type: str = "TURRET_ROTATE"


@dataclass
class TurretLookAtAction(StationAction):
    target: Vector
    type: str = "TURRET_LOOK_AT"


@dataclass
class TurretChargeAction(StationAction):
    type: str = "TURRET_CHARGE"


@dataclass
class TurretShootAction(StationAction):
    type: str = "TURRET_SHOOT"


@dataclass
class RadarScanAction(StationAction):
    targetShip: str
    type: str = "RADAR_SCAN"


@dataclass
class CrewMoveAction:
    crewMemberId: str
    destination: Vector
    type: str = "CREW_MOVE"


@dataclass
class ShipRotateAction:
    angle: float
    type: str = "SHIP_ROTATE"


@dataclass
class ShipLookAtAction:
    target: Vector
    type: str = "SHIP_LOOK_AT"