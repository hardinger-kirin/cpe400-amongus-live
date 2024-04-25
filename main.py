# in part referenced: https://github.com/lesander/amongus-impostor-detector/blob/main/detector.py

import pyshark
import argparse


def sniff(interface):
    capture = pyshark.LiveCapture(interface=interface, display_filter="amongus.packet_format eq \"Reliable\"")
    capture.sniff(timeout=1)
    return capture


if __name__ == "__main__":
    # https://stackoverflow.com/questions/4033723/how-do-i-access-command-line-arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("interface", help="The interface upon which to sniff packets.", type=str)
    args = parser.parse_args()

    players_name = {}
    players_color = {}
    players_id = {}
    players_tasks = {}

    current_map = -1

    got_task_list = False
    got_map = False
    printed_tasks = False

    while True:
        capture = sniff(args.interface)
        for packet in capture:
            if hasattr(packet.amongus, 'game_data'):
                data = packet.amongus._get_all_fields_with_alternates()
                field_count = 0
                for field in data:
                    def get_names_and_colors():
                        # keep track of players in game
                        if 'Name:' in str(field) and 'Scene Name' not in str(field):
                            if field.showname_value not in players_name:
                                # empty values and non-integer IDs
                                if not data[field_count - 3].showname_value.isnumeric() or not field.showname_value:
                                    return
                                players_name[data[field_count - 3].showname_value] = field.showname_value

                        if 'SetColor' in str(field) and field_count != len(data) - 1:
                            players_color[data[field_count - 1].showname_value] = data[field_count + 1].showname_value

                    def get_ids():
                        if 'Spawn Id' in str(field) and 'Player' in str(field.showname_value) and 'SetStartCounter' not in str(data):
                            players_id[data[field_count + 8].showname_value] = data[field_count + 5].showname_value

                    def get_kills():
                        # provide murder data
                        if 'MurderPlayer' in str(field):
                            murderer_id = data[field_count - 1].showname_value
                            victim_id = data[field_count + 1].showname_value

                            print('\x1b[5;30;43m', end='')

                            # prioritize displaying name over color
                            if murderer_id in players_name:
                                if victim_id in players_name:
                                    print(f'{players_name[murderer_id]} murdered {players_name[victim_id]}', end='')
                                elif victim_id in players_color:
                                    print(f'{players_name[murderer_id]} murdered {players_color[victim_id]}', end='')
                                else:
                                    print(f'{players_name[murderer_id]} murdered an unknown player of ID {victim_id}', end='')
                            elif murderer_id in players_color:
                                if victim_id in players_name:
                                    print(f'{players_color[murderer_id]} murdered {players_name[victim_id]}', end='')
                                elif victim_id in players_color:
                                    print(f'{players_color[murderer_id]} murdered {players_color[victim_id]}', end='')
                                else:
                                    print(f'{players_color[murderer_id]} murdered an unknown player of ID {victim_id}', end='')
                            else:
                                if victim_id in players_name:
                                    print(f'An unknown impostor of ID {murderer_id} murdered {players_name[victim_id]}', end='')
                                elif victim_id in players_color:
                                    print(f'An unknown impostor of ID {murderer_id} murdered {players_color[victim_id]}', end='')
                                else:
                                    print(f'An unknown impostor of ID {murderer_id} murdered an unknown player of ID {victim_id}', end='')

                            print('\x1b[0m')

                    def get_task_list():
                        if 'SetTasks' in str(field):
                            global got_task_list
                            len_task_list = len(data) - field_count
                            for i in range(field_count + 1, len_task_list, 3):
                                if 'Part Length' in str(data[i].showname_key):
                                    continue
                                player_id = data[i].showname_value
                                player_num_tasks = data[i + 1].showname_value
                                player_tasks = data[i + 2].showname_value

                                # prioritize displaying name over color
                                if player_id in players_id:
                                    players_tasks[players_name[players_id[player_id]]] = data[i + 2].showname_value
                                elif player_id in players_color:
                                    players_tasks[players_color[player_id]] = data[i + 2].showname_value
                                else:
                                    players_tasks[str("Unknown, ID: " + player_id)] = data[i + 2].showname_value

                            got_task_list = True

                    def get_map():
                        if 'Spawn Id' in str(field) and 'ShipStatus' in str(field.showname_value):
                            global got_map
                            global current_map
                            current_map = int(str(field.showname_value).replace(" (ShipStatus)", ''))
                            got_map = True

                    def print_tasks():
                        global printed_tasks
                        global current_map
                        # https://stackoverflow.com/questions/13673060/split-string-into-strings-by-length
                        for key in players_tasks:
                            tasks = players_tasks[key]
                            chunks, chunk_size = len(tasks), 2
                            tasks = [tasks[i:i+chunk_size] for i in range(0, chunks, chunk_size)]
                            print(f'Player {key} has tasks:',)
                            if current_map == 0:
                                for task in tasks:
                                    print('\t', end='')
                                    # https://stackoverflow.com/questions/209513/convert-hex-string-to-integer-in-python
                                    task = int(str(task), 16)
                                    if task == 0:
                                        print(f'Admin: Swipe Card')
                                    elif task == 1:
                                        print(f'Electrical: Fix Wiring')
                                    elif task == 2:
                                        print(f'Weapons: Clear Asteroids')
                                    elif task == 3:
                                        print(f'Engines: Align Engine Output')
                                    elif task == 4:
                                        print(f'Medbay: Submit Scan')
                                    elif task == 5:
                                        print(f'Medbay: Inspect Sample')
                                    elif task == 6:
                                        print(f'Storage: Fuel Engines')
                                    elif task == 7:
                                        print(f'Reactor: Start Reactor')
                                    elif task == 8:
                                        print(f'O2: Empty Chute')
                                    elif task == 9:
                                        print(f'Cafeteria: Empty Garbage')
                                    elif task == 10:
                                        print(f'Communications: Download Data')
                                    elif task == 11:
                                        print(f'Electrical: Calibrate Distributor')
                                    elif task == 12:
                                        print(f'Navigation: Chart Course')
                                    elif task == 13:
                                        print(f'O2: Clean O2 Filter')
                                    elif task == 14:
                                        print(f'Reactor: Unlock Manifolds')
                                    elif task == 15:
                                        print(f'Electrical: Download Data')
                                    elif task == 16:
                                        print(f'Navigation: Stabilize Steering')
                                    elif task == 17:
                                        print(f'Weapons: Download Data')
                                    elif task == 18:
                                        print(f'Shields: Prime Shields')
                                    elif task == 19:
                                        print(f'Cafeteria: Download Data')
                                    elif task == 20:
                                        print(f'Navigation: Download Data')
                                    elif task == 21:
                                        print(f'Electrical: Divert Power to Shields')
                                    elif task == 22:
                                        print(f'Electrical: Divert Power to Weapons')
                                    elif task == 23:
                                        print(f'Electrical: Divert Power to Communications')
                                    elif task == 24:
                                        print(f'Electrical: Divert Power to Upper Engine')
                                    elif task == 25:
                                        print(f'Electrical: Divert Power to O2')
                                    elif task == 26:
                                        print(f'Electrical: Divert Power to Navigation')
                                    elif task == 27:
                                        print(f'Electrical: Divert Power to Lower Engine')
                                    elif task == 28:
                                        print(f'Electrical: Divert Power to Security')
                                    else:
                                        print(f'[[Unknown Task]]')
                            elif current_map == 1:
                                for task in tasks:
                                    print('\t', end='')
                                    # https://stackoverflow.com/questions/209513/convert-hex-string-to-integer-in-python
                                    task = int(str(task), 16)
                                    if task == 0:
                                        print(f'Hallway: Fix Wiring')
                                    elif task == 1:
                                        print(f'Admin: Enter ID Code')
                                    elif task == 2:
                                        print(f'Medbay: Submit Scan')
                                    elif task == 3:
                                        print(f'Balcony: Clear Asteroids')
                                    elif task == 4:
                                        print(f'Electrical: Divert Power to Admin')
                                    elif task == 5:
                                        print(f'Electrical: Divert Power to Cafeteria')
                                    elif task == 6:
                                        print(f'Electrical: Divert Power to Communications')
                                    elif task == 7:
                                        print(f'Electrical: Divert Power to Launchpad')
                                    elif task == 8:
                                        print(f'Electrical: Divert Power to Medbay')
                                    elif task == 9:
                                        print(f'Electrical: Divert Power to Office')
                                    elif task == 10:
                                        print(f'Storage: Water Plants')
                                    elif task == 11:
                                        print(f'Reactor: Start Reactor')
                                    elif task == 12:
                                        print(f'Electrical: Divert Power to Greenhouse')
                                    elif task == 13:
                                        print(f'Admin: Chart Course')
                                    elif task == 14:
                                        print(f'Greenhouse: Clean O2 Filter')
                                    elif task == 15:
                                        print(f'Launchpad: Fuel Engines')
                                    elif task == 16:
                                        print(f'Laboratory: Assemble Artifact')
                                    elif task == 17:
                                        print(f'Laboratory: Sort Samples')
                                    elif task == 18:
                                        print(f'Admin: Prime Shields')
                                    elif task == 19:
                                        print(f'Cafeteria: Empty Garbage')
                                    elif task == 20:
                                        print(f'Balcony: Measure Weather')
                                    elif task == 21:
                                        print(f'Electrical: Divert Power to Laboratory')
                                    elif task == 22:
                                        print(f'Cafeteria: Buy Beverage')
                                    elif task == 23:
                                        print(f'Office: Process Data')
                                    elif task == 24:
                                        print(f'Launchpad: Run Diagnostics')
                                    elif task == 25:
                                        print(f'Reactor: Unlock Manifolds')
                                    else:
                                        print(f'[[Unknown Task]]')
                            elif current_map == 2:
                                for task in tasks:
                                    print('\t', end='')
                                    # https://stackoverflow.com/questions/209513/convert-hex-string-to-integer-in-python
                                    task = int(str(task), 16)
                                    if task == 0:
                                        print(f'Office: Swipe Card')
                                    elif task == 1:
                                        print(f'Dropship: Insert Keys')
                                    elif task == 2:
                                        print(f'Office: Scan Boarding Pass')
                                    elif task == 3:
                                        print(f'Electrical: Fix Wiring')
                                    elif task == 4:
                                        print(f'Weapons: Download Data')
                                    elif task == 5:
                                        print(f'Office: Download Data')
                                    elif task == 6:
                                        print(f'Electrical: Download Data')
                                    elif task == 7:
                                        print(f'Specimen Room: Download Data')
                                    elif task == 8:
                                        print(f'Storage: Download Data')
                                    elif task == 9:
                                        print(f'Specimen Room: Start Reactor')
                                    elif task == 10:
                                        print(f'Storage: Fuel Engines')
                                    elif task == 11:
                                        print(f'Boiler Room: Open Waterways')
                                    elif task == 12:
                                        print(f'Medbay: Inspect Sample')
                                    elif task == 13:
                                        print(f'Boiler Room: Replace Water Jug')
                                    elif task == 14:
                                        print(f'Outside: Fix Weather Node Node_GI')
                                    elif task == 15:
                                        print(f'Outside: Fix Weather Node Node_IRO')
                                    elif task == 16:
                                        print(f'Outside: Fix Weather Node Node_PD')
                                    elif task == 17:
                                        print(f'Outside: Fix Weather Node Node_TB')
                                    elif task == 18:
                                        print(f'Communications: Reboot WiFi')
                                    elif task == 19:
                                        print(f'O2: Monitor Tree')
                                    elif task == 20:
                                        print(f'Specimen Room: Unlock Manifolds')
                                    elif task == 21:
                                        print(f'Specimen Room: Store Artifacts')
                                    elif task == 22:
                                        print(f'O2: Fill Canisters')
                                    elif task == 23:
                                        print(f'O2: Empty Garbage')
                                    elif task == 24:
                                        print(f'Dropship: Chart Course')
                                    elif task == 25:
                                        print(f'Medbay: Submit Scan')
                                    elif task == 26:
                                        print(f'Weapons: Clear Asteroids')
                                    elif task == 27:
                                        print(f'Outside: Fix Weather Node Node_CA')
                                    elif task == 28:
                                        print(f'Outside: Fix Weather Node Node_MLG')
                                    elif task == 29:
                                        print(f'Laboratory: Align Telescope')
                                    elif task == 30:
                                        print(f'Laboratory: Repair Drill')
                                    elif task == 31:
                                        print(f'Laboratory: Record Temperature')
                                    elif task == 32:
                                        print(f'Outside: Record Temperature')
                                    else:
                                        print(f'[[Unknown Task]]')
                            elif current_map == 3:
                                for task in tasks:
                                    print('\t', end='')
                                    # https://stackoverflow.com/questions/209513/convert-hex-string-to-integer-in-python
                                    task = int(str(task), 16)
                                    if task == 0:
                                        print(f'Electrical: Fix Wiring')
                                    elif task == 1:
                                        print(f'Meeting Room: Enter ID Code')
                                    elif task == 2:
                                        print(f'Electrical: Reset Breakers')
                                    elif task == 3:
                                        print(f'Vault Room: Download Data')
                                    elif task == 4:
                                        print(f'Brig: Download Data')
                                    elif task == 5:
                                        print(f'Cargo Bay: Download Data')
                                    elif task == 6:
                                        print(f'Gap Room: Download Data')
                                    elif task == 7:
                                        print(f'Records: Download Data')
                                    elif task == 8:
                                        print(f'Cargo Bay: Unlcok Safe')
                                    elif task == 9:
                                        print(f'Ventilation: Start Fans')
                                    elif task == 10:
                                        print(f'Main Hall: Empty Garbage')
                                    elif task == 11:
                                        print(f'Medical: Empty Garbage')
                                    elif task == 12:
                                        print(f'Kitchen: Empty Garbage')
                                    elif task == 13:
                                        print(f'Main Hall: Develop Photos')
                                    elif task == 14:
                                        print(f'Cargo Bay: Fuel Engines')
                                    elif task == 15:
                                        print(f'Security: Rewind Tapes')
                                    elif task == 16:
                                        print(f'Vault Room: Polish Ruby')
                                    elif task == 17:
                                        print(f'Electrical: Calibrate Distributor')
                                    elif task == 18:
                                        print(f'Cockpit: Stabilize Steering')
                                    elif task == 19:
                                        print(f'Armory: Download Data')
                                    elif task == 20:
                                        print(f'Cockpit: Download Data')
                                    elif task == 21:
                                        print(f'Comms: Download Data')
                                    elif task == 22:
                                        print(f'Medical: Download Data')
                                    elif task == 23:
                                        print(f'Viewing Deck: Download Data')
                                    elif task == 24:
                                        print(f'Electrical: Divert Power to Armory')
                                    elif task == 25:
                                        print(f'Electrical: Divert Power to Cockpit')
                                    elif task == 26:
                                        print(f'Electrical: Divert Power to Gap Room')
                                    elif task == 27:
                                        print(f'Electrical: Divert Power to Main Hall')
                                    elif task == 28:
                                        print(f'Electrical: Divert Power to Meeting Room')
                                    elif task == 29:
                                        print(f'Electrical: Divert Power to Showers')
                                    elif task == 30:
                                        print(f'Electrical: Divert Power to Engine')
                                    elif task == 31:
                                        print(f'Showers: Pick Up Towels')
                                    elif task == 32:
                                        print(f'Lounge: Clean Toilet')
                                    elif task == 33:
                                        print(f'Vault Room: Dress Mannequin')
                                    elif task == 34:
                                        print(f'Records: Sort Records')
                                    elif task == 35:
                                        print(f'Armory: Put Away Pistols')
                                    elif task == 36:
                                        print(f'Armory: Put Away Rifles')
                                    elif task == 37:
                                        print(f'Main Hall: Decontaminate')
                                    elif task == 38:
                                        print(f'Kitchen: Make Burger')
                                    elif task == 39:
                                        print(f'Showers: Fix Shower')
                                    else:
                                        print(f'[[Unknown Task]]')
                            print('')
                        printed_tasks = True

                    get_names_and_colors()
                    get_ids()
                    if not got_task_list:
                        get_task_list()
                    if not got_map:
                        get_map()
                    if got_task_list and got_map and not printed_tasks:
                        print_tasks()
                    get_kills()

                    field_count += 1
            elif int(packet.amongus.payload_type) == 1:
                data = packet.amongus._get_all_fields_with_alternates()
                field_count = 0
                for field in data:
                    if 'Game Code:' in str(field):
                        print(f'Joined game. Code: {data[field_count + 4].showname_value}')
                        # reset flags
                        players_name = {}
                        players_color = {}
                        players_id = {}
                        players_tasks = {}

                        current_map = -1

                        got_task_list = False
                        got_map = False
                        printed_tasks = False
