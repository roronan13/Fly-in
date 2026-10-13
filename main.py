import sys

from parsing.parsing import parsing_entry
from file_content import FileContent
from file_content import Drone, Hub, Connection
from pathfinder.dijkstra import dijkstra


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

        #                 # COMPTER LES DEPARTS DE CHAQUE HUB ---------------------------------------------

        # # ce dict associe chaque hub au nombre de drones qui envisagent de le quitter pendant ce tour
        # departures: dict[Hub, int] = {}

        # for drone, next_hub, connection in potential_movements:
        #     # le hub de depart du mouvement est le hub actuel du drone
        #     former_hub: Hub = drone.current_hub

        #     if former_hub not in departures:
        #         departures[former_hub] = 0

        #     departures[former_hub] += 1

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

        # on compte les drones deja en transit vers chaque hub restricted
        incoming_transits: dict[Hub, int] = {}
        for drone in my_file_content.drones_list:
            if drone.is_in_transition and drone.remaining_turns > 0:
                destination = drone.destination

                incoming_transits[destination] = incoming_transits.get(destination, 0) + 1

        while True:
            # compter uniquement les departs des mouvements encore retenus
            accepted_departures: dict[Hub, int] = {}
            accepted_arrivals: dict[Hub, int] = {}

            # compter les nouveaux transits accaptes vers les zones restricted
            new_transits: dict[Hub, int] = {}

            for drone, next_hub, connection in validated_moves:
                former_hub: Hub = drone.current_hub

                accepted_departures[former_hub] = accepted_departures.get(former_hub, 0) + 1

                # un drone entrant en zone restricted reste sur la connection ce tour
                if next_hub.zone != "restricted":
                    accepted_arrivals[next_hub] = accepted_arrivals.get(next_hub, 0) + 1

            # cherche un hub dont la capacite finale serait depassee
            overloaded_hub: Hub | None = None

            for hub in my_file_content.hubs_list:
                if hub is my_file_content.start_hub or hub is my_file_content.end_hub:
                    continue

                final_occupation: int = hub.drones_occupation + accepted_arrivals.get(hub, 0) + arrivals_by_hub.get(hub, 0) - accepted_departures.get(hub, 0)

                if final_occupation > hub.max_drones:
                    overloaded_hub = hub
                    break

            # tous les hubs respectent leur capacite : validation terminee
            if overloaded_hub is None:
                break

            # retirer un mouvement entrant dans le hub surcharge
            movement_to_cancel: tuple[Drone, Hub, Connection] | None = None
            for movement in reversed(validated_moves):
                drone, next_hub, connection = movement
                if next_hub is overloaded_hub and next_hub.zone != "restricted":
                    movement_to_cancel = movement
                    break

            # aucun mouvement supprimable : la situation doit etre examinee
            if movement_to_cancel is None:
                raise RuntimeError(f"Impossible de respecter la capacite de {overloaded_hub.name}")

            validated_moves.remove(movement_to_cancel)

        # # continent les mouvements acceptes
        # validated_moves: list[tuple[Drone, Hub, Connection]] = []

        # # nombre de places reservees dans chaque hub par les mouvements acceptes pendant ce tour
        # reserved_spots: dict[Hub, int] = {}

        # # nombre de passages reserves sur chaque connection par les mouvements acceptes pendant ce tour
        # reserved_connections: dict[Connection, int] = {}

        # # on verifie chaque mouvement qui est envisage
        # for drone, next_hub, connection in potential_movements:
        #     # on initialise le compteur de reservations du hub si cest la premiere fois qu'on le rencontre
        #     if next_hub not in reserved_spots:
        #         reserved_spots[next_hub] = 0
        #     # on initialise le compteur de reservations de la connection
        #     if connection not in reserved_connections:
        #         reserved_connections[connection] = 0

        #     # calcule les places necessaires aux arrivees de ce tour
        #     planned_arrivals: int = arrivals_by_hub.get(next_hub, 0)
        #     # on calcule l'occupation prevue du hub d'arrivee, sans compter les departs qui n'ont pas encore ete valides
        #     hub_enough_space: bool = next_hub.drones_occupation + reserved_spots[next_hub] + planned_arrivals < next_hub.max_drones
        #     # hub_enough_space: bool = next_hub.drones_occupation + reserved_spots[next_hub] + planned_arrivals - departures.get(next_hub, 0) < next_hub.max_drones
        #     # on calcule le nombre de drones deja reserves sur cette connection
        #     connection_frees: int = connections_being_freed.get(connection, 0)
        #     connection_enough_space: bool = connection.drones_occupation + reserved_connections[connection] - connection_frees < connection.capacity

        #     # on affiche la decision prise pour chaque mouvement envisage
        #     print(f"Drone {drone.id} : {drone.current_hub.name} -> {next_hub.name} | place_hub={hub_enough_space}, place_connection={connection_enough_space}")

        #     # le mouvement est accepte si les deux conditions de capacite sont respectees
        #     if hub_enough_space and connection_enough_space:
        #         # on ajoute le mouvement a la liste des deplacements valides
        #         validated_moves.append((drone, next_hub, connection))
        #         # on reserve une place dans le hub d'arrivee
        #         reserved_spots[next_hub] += 1
        #         # on reserve une place sur la connection
        #         reserved_connections[connection] += 1
        #         # next_hub.drones_occupation += 1

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

        print("\nOccupation des hubs :")
        for hub in my_file_content.hubs_list:
            print(f"{hub.name}: {hub.drones_occupation}/{hub.max_drones}")

        i += 1

    sys.exit()
