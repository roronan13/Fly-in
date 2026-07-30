import sys

from file_content import FileContent


# class BadParsing(Exception):


def parsing_entry(file: str, my_file_content: FileContent) -> bool:

    try:
        with open(file, "r") as file_opened:
            lines_list: list[str] = file_opened.readlines()
        
            if not lines_list:
                print("Empty File !\n")
                return (False)

            for line in lines_list:
                print(f"{line}", end="")

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


            return (True)
    
    except (FileNotFoundError, PermissionError) as e:
        print(f"{e}\n")
        return (False)
