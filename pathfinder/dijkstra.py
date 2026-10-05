import sys
from file_content import Hub, Connection, Drone, FileContent


def get_cost(hub: Hub) -> int:
    if hub.zone == "blocked":
        return -1
    if hub.zone == "restricted":
        return 2
    else:
        return 1


def dijkstra(my_file_content: FileContent) -> list[Hub]:
    shortest_cost: dict = {}
    for hub in my_file_content.hubs_list:
        shortest_cost[hub.name] = float("inf")
    shortest_cost[my_file_content.start_hub.name] = 0

    current_hub: Hub = my_file_content.start_hub
    previous_for_path: dict = {}

    while current_hub is not None:
        for connection in current_hub.connections_list:
            neighbour: Hub = connection.destination

            if get_cost(neighbour) == -1:
                continue

            new_cost: int = shortest_cost[current_hub.name] + get_cost(neighbour)

            if new_cost < shortest_cost[neighbour.name]:
                shortest_cost[neighbour.name] = new_cost
                previous_for_path[neighbour.name] = current_hub

        current_hub.been_visited = True

        next_hub: Hub | None = None

        for hub in my_file_content.hubs_list:
            if not hub.been_visited and shortest_cost[hub.name] != float("inf"):
                if next_hub is None or shortest_cost[hub.name] < shortest_cost[next_hub.name]:
                    next_hub = hub

        if next_hub is None:
            break

        current_hub = next_hub

    if not my_file_content.end_hub.been_visited:
        print("There is no possible from start to end in this configuration !\n")
        sys.exit()

    shortest_path: list[Hub] = []
    current_hub = my_file_content.end_hub
    while current_hub is not my_file_content.start_hub:
        shortest_path.append(current_hub)
        current_hub = previous_for_path[current_hub.name]

    shortest_path.append(my_file_content.start_hub)
    shortest_path.reverse()

    return shortest_path
