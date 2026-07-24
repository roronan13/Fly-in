import sys


def parsing_entry(file: str) -> bool:

    try:
        open(file)
        print("opened.\n")
        return (True)
    
    except (FileNotFoundError, PermissionError) as e:
        print(f"{e}\n")
        return (False)
    
