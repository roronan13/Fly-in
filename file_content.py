class Hub:
    def __init__(self, name: str, coordinates: tuple[int, int], meta_data: list[str]) -> None:
        self.coordinates: tuple[int, int] = coordinates
        self.name: str = name
        self.meta_data = []


class FileContent:
    def __init__(self) -> None:
        self.nb_drones: int
        self.start_hub: Hub
        self.end_hub: Hub
        self.hubs_list: list[Hub] = []
