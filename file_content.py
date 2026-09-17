import sys


class Hub:
    def __init__(self, name: str, coordinates: tuple[int, int], meta_data: list[str]) -> None:
        self.coordinates: tuple[int, int] = coordinates
        self.name: str = name
        self.meta_data: list[str] = meta_data
        self.connections_list: list[tuple[Hub, int]] = []# ??
        nb_zone: int = 0
        nb_color: int = 0
        nb_max_drones: int = 0

        if len(meta_data) == 0:
            self.zone: str = "normal"
            self.color: str = "none"
            self.max_drones: int = 1
        else:
            test_multiple_equals: list[str] = []
            for one_meta_data in meta_data:
                if one_meta_data.startswith("zone="):
                    test_multiple_equals = one_meta_data.split("=")
                    if len(test_multiple_equals) != 2:
                        print(f"{self.name} : wrong syntax for meta_data !\n")
                        sys.exit()
                    received_zone_type: str = one_meta_data.split("=")[1]
                    # if received_zone_type == "":

                    #     sys.exit()
                    if received_zone_type not in ["normal", "blocked", "restricted", "priority"]:
                        print(f"{self.name} : zone type for hubs must be either normal, blocked, restricted or priority ! \n")
                        sys.exit()
                    self.zone: str = received_zone_type
                    nb_zone += 1
                elif nb_zone == 0:
                    self.zone = "normal"
                if one_meta_data.startswith("color="):
                    test_multiple_equals = one_meta_data.split("=")
                    if len(test_multiple_equals) != 2:
                        print(f"{self.name} : wrong syntax for meta_data !\n")
                        sys.exit()
                    self.color: str = one_meta_data.split("=")[1]
                    if self.color == "":
                        print(f"{self.name} : color must be specified !\n")
                        sys.exit()
                    nb_color += 1
                elif nb_color == 0:
                    self.color = "none"
                if one_meta_data.startswith("max_drones="):
                    test_multiple_equals = one_meta_data.split("=")
                    if len(test_multiple_equals) != 2:
                        print(f"{self.name} : wrong syntax for meta_data !\n")
                        sys.exit()
                    try:
                        self.max_drones: int = int(one_meta_data.split("=")[1])
                        if self.max_drones < 0:
                            print(f"{self.name} : max_drones must be a positive int ! \n")
                            sys.exit()
                        nb_max_drones += 1
                    except ValueError as e:
                        print(f"{self.name} : max_drones in meta_data must be an int ! \n{e}\n")
                        sys.exit()
                elif nb_max_drones == 0:
                    self.max_drones = 1


class FileContent:
    def __init__(self) -> None:
        self.nb_drones: int
        self.start_hub: Hub
        self.end_hub: Hub
        self.hubs_list: list[Hub] = []
