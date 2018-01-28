import hlt
import logging
from time import time

#SETUP

class Bot:
    def __init__(self, entity, my_id, myShips):
        self.ship = entity
        
        self.playerID = my_id
        self.teamShips = myShips
        
    def findNearbyEntities(self, gameMap):
        self.entitiesDistance = gameMap.nearby_entities_by_distance(self.ship)
        
    def sortNearbyEntities(self):
        self.planetsOfInterest = []
        self.closestShip = None
        tempSortedEntities = sorted(self.entitiesDistance)
        found = False
        for distance in tempSortedEntities:
            entity = self.entitiesDistance[distance][0]
            if self.isPlanet(entity, self.playerID):
                
                self.planetsOfInterest.append((entity, distance)) 
            if self.isShip(entity, self.playerID, self.teamShips) and not found:
                found = True
                self.closestShip = (entity, distance)

    def getPriorities(self, gameMap):
        self.findNearbyEntities(gameMap)
        self.sortNearbyEntities()
        self.priorities = self.planetsOfInterest
        self.priorities.append(self.closestShip)
        if self.closestShip[1] < 25:
            self.priorities.reverse()
        return self.priorities


    def isPlanet(self, entity, myID):
        if isinstance(entity, hlt.entity.Planet):
            return (not entity.is_owned() or (entity.owner.id == myID and not entity.is_full()))
        return False
    
    def isShip(self,entity, myID, teamShips):
        return isinstance(entity, hlt.entity.Ship) and not entity in teamShips

class BotController:
    def __init__(self):
        self.game = hlt.Game("Settler")

        self.command_queue = []
        
    def update(self):
        self.start = time()
        self.gameMap = self.game.update_map()
        self.myID = self.gameMap.my_id
        self.myBots = []
        self.command_queue = []
        
    def getShips(self):
        myShips = []
        
        for ship in self.gameMap.get_me().all_ships():
            myShips.append(ship)

        return myShips

    def createBots(self):
        ships = self.getShips()
        self.myBots = []
        for bot in ships:
            self.myBots.append(Bot(bot,self.myID,ships))

    def getBotPriorities(self):
        botPriorities = {}
        for bot in self.myBots:
            botPriorities[bot.ship] = bot.getPriorities(self.gameMap)
        return self.sortBotPriorities(botPriorities)

    def sortBotPriorities(self, botPriorities):
        tempBotPriorities = sorted(botPriorities, key = lambda bot:botPriorities[bot][0][1])
        finalBotPriorities = {}
        for bot in tempBotPriorities:
            finalBotPriorities[bot] = botPriorities[bot]
        return finalBotPriorities

    def getPlanetSpaces(self):
        planetSpaces = {}
        for planet in self.gameMap.all_planets():
            planetSpaces[planet] = planet.num_docking_spots-len(planet._docked_ship_ids)
        return planetSpaces

    def getCommands(self):        
        priorities = self.getBotPriorities()
        planetSpaces = self.getPlanetSpaces()
        for bot in priorities:
            if bot.docking_status != bot.DockingStatus.UNDOCKED:
                continue
            navigateCommand = None
            for preference in priorities[bot]:
                target = preference[0]
                if self.isPlanet(target):
                    if bot.can_dock(target):
                        planetSpaces[target] -= 1
                        navigateCommand = bot.dock(target)
                        break
                    if planetSpaces[target] > 0:
                        planetSpaces[target] -= 1
                        navigateCommand = bot.navigate(
                            bot.closest_point_to(target),
                            self.gameMap,
                            speed=int(hlt.constants.MAX_SPEED),
                            ignore_ships=False)
                        break
                else:
                    #Attack Ship Code
                    navigateCommand = bot.navigate(
                            bot.closest_point_to(target),
                            self.gameMap,
                            speed=int(hlt.constants.MAX_SPEED),
                            ignore_ships=False)
                    break
            if navigateCommand:
                self.command_queue.append(navigateCommand)
                
    def sendCommands(self):
        logging.info(self.start-time())
        self.game.send_command_queue(self.command_queue)
        

    def isPlanet(self,entity):
        return isinstance(entity, hlt.entity.Planet)

#START GAME
Controller = BotController()

logging.info("Initialising Robbot...")


while True:
    Controller.update()
    Controller.createBots()
    Controller.getCommands()
    Controller.sendCommands()
                
            
            
        
