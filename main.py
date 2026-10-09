import sys

from parsing.parsing import parsing_entry
from file_content import FileContent
from file_content import Drone, Hub, Connection
from pathfinder.dijkstra import dijkstra, can_go_to_hub


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("NO FILE.\n")
        sys.exit()

    my_file_content: FileContent = FileContent()

    if not parsing_entry(sys.argv[1], my_file_content):
        print("END.\n")
        sys.exit()
    
    for i in range(my_file_content.nb_drones):
        drone: Drone = Drone(i, my_file_content.start_hub)
        my_file_content.drones_list.append(drone)
    my_file_content.start_hub.max_drones = my_file_content.nb_drones
    my_file_content.end_hub.max_drones = my_file_content.nb_drones
    
    print(f"nb_drones : {len(my_file_content.drones_list)}")
    for drone in my_file_content.drones_list:
        print(f"{drone.id}")

    # for hub in my_file_content.hubs_list:
    #     print(f"\n\n{hub.name} {hub.coordinates} zone_type: {hub.zone}, color: {hub.color}, max_drones: {hub.max_drones}")
    #     print(f"connected to {len(hub.connections_list)}")
    #     for connection in hub.connections_list:
    #         print(f"{connection.destination.name} (max_link_capacity : {connection.capacity})")

    shortest_path: list[Hub] = dijkstra(my_file_content)
    print("")
    for hub in shortest_path:
        print(f"{hub.name}")

    for drone in my_file_content.drones_list:
        drone.path = shortest_path

    print("")
    my_file_content.start_hub.drones_occupation = my_file_content.nb_drones
    i: int = 1
    while not my_file_content.end_hub.drones_occupation == my_file_content.nb_drones:
    # for i in range(10):
        print(f"\n--- TURN {i} ---")

        # liste temporaire des deplacements envisages a ce tour
        potential_movements = []

                        # FAIRE AVANCER LES DRONES DEJA EN TRANSIT 

        # on examine chaque drone pour savoir s'il est en transit 
        for drone in my_file_content.drones_list:

            if drone.is_in_transition:
                # on diminue le nombre de tours restants avant son arrivee
                drone.remaining_turns -= 1

                # lorsque le compteur atteint 0 le drone doit arriver
                if drone.remaining_turns == 0:
                    # on recupere le hub de destination et la connection que le drone occupe pendant son transit
                    destination: Hub = drone.destination
                    connection: Connection = drone.current_connection

                    # le drone libere la connection : on diminue son occupation et on le retire de la liste
                    connection.drones_occupation -= 1
                    connection.present_drones_list.remove(drone)

                    # le drone arrive a sa destination
                    drone.current_hub = destination
                    destination.drones_occupation += 1
                    destination.present_drones_list.append(drone)

                    # le drone n'est plus en transition : on efface les informations 
                    drone.is_in_transition = False
                    drone.destination = None
                    drone.current_connection = None

                    print(f"Drone {drone.id} arrive a {destination.name}")

                        # IDENTIFIER LES DEPLACEMENTS ENVISAGEABLES

            print(f"Drone {drone.id} : {drone.current_hub.name}, path_index={drone.path_index}")

            # si le drone nest pas encore arrive a la fin 
            if drone.path_index < len(drone.path) - 1:
                next_hub: Hub = drone.path[drone.path_index + 1]

                print(f" veut aller vers {next_hub.name}")

                connection: Connection = None

                # on recherche la connection entre le hub actuel et le prochain hub 
                for found_connection in drone.current_hub.connections_list:
                    if found_connection.destination is next_hub:
                        connection = found_connection
                        break

                print(f"connection trouvee : capacite : {connection.capacity}")

                # if can_go_to_hub(next_hub, my_file_content):
                # on memorise le deplacement envisage : les capacites seront verifies pour l'ensemble des mouvements
                potential_movements.append((drone, next_hub, connection))
                    # drone.path_index += 1
                    # drone.current_hub.drones_occupation -= 1
                    # drone.current_hub = next_hub
                    # next_hub.drones_occupation += 1

        # ce dict associe chaque hub au nombre de drones qui envisagent de le quitter pendant ce tour 
        departures = {}

        for drone, next_hub, connection in potential_movements:
            # le hub de depart du mouvement est le hub actuel du drone 
            former_hub = drone.current_hub

            if former_hub not in departures:
                departures[former_hub] = 0

            departures[former_hub] += 1

                        # VERIFIER LES CAPACITES DES HUBS ET DES CONNECTIONS 

        # continent les mouvements acceptes 
        validated_moves = []

        # nombre de places reservees dans chaque hub par les mouvements acceptes pendant ce tour 
        reserved_spots = {}

        # nombre de passages reserves sur chaque connection par les mouvements acceptes pendant ce tour 
        reserved_connections = {}

        # on verifie chaque mouvement qui est envisage 
        for drone, next_hub, connection in potential_movements:
            # on initialise le compteur 
            if next_hub not in reserved_spots:
                reserved_spots[next_hub] = 0

            if connection not in reserved_connections:
                reserved_connections[connection] = 0

            hub_enough_space: bool = next_hub.drones_occupation + reserved_spots[next_hub] - departures.get(next_hub, 0) < next_hub.max_drones

            connection_enough_space: bool = reserved_connections[connection] < connection.capacity

            if hub_enough_space and connection_enough_space:
                validated_moves.append((drone, next_hub, connection))
                reserved_spots[next_hub] += 1
                reserved_connections[connection] += 1
                # next_hub.drones_occupation += 1

        for drone, next_hub, connection in validated_moves:
            former_hub = drone.current_hub

            drone.path_index += 1
            former_hub.drones_occupation -= 1
            drone.current_hub = next_hub
            next_hub.drones_occupation += 1

            print("")
            print(f"Drone {drone.id} va vers {next_hub.name}")

        i += 1

    sys.exit()
