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

        movements = []

        for drone in my_file_content.drones_list:

            print(f"Drone {drone.id} : {drone.current_hub.name}, path_index={drone.path_index}")

            if drone.path_index < len(drone.path) - 1:
                next_hub: Hub = drone.path[drone.path_index + 1]

                print(f" veut aller vers {next_hub.name}")

                connection: Connection = None

                for found_connection in drone.current_hub.connections_list:
                    if found_connection.destination is next_hub:
                        connection = found_connection
                        break

                print(f"connection trouvee : capacite : {connection.capacity}")

                # if can_go_to_hub(next_hub, my_file_content):
                movements.append((drone, next_hub, connection))
                    # drone.path_index += 1
                    # drone.current_hub.drones_occupation -= 1
                    # drone.current_hub = next_hub
                    # next_hub.drones_occupation += 1

        departures = {}

        for drone, next_hub, connection in movements:
            former_hub = drone.current_hub

            if former_hub not in departures:
                departures[former_hub] = 0

            departures[former_hub] += 1

        accepted_moves = []
        reserved_spots = {}

        for drone, next_hub, connection in movements:
            if next_hub not in reserved_spots:
                reserved_spots[next_hub] = 0

            if next_hub.drones_occupation + reserved_spots[next_hub] - departures.get(next_hub, 0) < next_hub.max_drones:
                accepted_moves.append((drone, next_hub, connection))
                reserved_spots[next_hub] += 1
                # next_hub.drones_occupation += 1

        for drone, next_hub, connection in accepted_moves:
            former_hub = drone.current_hub

            drone.path_index += 1
            former_hub.drones_occupation -= 1
            drone.current_hub = next_hub
            next_hub.drones_occupation += 1

            print(f"Drone {drone.id} va vers {next_hub.name}")

        i += 1

    sys.exit()
