import sys
from parsing.parsing import parsing_entry


if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("NO FILE.\n")
        sys.exit()

    parsing_entry(sys.argv[1])

