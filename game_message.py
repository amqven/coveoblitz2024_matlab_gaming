from __future__ import annotations

from dataclasses import dataclass, field
from enum import unique, Enum
from typing import List, Dict, Optional


@dataclass
class GameMessage:
    type: str
    tick: int
    lastTickErrors: List[str]
    constants: Constants
    currentTickNumber: int
    debris: List[Debris]
    rockets: List[Projectile]
    shipsPositions: Dict[str, Vector]
    ships: Dict[str, Ship]
    currentTeamId: str


@dataclass
class DebrisExplodesInto:
    debrisType: DebrisType
    approximateAngle: float


@unique
class DebrisType(str, Enum):
    Large = "LARGE"
    Medium = "MEDIUM"
    Small = "SMALL"


@dataclass
class DebrisInfo:
    radius: float
    damage: float
    approximateSpeed: float
    explodesInto: List[DebrisExplodesInto] = field(default_factory=list)


@dataclass
class Projectile:
    id: str
    teamId: Optional[str]
    position: Vector
    velocity: Vector
    radius: float
    damage: float
    bonusShieldDamage: float
    bonusHullDamage: float


@dataclass
class Debris(Projectile):
    debrisType: DebrisType


@dataclass
class World:
    width: float
    height: float


@dataclass
class Grid:
    height: int
    width: int

@unique
class TurretType(str, Enum):
    Normal = "NORMAL"
    Fast = "FAST"
    Cannon = "CANNON"
    Sniper = "SNIPER"
    EMP = "EMP"

@dataclass
class TurretConstants:
    rotatable: bool
    rocketChargeCost: int
    maxCharge: int
    rocketSpeed: float
    rocketRadius: float
    rocketDamage: float
    rocketBonusShieldDamage: float
    rocketBonusHullDamage: float


@dataclass
class ShieldConstants:
    shieldRadius: float
    shieldRegenerationPercent: float
    shieldBreakHandicap: int


@dataclass
class RadarConstants:
    radarRadius: float


@dataclass
class StationsConstants:
    turretInfos: Dict[TurretType, TurretConstants]
    shield: ShieldConstants
    radar: RadarConstants


@dataclass
class ShipConstants:
    grid: Grid
    maxHealth: float
    maxShield: float
    maxRotationDegrees: float
    stations: StationsConstants


@dataclass
class Constants:
    world: World
    debrisInfos: Dict[DebrisType, DebrisInfo]
    ship: ShipConstants


@dataclass
class CrewMember:
    id: str
    name: str
    age: float
    socialInsurance: str
    currentStation: Optional[str]
    destination: Optional[Vector]
    gridPosition: Vector
    distanceFromStations: DistanceFromStations


@dataclass
class CrewDistance:
    stationId: str
    stationPosition: Vector
    distance: float


@dataclass
class DistanceFromStations:
    turrets: List[CrewDistance]
    shields: List[CrewDistance]
    radars: List[CrewDistance]
    helms: List[CrewDistance]


@dataclass
class Vector:
    x: float
    y: float


@dataclass
class WalkableTile:
    x: float
    y: float


@dataclass
class Station:
    id: str
    gridPosition: Vector
    operator: Optional[str]


@dataclass
class TurretStation(Station):
    turretType: TurretType
    worldPosition: Vector
    orientationDegrees: float
    charge: int
    cooldown: int


@dataclass
class RadarStation(Station):
    currentTarget: Optional[str]


@dataclass
class StationsData:
    turrets: List[TurretStation]
    shields: List[Station]
    radars: List[RadarStation]
    helms: List[Station]


@dataclass
class Ship:
    teamId: str
    worldPosition: Vector
    orientationDegrees: float
    currentHealth: float
    currentShield: float
    crew: List[CrewMember]
    walkableTiles: List[WalkableTile]
    stations: StationsData
