import sys


class Hub:
    def __init__(self, name: str, coordinates: tuple[int, int], meta_data: list[str]) -> None:
        self.coordinates: tuple[int, int] = coordinates
        self.name: str = name
        self.meta_data: list[str] = meta_data
        self.connections_list: list = [Hub] # ??
        nb_zone: int = 0
        nb_color: int = 0
        nb_max_drones: int = 0

        if len(meta_data) == 0:
            self.zone = "normal"
            self.color = "none"
            self.max_drones = 1
        else:
            for one_meta_data in meta_data:
                if one_meta_data.startswith("zone="):
                    self.zone: str = one_meta_data.split("=")[1]
                    nb_zone += 1
                elif nb_zone == 0:
                    self.zone = "normal"
                if one_meta_data.startswith("color="):
                    self.color: str = one_meta_data.split("=")[1]
                    nb_color += 1
                elif nb_color == 0:
                    self.color = "none"
                if one_meta_data.startswith("max_drones="):
                    try:
                        self.max_drones: int = int(one_meta_data.split("=")[1])
                        if self.max_drones < 0:
                            print("max_drones must be a positive int ! \n")
                            sys.exit()
                        nb_max_drones += 1
                    except ValueError as e:
                        print(f"max_drones in meta_data must be an int ! \n{e}\n")
                        sys.exit()
                elif nb_max_drones == 0:
                    self.max_drones = 1


class FileContent:
    def __init__(self) -> None:
        self.nb_drones: int
        self.start_hub: Hub
        self.end_hub: Hub
        self.hubs_list: list[Hub] = []
