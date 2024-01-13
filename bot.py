from game_message import *
from actions import *
import random
import math

class Bot:
    def __init__(self):
        self.positions_enemies = []
        self.turret_valide = []
        print("Initializing your super mega duper bot")
        self._first_turn = True
        self._target_ship = None
        self._turret_target = False

        # helm attributes
        self.ship_direction = 0
        self.ship_angle = 0
        self.current_rotation_target = Vector(200, 200)

    def get_next_move(self, game_message: GameMessage):
        """
        Here is where the magic happens, for now the moves are not very good. I bet you can do better ;)
        """
        actions = []

        team_id = game_message.currentTeamId
        my_ship = game_message.ships.get(team_id)
        other_ships_ids = [shipId for shipId in game_message.shipsPositions.keys() if shipId != team_id]
        self._target_ship = game_message.shipsPositions[random.choice(other_ships_ids)]
        print("targets", game_message.shipsPositions)

        station_list = my_ship.stations

        # Find who's not doing anything and try to give them a job?
        idle_crewmates = [crewmate for crewmate in my_ship.crew if crewmate.currentStation is None and crewmate.destination is None]
        if self._first_turn:

            actions.append(CrewMoveAction(idle_crewmates[0].id, my_ship.stations.helms[0].gridPosition))
            actions.append(CrewMoveAction(idle_crewmates[1].id, my_ship.stations.shields[0].gridPosition))
            emp_turrets = [turret for turret in station_list.turrets if turret.turretType is TurretType.EMP]
            normal_turret = [turret for turret in station_list.turrets if turret.turretType is TurretType.Normal]
            #if emp_turrets:
            #    actions.append(CrewMoveAction(idle_crewmates[2].id, emp_turrets[0].gridPosition))
            if normal_turret:
                actions.append(CrewMoveAction(idle_crewmates[2].id, normal_turret[0].gridPosition))
            else:
                actions.append(CrewMoveAction(idle_crewmates[2].id, my_ship.stations.turrets[0].gridPosition))
            actions.append(CrewMoveAction(idle_crewmates[3].id, my_ship.stations.radars[0].gridPosition))
        print(self._target_ship)
        self.turret_actions(game_message, my_ship, actions)
        self.helm_actions(actions, my_ship)

        self.radar_actions(actions, my_ship, other_ships_ids)

        # You can clearly do better than the random actions above! Have fun!
        self._first_turn = False
        return actions

    def radar_actions(self, actions, my_ship, other_ships_ids):
        operatedRadarStation = [station for station in my_ship.stations.radars if station.operator is not None]
        for radar_station in operatedRadarStation:
            actions.append(RadarScanAction(radar_station.id, random.choice(other_ships_ids)))

    def helm_actions(self, actions, my_ship):

        ship_angle = self.getShipAngle(my_ship)
        ship_direction = self.getShipDirection(my_ship)
        current_rotation_target = self.getRotationTarget()

        operatedHelmStation = [station for station in my_ship.stations.helms if station.operator is not None]

        if operatedHelmStation:
            actions.append(ShipLookAtAction(current_rotation_target))

    def turret_actions(self, game_message, my_ship, actions):
            actions.append(ShipRotateAction(random.uniform(0, 360)))

    def turret_actions(self, game_message: GameMessage, my_ship, actions):
        # Now crew members at stations should do something!
        operatedTurretStations = [station for station in my_ship.stations.turrets if station.operator is not None]
        for turret_station in operatedTurretStations:
            if not self._turret_target:
                actions.append(TurretLookAtAction(turret_station.id, self._target_ship))
                self._turret_target = True
                continue
            max_charge = game_message.constants.ship.stations.turretInfos.get(turret_station.turretType).maxCharge
            if turret_station.charge < max_charge*0.5:
                 actions.append(TurretChargeAction(turret_station.id))
            else:
                 actions.append(TurretShootAction(turret_station.id))


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
                if pos_enemy.x == pos_ship.x:
                    if pos_enemy.y > pos_ship.y:
                        self.positions_enemies.append(90)
                    else:
                        self.positions_enemies.append(270)
                elif pos_enemy.y == pos_ship.y:
                    if pos_enemy.x > pos_ship.x:
                        self.positions_enemies.append(0)
                    else:
                        self.positions_enemies.append(180)
                else:
                    if pos_enemy.x > pos_ship.x:
                        if pos_enemy.y > pos_ship.y:
                            self.positions_enemies.append(
                                (math.atan2(pos_enemy.y - pos_ship.y, pos_enemy.x - pos_ship.x), id))
                        else:
                            self.positions_enemies.append(
                                (360 + math.atan2(pos_enemy.y - pos_ship.y, pos_enemy.x - pos_ship.x), id))
                    else:
                        self.positions_enemies.append((
                            180 + math.atan2(pos_enemy.y - pos_ship.y, pos_enemy.x - pos_ship.x), id))

    def cannon_a_rotate(self, my_ship):
        for angles in self.positions_enemies:
            if self._target_ship.teamId == angles[1]:
                return angles[0] - my_ship.stations.turrets[3].orientationDegrees
