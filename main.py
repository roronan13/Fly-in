import sys

from parsing.parsing import parsing_entry
from file_content import FileContent
from file_content import Drone, Hub, Connection
from pathfinder.dijkstra import dijkstra


def get_final_occupation(hub: Hub, validated_moves: list[tuple[Drone, Hub, Connection]], arrivals_by_hub: dict[Hub, int]) -> int:
    occupation: int = hub.drones_occupation
    occupation += arrivals_by_hub.get(hub, 0)

    for drone, next_hub, connection in validated_moves:
        if drone.current_hub is hub:
            occupation -= 1
        if next_hub is hub and next_hub.zone != "restricted":
            occupation += 1

    return occupation


def can_leave_next_turn(hub: Hub, validated_moves: list[tuple[Drone, Hub, Connection]], arrivals_by_hub: dict[Hub, int], my_file_content: FileContent, visited: set[Hub] | None = None) -> bool:
    if visited is None:
        visited = set()

    if hub in visited:
        return False

    visited.add(hub)

    # la fin peut toujours accueillir les drones
    if hub is my_file_content.end_hub:
        return True

    # chercher un drone qui sera present dans ce hub
    drones_present: list[Drone] = []

    for drone in hub.present_drones_list:
        if not any(move[0] is drone for move in validated_moves):
            drones_present.append(drone)

    for drone, destination, connection in validated_moves:
        if destination is hub and hub.zone != "restricted":
            drones_present.append(drone)

    for drone in drones_present:
        moved_this_turn = any(moving_drone is drone for moving_drone, destination, connection in validated_moves)

        next_index: int = drone.path_index + (1 if moved_this_turn else 0)
        if next_index >= len(drone.path) - 1:
            continue

        next_hub = drone.path[next_index + 1]

        for connection in hub.connections_list:
            if connection.destination is not next_hub:
                continue
            if connection.capacity <= 0:
                continue
            # si le prochain hub est restricted le drone peut commencer son transit
            if next_hub.zone == "restricted":
                return True

            next_turn_occupation: int = get_final_occupation(next_hub, validated_moves, arrivals_by_hub)
            if next_turn_occupation < next_hub.max_drones:
                return True

            # le prochain hub est plein, peut il lui meme liberer une place ?
            if can_leave_next_turn(next_hub, validated_moves, arrivals_by_hub, my_file_content, visited.copy()):
                return True

    return False


def get_possible_departures(hub: Hub, drones_to_check: list[Drone], validated_moves: list[tuple[Drone, Hub, Connection]], arrivals_by_hub: dict[Hub, int], my_file_content: FileContent) -> int:
    departures: int = 0
    reserved_connections: dict[Connection, int] = {}
    reserved_hubs: dict[Hub, int] = {}

    for drone in drones_to_check:
        if drone.path_index >= len(drone.path) - 1:
            continue

        next_hub: Hub = drone.path[drone.path_index + 1]

        connection: Connection | None = None

        for found_connection in hub.connections_list:
            if found_connection.destination is next_hub:
                connection = found_connection
                break
        if connection is None:
            continue

        # capacite disponible sur la connection au prochain tour
        reserved: int = reserved_connections.get(connection, 0)
        if reserved >= connection.capacity:
            continue

        # occupation du hub de destination apres le tour actuel
        next_turn_occupation: int = get_final_occupation(next_hub, validated_moves, arrivals_by_hub)

        # un depart vers une zone restricted commence un transit : il ne prend pas tout de suite une place dans le hub
        if next_hub.zone != "restricted":
            already_reserved: int = reserved_hubs.get(next_hub, 0)

            if next_turn_occupation + already_reserved >= next_hub.max_drones:
                if not can_leave_next_turn(next_hub, validated_moves, arrivals_by_hub, my_file_content):
                    continue

            reserved_hubs[next_hub] = already_reserved + 1

        reserved_connections[connection] = reserved + 1
        departures += 1

    return departures


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("NO FILE.\n")
        sys.exit()

    my_file_content: FileContent = FileContent()

    if not parsing_entry(sys.argv[1], my_file_content):
        print("END.\n")
        sys.exit()

    for i in range(my_file_content.nb_drones):
        drone: Drone = Drone(i, my_file_content.start_hub)
        my_file_content.drones_list.append(drone)
    my_file_content.start_hub.max_drones = my_file_content.nb_drones
    my_file_content.end_hub.max_drones = my_file_content.nb_drones
    my_file_content.start_hub.drones_occupation = my_file_content.nb_drones

    # print(f"nb_drones : {len(my_file_content.drones_list)}")
    # for drone in my_file_content.drones_list:
    #     print(f"{drone.id}")

    # for hub in my_file_content.hubs_list:
    #     print(f"\n\n{hub.name} {hub.coordinates} zone_type: {hub.zone}, color: {hub.color}, max_drones: {hub.max_drones}")
    #     print(f"connected to {len(hub.connections_list)}")
    #     for connection in hub.connections_list:
    #         print(f"{connection.destination.name} (max_link_capacity : {connection.capacity})")

    shortest_path: list[Hub] = dijkstra(my_file_content)
    for drone in my_file_content.drones_list:
        drone.path = shortest_path
        my_file_content.start_hub.present_drones_list.append(drone)

    print("")
    for hub in shortest_path:
        print(f"{hub.name}")

    print("")

    i: int = 1
    while not my_file_content.end_hub.drones_occupation == my_file_content.nb_drones:
    # for i in range(10):
        print(f"\n--- TURN {i} ---")

        # liste temporaire des deplacements envisages a ce tour
        potential_movements: list[tuple[Drone, Hub, Connection]] = []
        # liste des drones qui doivent arriver a destination pendant ce tour
        arrivals_this_turn: list[tuple[Drone, Hub, Connection]] = []

                        # FAIRE AVANCER LES DRONES DEJA EN TRANSIT --------------------------------------

        # on examine chaque drone pour savoir s'il est en transit
        for drone in my_file_content.drones_list:

            if drone.is_in_transition:
                # on diminue le nombre de tours restants avant son arrivee
                drone.remaining_turns -= 1

                # si le compteur atteint 0 le drone doit arriver
                if drone.remaining_turns == 0:
                    # on recupere le hub de destination et la connection que le drone occupe pendant son transit
                    destination: Hub = drone.destination
                    connection: Connection = drone.current_connection

                    # on enregistre l'arrivee pour la traiter pendant la phase d'execution
                    arrivals_this_turn.append((drone, destination, connection))

                    # # le drone libere la connection : on diminue son occupation et on le retire de la liste
                    # connection.drones_occupation -= 1
                    # connection.present_drones_list.remove(drone)

                    # # le drone arrive a sa destination
                    # drone.current_hub = destination
                    # destination.drones_occupation += 1
                    # destination.present_drones_list.append(drone)

                    # # le drone n'est plus en transition : on efface les informations
                    # drone.is_in_transition = False
                    # drone.destination = None
                    # drone.current_connection = None

                    # print(f"Drone {drone.id} est arrive a {destination.name}")

                    print(f"Drone {drone.id} doit arriver a {destination.name}")

                        # IDENTIFIER LES DEPLACEMENTS ENVISAGEABLES ------------------------------------

            # on ne veut pas qu'un drone en transit commence un autre deplacement
            if drone.is_in_transition:
                continue

            print(f"Drone {drone.id} : {drone.current_hub.name}, path_index={drone.path_index}")

            # si le drone nest pas encore arrive a la fin
            if drone.path_index < len(drone.path) - 1:
                next_hub: Hub = drone.path[drone.path_index + 1]

                print(f" veut aller vers {next_hub.name}")

                connection: Connection | None = None

                # on recherche la connection entre le hub actuel et le prochain hub
                for found_connection in drone.current_hub.connections_list:
                    if found_connection.destination is next_hub:
                        connection = found_connection
                        break

                print(f"connection trouvee : capacite : {connection.capacity}")

                # if can_go_to_hub(next_hub, my_file_content):
                # on memorise le deplacement envisage : les capacites seront verifies pour l'ensemble des mouvements
                potential_movements.append((drone, next_hub, connection))
                    # drone.path_index += 1
                    # drone.current_hub.drones_occupation -= 1
                    # drone.current_hub = next_hub
                    # next_hub.drones_occupation += 1

                        # COMPTER LES CONNECTIONS QUI SERONT LIBEREES --------------------------------------

        # dictionnaire qui compte les drones qui vont arriver dans chaque hub ce tour
        arrivals_by_hub: dict[Hub, int] = {}
        for (drone, destination, connection) in arrivals_this_turn:
            if destination not in arrivals_by_hub:
                arrivals_by_hub[destination] = 0

            arrivals_by_hub[destination] += 1

        for hub, count in arrivals_by_hub.items():
            print(f"Arrivees prevues a {hub.name} : {count}")

        # dictionnaire comptant les places qui vont etre liberees par les drones arrivant a destination pdt ce tour
        connections_being_freed: dict[Connection, int] = {}

        for drone, destination, connection in arrivals_this_turn:
            if connection not in connections_being_freed:
                connections_being_freed[connection] = 0

                # ce drone va liberer une place sur cette connection
            connections_being_freed[connection] += 1

                        # VERIFIER LES CAPACITES DES HUBS ET DES CONNECTIONS ----------------------------

        # selectionner les mouvements que les connections permettent
        candidate_moves: list[tuple[Drone, Hub, Connection]] = []
        reserved_connections: dict[Connection, int] = {}

        for drone, next_hub, connection in potential_movements:
            connection_frees: int = connections_being_freed.get(connection, 0)
            reserved: int = reserved_connections.get(connection, 0)

            # une connection peut etre reutilisee si un drone la libere ce tour
            if connection.drones_occupation + reserved - connection_frees < connection.capacity:
                candidate_moves.append((drone, next_hub, connection))
                reserved_connections[connection] = reserved + 1

        # eliminer les mouvements qui depassent la capacite finale des hubs
        validated_moves: list[tuple[Drone, Hub, Connection]] = candidate_moves.copy()

        while True:
            # compter les nouveaux transits accaptes vers les zones restricted
            new_transits: dict[Hub, int] = {}

            for drone, next_hub, connection in validated_moves:
                former_hub: Hub = drone.current_hub

                if next_hub.zone == "restricted":   
                # les drones vers une zone restricted arriveront au tour suivant 
                    new_transits[next_hub] = new_transits.get(next_hub, 0) + 1

            # cherche un hub dont la capacite finale serait depassee
            overloaded_hub: Hub | None = None

            for hub in my_file_content.hubs_list:
                if hub is my_file_content.start_hub or hub is my_file_content.end_hub:
                    continue

                final_occupation: int = get_final_occupation(hub, validated_moves, arrivals_by_hub)

                # verifier que l'occupation de ce tour respecte la capacite
                if final_occupation > hub.max_drones:
                    overloaded_hub = hub
                    break

                # pour une zone restricted, verifier aussi les places necessaires aux drones qui arriveront au tour suivant
                if hub.zone == "restricted":
                    # nombre de drones qui commenceront un transit ce tour
                    future_arrivals: int = new_transits.get(hub, 0)
                    # nombre de drones qui pourront quitter ce hub au tour suivant
                    possible_departures: int = 0

                    # drones presents qui resteront dans le hub a la fin du tour
                    drones_to_check: list[Drone] = []
                    for drone in hub.present_drones_list:
                        # verifier si ce drone a deja un depart valide pour ce tour
                        is_leaving_this_turn: bool = False

                        for moving_drone, next_hub, connection in validated_moves:
                            if moving_drone is drone:
                                is_leaving_this_turn = True
                                break

                        # ne compter que les drones qui seront encore presents
                        if not is_leaving_this_turn:
                            drones_to_check.append(drone)

                    # ajouter les drones qui arrivent dans ce hub pendant ce tour
                    for drone, destination, connection in arrivals_this_turn:
                        if destination is hub:
                            drones_to_check.append(drone)

                    # compter les drones qui possedent une sortie
                    possible_departures = get_possible_departures(hub, drones_to_check, validated_moves, arrivals_by_hub, my_file_content)

                    # occupation prevue au tour suivant
                    future_occupation: int = final_occupation + future_arrivals - possible_departures
                    if future_occupation > hub.max_drones:
                        overloaded_hub = hub
                        break

            # tous les hubs respectent leur capacite : validation terminee
            if overloaded_hub is None:
                break

            # retirer un mouvement entrant dans le hub surcharge
            movement_to_cancel: tuple[Drone, Hub, Connection] | None = None
            for movement in reversed(validated_moves):
                drone, next_hub, connection = movement
                if next_hub is overloaded_hub:
                    movement_to_cancel = movement
                    break

            # aucun mouvement supprimable : la situation doit etre examinee
            if movement_to_cancel is None:
                raise RuntimeError(f"Impossible de respecter la capacite de {overloaded_hub.name}")

            validated_moves.remove(movement_to_cancel)

                        # EXECUTER LES DEPLACEMENTS VALIDES -------------------------------------------

        # tous les mouvements ont ete evalues, on applique les deplacements qui ont ete acceptes
        for drone, next_hub, connection in validated_moves:
            # on memorise le hub que le drone va quitter
            former_hub: Hub = drone.current_hub

            drone.path_index += 1
            former_hub.drones_occupation -= 1
            former_hub.present_drones_list.remove(drone)

            if next_hub.zone == "restricted":
                drone.is_in_transition = True
                drone.destination = next_hub
                drone.current_connection = connection
                drone.remaining_turns = 1

                connection.drones_occupation += 1
                connection.present_drones_list.append(drone)

                print(f"Drone {drone.id} commence son transit vers {next_hub.name}")

            else:
                drone.current_hub = next_hub

                next_hub.drones_occupation += 1
                next_hub.present_drones_list.append(drone)

                print("")
                print(f"Drone {drone.id} va vers {next_hub.name}")

                        # TRAITER LES ARRIVEES DES DRONES EN TRANSIT --------------------------------------------

        # on applique les arrivees enregistrees au debut du tour
        for drone, destination, connection in arrivals_this_turn:
            connection.drones_occupation -= 1
            connection.present_drones_list.remove(drone)

            drone.current_hub = destination
            destination.drones_occupation += 1
            destination.present_drones_list.append(drone)

            drone.is_in_transition = False
            drone.destination = None
            drone.current_connection = None

            print(f"Drone {drone.id} est arrive a {drone.current_hub.name}")

        # on verifie que l'occupation de chaque hub respecte sa capacite
        for hub in my_file_content.hubs_list:
            if hub is my_file_content.start_hub or hub is my_file_content.end_hub:
                continue

            assert hub.drones_occupation <= hub.max_drones, (f"Capacite depassee dans {hub.name} : {hub.drones_occupation}/{hub.max_drones}")

        # verifier que chaque connection respecte sa capacite
        for hub in my_file_content.hubs_list:
            for connection in hub.connections_list:
                assert connection.drones_occupation <= connection.capacity, (f"Capacite depassee sur la connection {hub.name} -> {connection.destination.name} : {connection.drones_occupation}/{connection.capacity}")

        # verifier la coherence des compteurs des hubs
        for hub in my_file_content.hubs_list:
            assert hub.drones_occupation == len(hub.present_drones_list), (f"Incoherence dans le hub {hub.name}")

            # verifier aussi les compteurs des connections
            for connection in hub.connections_list:
                assert connection.drones_occupation == len(connection.present_drones_list), (f"Incoherence sur la connection {hub.name} -> {connection.destination.name}")

        print("\nOccupation des hubs :")
        for hub in my_file_content.hubs_list:
            print(f"{hub.name}: {hub.drones_occupation}/{hub.max_drones}")

        i += 1

    sys.exit()
