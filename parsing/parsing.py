import sys

from file_content import FileContent
from file_content import Hub

# l = ""
# if ("#") in l:
#     l = l[:l.index("#")].strip()

# class BadParsing(Exception):


def check_hubs_lines(line: str) -> tuple[bool, tuple[str, tuple[int, int], list[str]]]:
    valid_line: bool = False

    splited_line: list[str]
    splited_line = line.split(" ")
    if len(splited_line) != 5:
        print(f"Wrong number of data for {line} !\n")
        return (False, ("NO-NAME", (-1, -1), ["NO-META-DATA"]))

    hub_name: str
    try:
        hub_name = str(splited_line[1])
        valid_line = True
    except ValueError as e:
        print(f"{line} must have a valid name ! \n{e}\n")
        hub_name = "NO_NAME"

    try:
        coordinates: tuple[int, int] = (int(splited_line[2]), int(splited_line[3]))
        coordinates[0] > -1
        coordinates[1] > -1
        valid_line = True
    except ValueError as e:
        print(f"{line} must have valid int coordinates ! \n{e}\n")
        coordinates = (-1, -1)
        valid_line = False

    # if coordinates[0] < 0 or coordinates[1] < 0:
    #     print("Coordinates must be positive int !\n")
    #     valid_line = False

    if ("[") in line and ("]") in line:
        valid_meta_data: str
        meta_datas_list: list[str] = []
        meta_data_section: str = line[:line.index("[")].strip("[]")
        splited_meta_data_section: list[str] = meta_data_section.split(" ")
        for meta_data in splited_meta_data_section:
            if meta_data.startswith("color=") or meta_data.startswith("zone=") or meta_data.startswith("max_drones="):
                valid_meta_data = meta_data
                meta_datas_list.append(valid_meta_data)

                nb_color: int = 0
                if meta_data.startswith("color="):
                    nb_color += 1
                nb_zone: int = 0
                if meta_data.startswith("zone="):
                    nb_zone += 1
                nb_max_drones: int = 0
                if meta_data.startswith("nb_max_drones="):
                    nb_max_drones += 1

        if nb_color > 1 or nb_zone > 1 or nb_max_drones > 1:
            print(f"Wrong meta-data syntax for {line} !\n")
            return (False, ("NO-NAME", (-1, -1), ["NO-META-DATA"]))

    else:
        print(f"No meta-data for {line} !\n")
        return (False, ("NO-NAME", (-1, -1), ["NO-META-DATA"]))

    transformed_line = (valid_line, (hub_name, coordinates, meta_datas_list))
    return (transformed_line)


def parsing_entry(file: str, my_file_content: FileContent) -> bool:

    try:
        with open(file, "r") as file_opened:
            lines_list: list[str] = file_opened.readlines()

            if not lines_list:
                print("Empty File !\n")
                return (False)

# check nb drones
            nb_drones_line = lines_list[0].strip()
            if nb_drones_line.startswith("#"):
                nb_drones_line = lines_list[1].strip()

            if nb_drones_line.startswith("nb_drones: "):
                try:
                    nb_drones: int = int(nb_drones_line.split(": ")[1])
                    if nb_drones < 0:
                        print("Negative nb_drones !\n")
                    my_file_content.nb_drones = nb_drones
                except ValueError as e:
                    print(f"nb_drones must be int ! \n{e}\n")
                    return (False)

            else:
                print("Syntax nb_drones: <int> !\n")
                return (False)

# check start hub
            nb_of_start_hub: int = 0
            for line in lines_list:
                if line.startswith("start_hub:"):
                    start_hub_string: str = line
                    nb_of_start_hub += 1

            if nb_of_start_hub != 1:
                print("Only one start_hub !\n")
                return (False)

            start_hub_result: tuple[bool, tuple[str, tuple[int, int], list[str]]] = check_hubs_lines(start_hub_string)
            if not start_hub_result[0]:
                print("Wrong syntax for start_hub !\n")
                return (False)

            else:
                start_hub: Hub = Hub(start_hub_result[1][0], start_hub_result[1][1], start_hub_result[1][2])

# check end hub
            nb_of_end_hub: int = 0
            for line in lines_list:
                if line.startswith("end_hub:"):
                    end_hub_string: str = line
                    nb_of_end_hub += 1

            if nb_of_end_hub != 1:
                print("Only one end_hub !\n")
                return (False)

            end_hub_result: tuple[bool, tuple[str, tuple[int, int]], list[str]] = check_hubs_lines(end_hub_string)
            if not end_hub_result[0]:
                print("Wrong syntax for end_hub !\n")
                return (False)

            else:
                end_hub: Hub = Hub(end_hub_result[1][0], end_hub_result[1][1], end_hub_result[1][2])

            my_file_content.start_hub = start_hub
            my_file_content.end_hub = end_hub

# check hubs
            for line in lines_list:
                if line.startswith("hub: "):
                    hub_result: tuple[bool, tuple[str, tuple[int, int]], list[str]] = check_hubs_lines(line)

                    if not hub_result[0]:
                        print(f"Wrong syntax for {line} !\n")
                        return (False)
                    else:
                        hub: Hub = Hub(hub_result[1][0], hub_result[1][1], hub_result[1][2])
                        my_file_content.hubs_list.append(hub)

            return (True)

    except (FileNotFoundError, PermissionError) as e:
        print(f"{e}\n")
        return (False)
