import hlt
import logging


game = hlt.Game("Robbot")

logging.info("Initialising Robbot...")

while True:
    #TURN START

    game_map = game.update_map()
    command_queue = []
    
    my_id = game_map.my_id
    my_ships = game_map.get_me().all_ships()
    for ship in my_ships:
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            continue
    
        entities_distance = game_map.nearby_entities_by_distance(ship)
        distances = []
        entities = []
        for entity in entities_distance:
            distances.append(entity)
            entities.append(entities_distance[entity])
            
        sorted_distances = []
        sorted_entities = []
        for i in range(len(distances)):
            min_i = distances.index(min(distances))
            sorted_distances.append(distances.pop(min_i))
            sorted_entities.append(entities.pop(min_i))

            
        closest_empty_planets = []
        closest_enemy_ships = []
        for i in range(len(sorted_entities)):
            entity = sorted_entities[i][0]
            if isinstance(entity, hlt.entity.Planet):
                if not entity.is_owned():
                    closest_empty_planets.append(entity)
                else:
                    if entity.owner.id == my_id and not entity.is_full():
                        closest_empty_planets.append(entity)
                continue
            
            if isinstance(entity, hlt.entity.Ship) and not entity in my_ships:
                closest_enemy_ships.append(entity)

        if len(closest_empty_planets) > 0:
            target_planet = closest_empty_planets[0]
            if ship.can_dock(target_planet):
                command_queue.append(ship.dock(target_planet))
            else:
                navigate_command = ship.navigate(
                    ship.closest_point_to(target_planet),
                    game_map,
                    speed=int(hlt.constants.MAX_SPEED),
                    ignore_ships=False)
                if navigate_command:
                    command_queue.append(navigate_command)
                
        elif len(closest_enemy_ships) > 0:
            target_ship = closest_enemy_ships[0]
            navigate_command = ship.navigate(
                    target_ship,
                    game_map,
                    speed=int(hlt.constants.MAX_SPEED),
                    ignore_ships=False)
            if navigate_command:
                command_queue.append(navigate_command)
    game.send_command_queue(command_queue)
            
            
            
        
