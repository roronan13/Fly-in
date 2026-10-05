import sys

from parsing.parsing import parsing_entry
from file_content import FileContent
from file_content import Drone, Hub
from pathfinder.dijkstra import dijkstra


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("NO FILE.\n")
        sys.exit()

    my_file_content: FileContent = FileContent()

    if not parsing_entry(sys.argv[1], my_file_content):
        print("END.\n")
        sys.exit()

    # my_file_content.hubs_list.append(my_file_content.start_hub)
    # my_file_content.hubs_list.append(my_file_content.end_hub)

    # print(f"{len(my_file_content.hubs_list)}")
    # for hub in my_file_content.hubs_list:
    #                         print(f"{hub.name}")

    # print(f"{my_file_content.nb_drones}\n")
    # print(f"{my_file_content.start_hub.name}")
    # print(f"{my_file_content.start_hub.coordinates}")
    # print(f"{my_file_content.start_hub.zone}")
    # print(f"{my_file_content.start_hub.color}")
    # print(f"{my_file_content.start_hub.max_drones}\n")
    # print(f"{my_file_content.end_hub.name}")
    # print(f"{my_file_content.end_hub.coordinates}")
    # print(f"{my_file_content.end_hub.zone}")
    # print(f"{my_file_content.end_hub.color}")
    # print(f"{my_file_content.end_hub.max_drones}\n")
    for i in range(my_file_content.nb_drones):
        drone: Drone = Drone(i, my_file_content.start_hub)
        my_file_content.drones_list.append(drone)
    print(f"nb_drones : {len(my_file_content.drones_list)}")
    for drone in my_file_content.drones_list:
        print(f"{drone.id}")

    for hub in my_file_content.hubs_list:
        print(f"\n\n{hub.name} {hub.coordinates} zone_type: {hub.zone}, color: {hub.color}, max_drones: {hub.max_drones}")
        print(f"connected to {len(hub.connections_list)}")
        for connection in hub.connections_list:
            print(f"{connection.destination.name} (max_link_capacity : {connection.capacity})")

    # shortest_path: list[Hub] = dijkstra(my_file_content)

    sys.exit()
