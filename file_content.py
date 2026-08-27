class Hub:
    def __init__(self, name: str, coordinates: tuple[int, int]) -> None:
        self.coordinates: tuple[int, int] = coordinates
        self.name: str = name


class FileContent:
    def __init__(self) -> None:
        self.nb_drones: int
        self.start_hub: Hub
        self.end_hub: Hub
