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
