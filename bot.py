from game_message import *
from actions import *
import random
import dataclasses
import inspect

class Bot:
    def __init__(self):
        print("Initializing your super mega duper bot")
        self._first_turn = True
        self._target_ship = None
        self._turret_target = False


    def get_next_move(self, game_message: GameMessage):
        """
        Here is where the magic happens, for now the moves are not very good. I bet you can do better ;)
        """
        actions = []
        team_id = game_message.currentTeamId
        my_ship = game_message.ships.get(team_id)
        other_ships_ids = [shipId for shipId in game_message.shipsPositions.keys() if shipId != team_id]
        self._target_ship = game_message.shipsPositions[random.choice(other_ships_ids)]
        # print("targets", game_message.shipsPositions)

        # Find who's not doing anything and try to give them a job?
        if self._first_turn:
            self.crewmate_dispatcher(actions, my_ship)
            
        # print(self._target_ship)
        self.turret_actions(game_message, my_ship, actions)
        #self.helm_actions(actions, my_ship)

        self.radar_actions(actions, my_ship, other_ships_ids)

        # You can clearly do better than the random actions above! Have fun!
        self._first_turn = False
        return actions

    def radar_actions(self, actions, my_ship, other_ships_ids):
        operatedRadarStation = [station for station in my_ship.stations.radars if station.operator is not None]
        for radar_station in operatedRadarStation:
            actions.append(RadarScanAction(radar_station.id, random.choice(other_ships_ids)))

    def helm_actions(self, actions, my_ship):
        operatedHelmStation = [station for station in my_ship.stations.helms if station.operator is not None]
        if operatedHelmStation:
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

    def crewmate_dispatcher(self, actions, my_ship):
        wantedStations = ["turrets", "helms", "radars", "shields", "turrets", "turrets", "shields", "turrets"]
        usedStations = []
        idle_crewmates = [crewmate for crewmate in my_ship.crew if crewmate.currentStation is None and crewmate.destination is None]
        for idle_crewmate in idle_crewmates:
            availableStations = self.getCrewmateAvailableStations(idle_crewmate)
            fields = dataclasses.fields(availableStations)
            for wantedStation in wantedStations:
                for field in fields:
                    if (getattr(availableStations, wantedStation) != []):
                        i = 0
                        try:
                            while(getattr(availableStations, wantedStation)[i].stationId in usedStations):
                                i = i + 1
                        except:
                            continue
                        actions.append(CrewMoveAction(idle_crewmate.id, getattr(availableStations, wantedStation)[i].stationPosition))
                        usedStations.append(getattr(availableStations, wantedStation)[i].stationId)
                        wantedStations.remove(wantedStation)
                        break

    def getCrewmateAvailableStations(self, crewmate):
        availableStations = []
        if (crewmate.distanceFromStations.turrets != []):
            availableStations.append("turrets")
        if (crewmate.distanceFromStations.shields != []):
            availableStations.append("shields")
        if (crewmate.distanceFromStations.radars != []):
            availableStations.append("radars")
        if (crewmate.distanceFromStations.helms != []):
            availableStations.append("helms")
        return crewmate.distanceFromStations