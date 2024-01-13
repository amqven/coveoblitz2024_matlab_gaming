import game_message
from game_message import *
from actions import *
import random
import dataclasses
import inspect
import math

class Bot:
    def __init__(self):
        self.positions_enemies = []
        self.turret_valide = []
        print("Initializing your super mega duper bot")
        self._first_turn = True
        self._target_ship = None
        self._turret_target = False
        self._dead_counter = 0
        self._enemies = []
        self._ready_to_shoot = False
        self.usedStations = []

        # helm attributes
        self.last_angle = 0
        self.ship_direction = 0
        self.ship_angle = 0
        self.current_rotation_target = Vector(0, 0)
        self.someone_on_emp = False
        self.someone_on_normal = False
        self.cannon_orientation = None

    def get_next_move(self, game_message: GameMessage):
        """
        Here is where the magic happens, for now the moves are not very good. I bet you can do better ;)
        """
        actions = []

        team_id = game_message.currentTeamId
        my_ship = game_message.ships.get(team_id)
        self.other_ships_ids = [shipId for shipId in game_message.shipsPositions.keys() if shipId != team_id]
        
        station_list = my_ship.stations

        idle_crewmates = [crewmate for crewmate in my_ship.crew if crewmate.currentStation is None and crewmate.destination is None]
        if self._first_turn:
            self.other_ships_ids = [shipId for shipId in game_message.shipsPositions.keys() if shipId != team_id]
            self.enemy_count = len(self.other_ships_ids)
            self._target_id = self.other_ships_ids[0]
            self._target_ship = game_message.shipsPositions[self.other_ships_ids[0]]
            self.crewmate_dispatcher(actions, my_ship)

        if game_message.ships.get(self._target_id):
            # print(game_message.ships.get(self._target_id))
            if game_message.ships.get(self._target_id).currentHealth <= 100:
                self.set_new_target(game_message)

        self.turret_actions(game_message, my_ship, actions)
        self.helm_actions(actions, my_ship)

        self.radar_actions(actions, my_ship, self.other_ships_ids)

        # self.sendCrewmate2turret(TurretType.Normal, my_ship, 1, actions)
        self._first_turn = False
        return actions

    def radar_actions(self, actions, my_ship, other_ships_ids):
        operatedRadarStation = [station for station in my_ship.stations.radars if station.operator is not None]
        for radar_station in operatedRadarStation:
            actions.append(RadarScanAction(radar_station.id, self._target_id))

    def helm_actions(self, actions, my_ship):

        ship_angle = self.getShipAngle(my_ship)
        ship_direction = self.getShipDirection(my_ship)
        current_rotation_target = self.getRotationTarget()

        operatedHelmStation = [station for station in my_ship.stations.helms if station.operator is not None]

        boolRotate = False
        aiming_angle = self.cannon_orientation

        if operatedHelmStation:
            if self.cannon_orientation is not None:
                aim_direction = 360 - self.cannon_orientation
                if ((ship_angle <= (aim_direction -2)) or (ship_angle >= (aim_direction +2))):
                    if aim_direction  > 180:
                        actions.append(ShipRotateAction(180))
                    elif aim_direction  <= 180:
                        actions.append(ShipRotateAction(-180))
            else:
                actions.append(ShipLookAtAction(self._target_ship))

        
        if (ship_angle - self.last_angle) <= 1 and (ship_angle - self.last_angle) >= -1:
            self._ready_to_shoot = True
        else:
            self._ready_to_shoot = False
        self.last_angle = ship_angle


    def turret_actions(self, game_message: GameMessage, my_ship, actions):
        operatedTurretStations = [station for station in my_ship.stations.turrets if station.operator is not None]
        for turret_station in operatedTurretStations:
            max_charge = game_message.constants.ship.stations.turretInfos.get(turret_station.turretType).maxCharge
            if self._ready_to_shoot:              
                if not self._turret_target:
                    if turret_station.turretType != TurretType.Normal:
                        actions.append(TurretLookAtAction(turret_station.id, self._target_ship))
                    else:
                        meteors = filter(lambda d: d.debrisType == DebrisType.Large, game_message.debris)
                        meteors = sorted(meteors, lambda m: math.exp2(my_ship.worldPosition.x - m.position.x) + math.exp2(my_ship.worldPosition.y - m.position.y))

                        max_charge *= 0.1
                        if len(meteors) >= 0:
                            actions.append(TurretLookAtAction(turret_station.id, meteors[0].position))
                        else:
                            actions.append(TurretLookAtAction(turret_station.id, self._target_ship))
                    self._turret_target = True
                else:
                    if turret_station.charge <= 0.5*max_charge:
                        actions.append(TurretChargeAction(turret_station.id))
                    else:
                        actions.append(TurretShootAction(turret_station.id))
                    if turret_station.turretType == TurretType.Normal:
                        self._turret_target = False

    def set_new_target(self, game_message):
        self._dead_counter += 1
        self._dead_counter = self._dead_counter % self.enemy_count
        self._ready_to_shoot = False
        self._target_id = self.other_ships_ids[self._dead_counter]
        self._target_ship = game_message.shipsPositions[self._target_id]
        self._turret_target = False
        self.current_rotation_target = self._target_ship

    def getShipAngle(self, my_ship):
        return my_ship.orientationDegrees

    def getShipDirection(self, my_ship):
        return self.ship_direction

    def getRotationTarget(self):
        return self.current_rotation_target



    def turret_vise(self, my_ship):

        i = 0
        for turret in my_ship.stations.turrets:
            for angle in self.positions_enemies:
                self.turret_valide[i] = False
                if angle == turret.orientationDegrees:
                    self.turret_valide[i] = True
            i += 1

    def get_angles_enemis(self, game_message: GameMessage, my_ship):
        pos_ship = my_ship.worldPosition

        for id in game_message.ships.keys():
            if game_message.currentTeamId is not id:
                pos_enemy = game_message.ships.get(id).worldPosition
                self.positions_enemies.append(
                    (math.degrees(math.atan2(pos_enemy.y - pos_ship.y, pos_enemy.x - pos_ship.x)), id))

    def cannon_a_rotate(self, my_ship):
        for angles in self.positions_enemies:
            if self._target_ship.teamId == angles[1]:
                return angles[0] - my_ship.stations.turrets[3].orientationDegrees


    def crewmate_dispatcher(self, actions, my_ship: Ship):
        wantedStations = ["turrets", "helms", "radars", "shields", "turrets", "turrets", "shields", "turrets"]
        wantedStations = wantedStations[::-1]
        idle_crewmates = [crewmate for crewmate in my_ship.crew if crewmate.currentStation is None and crewmate.destination is None]
        for idle_crewmate in idle_crewmates:
            availableStations = idle_crewmate.distanceFromStations
            fields = dataclasses.fields(availableStations)
            for wantedStation in wantedStations:
                for field in fields:
                    stations = getattr(availableStations, wantedStation)
                    if (stations != []):
                        i = 0
                        try:
                            while(stations[i].stationId in usedStations):
                                i = i + 1
                        except:
                            continue
                        if wantedStation == "turrets":
                            turret = [turret for turret in my_ship.stations.turrets if turret.id == stations[i].stationId][0]
                            if turret.turretType not in [TurretType.Normal, TurretType.EMP]:
                                self.cannon_orientation = turret.orientationDegrees
                        actions.append(CrewMoveAction(idle_crewmate.id, stations[i].stationPosition))
                        usedStations.append(stations[i].stationId)
                        wantedStations.remove(wantedStation)
                        break

    def sendCrewmate2turret(self, turretType, my_ship, numberOfCrewmateOnGun, actions):
        idle_crewmates = [crewmate for crewmate in my_ship.crew if crewmate.currentStation is not None and crewmate.destination is None] #change to desired station to leave
        TurretId = []
        for turret in my_ship.stations.turrets:
            if (turret.turretType == turretType and turret.operator == None):
                TurretId.append(turret.id)

        for idle_crewmate in idle_crewmates:
            for turret in idle_crewmate.distanceFromStations.turrets:
                if (turret.stationId in TurretId and turret.stationId in self.usedStations):
                    try:
                        TurretId.remove(turret.stationId)
                    except:
                        print("coucou")
                    if (numberOfCrewmateOnGun != 0):
                        actions.append(CrewMoveAction(idle_crewmate.id, turret.stationPosition))
                        self.usedStations.append(turret.stationId)
                        numberOfCrewmateOnGun -= 1