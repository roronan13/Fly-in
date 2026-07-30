import sys

from parsing.parsing import parsing_entry
from file_content import FileContent


if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("NO FILE.\n")
        sys.exit()

    my_file_content: FileContent = FileContent()

    if not parsing_entry(sys.argv[1], my_file_content):
        print("END.\n")
        sys.exit()

    print(f"{my_file_content.nb_drones}\n")
    print("OKAY.\n")

    sys.exit()
