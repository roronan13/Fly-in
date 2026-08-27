import sys

from file_content import FileContent
from file_content import Hub


# class BadParsing(Exception):


def check_hubs_lines(line: str) -> tuple[bool, tuple[str, tuple[int, int]]]:
    valid_line: bool = False

    splited_line: list[str]
    splited_line = line.split(" ")
    if len(splited_line) < 4:
        print("Not enough data for start_hub line !\n")
        return (False, ("NO-NAME", (-1, -1)))

    hub_name: str
    try:
        hub_name = splited_line[1]
        valid_line = True
    except ValueError as e:
        print(f"Start_hub must have a valid name ! \n{e}\n")

    try:
        coordinates: tuple[int, int] = (splited_line[2], splited_line[3])
        valid_line = True
    except ValueError as e:
        print(f"Start_hub must have valid int coordinates ! \n{e}\n")
        valid_line = False

    transformed_line = (valid_line, (hub_name, (coordinates)))
    return (transformed_line)


def parsing_entry(file: str, my_file_content: FileContent) -> bool:

    try:
        with open(file, "r") as file_opened:
            lines_list: list[str] = file_opened.readlines()

            if not lines_list:
                print("Empty File !\n")
                return (False)

            # for line in lines_list:
            #     print(f"{line}", end="")

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

            nb_of_start_hub: int = 0
            for line in lines_list:
                if line.startswith("start_hub:"):
                    start_hub_string: str = line
                    nb_of_start_hub += 1

            if nb_of_start_hub != 1:
                print("Only one start_hub !\n")
                return (False)

            start_hub_result: tuple[bool, tuple[str, tuple[int, int]]] = check_hubs_lines(start_hub_string)
            if not start_hub_result[0]:
                print("Wrong syntax for start_hub !\n")
                return (False)

            else:
                start_hub: Hub = Hub(start_hub_result[1][0], start_hub_result[1][1])

            my_file_content.start_hub = start_hub

            return (True)

    except (FileNotFoundError, PermissionError) as e:
        print(f"{e}\n")
        return (False)
