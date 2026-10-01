from file_content import Hub


def get_cost(hub: Hub) -> int:
    if hub.zone == "blocked":
        return -1
    if hub.zone == "restricted":
        return 2
    else:
        return 1
