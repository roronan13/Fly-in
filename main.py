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

    # my_file_content.hubs_list.append(my_file_content.start_hub)
    # my_file_content.hubs_list.append(my_file_content.end_hub)

    # print(f"{len(my_file_content.hubs_list)}")
    # for hub in my_file_content.hubs_list:
    #                         print(f"{hub.name}")

    # print(f"{my_file_content.nb_drones}\n")
    # print(f"{my_file_content.start_hub.name}")
    # print(f"{my_file_content.start_hub.coordinates}")
    # print(f"{my_file_content.start_hub.zone}")
    # print(f"{my_file_content.start_hub.color}")
    # print(f"{my_file_content.start_hub.max_drones}\n")
    # print(f"{my_file_content.end_hub.name}")
    # print(f"{my_file_content.end_hub.coordinates}")
    # print(f"{my_file_content.end_hub.zone}")
    # print(f"{my_file_content.end_hub.color}")
    # print(f"{my_file_content.end_hub.max_drones}\n")
    for hub in my_file_content.hubs_list:
        print(f"\n{hub.name} {hub.coordinates} {hub.zone} {hub.color} {hub.max_drones}")
        print(f"{len(hub.connections_list)}")
        for connected_hub in hub.connections_list:
            print(f"{connected_hub.name}")

    sys.exit()
