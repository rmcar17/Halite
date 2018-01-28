import hlt
import logging
from time import time

#SETUP

def get_entities_and_distance(ship, game_map):
    entities_distance = game_map.nearby_entities_by_distance(ship)
    distances = []
    entities = []
    for entity in entities_distance:
        distances.append(entity)
        entities.append(entities_distance[entity])
    return [distances,entities]

def sort_entities_by_distance(distance, entity):
    sorted_distances = []
    sorted_entities = []
    for i in range(len(distance)):
        min_i = distance.index(min(distance))
        sorted_distances.append(distance.pop(min_i))
        sorted_entities.append(entity.pop(min_i))
    return [sorted_distances, sorted_entities]

def get_empty_planets_and_enemy_ships(entities):
    closest_empty_planets = []
    closest_enemy_ships = []
    for i in range(len(entities)):
        entity = entities[i][0]
        if isinstance(entity, hlt.entity.Planet):
            if not entity.is_owned() or (entity.owner.id == my_id and not entity.is_full()):
                closest_empty_planets.append(entity)
            continue
        if isinstance(entity, hlt.entity.Ship) and not entity in my_ships:
            closest_enemy_ships.append(entity)
    return [closest_empty_planets,closest_enemy_ships]

def get_command(ship, closest_empty_planets, closest_enemy_ships,planned_planets):
    if len(closest_empty_planets) > 0:
        count = 0
        for planet in closest_empty_planets:
            count += 1
            target_planet = planet
            if planned_planets[target_planet] > 0:
                planned_planets[target_planet] -= 1
                break
        con = True
        if count == len(closest_empty_planets):
            con = False
        if ship.can_dock(target_planet) and con:
            return [ship.dock(target_planet),planned_planets]
        else:
            navigate_command = ship.navigate(
                ship.closest_point_to(target_planet),
                game_map,
                speed=int(hlt.constants.MAX_SPEED),
                ignore_ships=False)
            if navigate_command and con:
                return [navigate_command,planned_planets]
            
    if len(closest_enemy_ships) > 0:
        target_ship = closest_enemy_ships[0]
        navigate_command = ship.navigate(
                ship.closest_point_to(target_ship),
                game_map,
                speed=int(hlt.constants.MAX_SPEED),
                ignore_ships=False)
        if navigate_command:
            return [navigate_command, planned_planets]
    return [None, planned_planets]

#START GAME
game = hlt.Game("Settler")

logging.info("Initialising Robbot...")

while True:
    #TURN START
    start_turn = time()
    
    game_map = game.update_map()
    command_queue = []
    
    my_id = game_map.my_id
    my_ships = game_map.get_me().all_ships()
    
    planned_planets = {}
    for planet in game_map.all_planets():
        planned_planets[planet] = planet.num_docking_spots-len(planet._docked_ship_ids)

    logging.info(planned_planets)
    
    for ship in my_ships:
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            continue
    
        distance_entities = get_entities_and_distance(ship, game_map)

        sorted_distance_entities = sort_entities_by_distance(distance_entities.pop(0),distance_entities.pop(0))
        sorted_distances = sorted_distance_entities.pop(0)
        sorted_entities = sorted_distance_entities.pop(0)

        objects_of_interest = get_empty_planets_and_enemy_ships(sorted_entities)        

        command = get_command(ship, objects_of_interest.pop(0), objects_of_interest.pop(0),planned_planets)
        logging.info(command[0])
        if command[0]:
            command_queue.append(command[0])
        planned_planets = command[1]

        if (time()-start_turn) > 1.8:
            break
    game.send_command_queue(command_queue)
            
            
            
        
