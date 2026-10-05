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
    shortest_cost["start"] = 0

    current_hub: Hub = my_file_content.start_hub

    for connection in current_hub.connections_list:
        neighbour: Hub = connection.destination

        if get_cost(neighbour) == -1:
            continue

        new_cost: int = shortest_cost[current_hub.name] + get_cost(neighbour)

        if new_cost < shortest_cost[neighbour.name]:
            shortest_cost[neighbour.name] = new_cost

    current_hub.been_visited = True

    