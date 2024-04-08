# in part referenced: https://github.com/lesander/amongus-impostor-detector/blob/main/detector.py

import pyshark

def sniff():
    capture = pyshark.LiveCapture(interface='Ethernet', display_filter="amongus.packet_format eq \"Reliable\"")
    capture.sniff(timeout=1)
    return capture

if __name__ == "__main__":
    players_name = {}
    players_color = {}

    while(1):
        capture = sniff()
        for packet in capture:
            if hasattr(packet.amongus, 'game_data'):
                data = packet.amongus._get_all_fields_with_alternates()
                field_count = 0
                for field in data:
                    # keep track of players in game
                    if 'Name:' in str(field) and 'Scene Name' not in str(field):
                        if field.showname_value not in players_name:
                            players_name[data[field_count - 3].showname_value] = field.showname_value

                    if 'SetColor' in str(field) and field_count != len(data) - 1:
                        players_color[data[field_count - 1].showname_value] = data[field_count + 1]

                    # reveal imposter, if possible
                    if 'Impostor: 2' in str(field):
                        # The PlayerName string is 5 fields back in an UpdateGameData player array.
                        impostor = data[field_count - 4].showname_value
                        print(f"Found an impostor. Color: {impostor}")

                    # provide murder data
                    if 'MurderPlayer' in str(field):
                        murderer_id = data[field_count - 1].showname_value
                        victim_id = data[field_count + 1].showname_value

                        # prioritize displaying name over color
                        if murderer_id in players_name:
                            if victim_id in players_name:
                                print(f'{players_name[murderer_id]} murdered {players_name[victim_id]}')
                            elif victim_id in players_color:
                                print(f'{players_name[murderer_id]} murdered {players_color[victim_id]}')
                            else:
                                print(f'{players_name[murderer_id]} murdered an unknown player of ID {victim_id}')
                        elif murderer_id in players_color:
                            if victim_id in players_name:
                                print(f'{players_color[murderer_id]} murdered {players_name[victim_id]}')
                            elif victim_id in players_color:
                                print(f'{players_color[murderer_id]} murdered {players_color[victim_id]}')
                            else:
                                print(f'{players_color[murderer_id]} murdered an unknown player of ID {victim_id}')
                        else:
                            if victim_id in players_name:
                                print(f'An unknown impostor of ID {murderer_id} murdered {players_name[victim_id]}')
                            elif victim_id in players_color:
                                print(f'An unknown impostor of ID {murderer_id} murdered {players_color[victim_id]}')
                            else:
                                print(f'An unknown impostor of ID {murderer_id} murdered an unknown player of ID {victim_id}')

                    field_count += 1