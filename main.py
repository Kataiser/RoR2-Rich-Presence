import copy
import os
import sys
import time

sys.path.append(os.path.abspath(os.path.join('python', 'packages')))
sys.path.append(os.path.abspath(os.path.join('python')))
from discoIPC import ipc

import processes


def main():
    output_log_txt_path = "{}\\AppData\\LocalLow\\Hopoo Games, LLC\\Risk of Rain 2\\output_log.txt".format(os.getenv('UserProfile'))

    start_time = int(time.time())
    activity = {'details': 'Loading game',  # this is what gets modified and sent to Discord via discoIPC
                'timestamps': {'start': start_time},
                'assets': {'small_image': ' ', 'small_text': 'Risk of Rain 2', 'large_image': 'logo', 'large_text': 'Risk of Rain 2'},
                'state': 'Not in lobby'}
    client_connected = False
    has_mention_not_running = False
    process_scanner = processes.ProcessScanner()

    while True:
        next_delay = 5
        p_data = process_scanner.scan()
        activity['timestamps']['start'] = p_data['ROR2']['time']

        if p_data['ROR2']['running'] and p_data['Discord']['running']:
            if not client_connected:
                # connects to Discord
                client = ipc.DiscordIPC('566395208858861569')
                client.connect()
                client_connected = True

            with open(output_log_txt_path, 'r', errors='replace') as output_log_txt:
                output_log = output_log_txt.readlines()

            old_details_state = copy.copy((activity['details'], activity['state']))

            for line in output_log:
                if 'Loaded scene' in line:
                    activity = switch_image_mode(activity)

                    if 'title' in line:
                        activity['details'] = "Main menu"
                        activity['state'] = "Not in lobby"
                    elif 'lobby loadSceneMode=Single' in line:
                        activity['details'] = "In lobby"
                        activity['state'] = "Singleplayer"
                    elif 'crystalworld' in line:
                        activity['state'] = "Prismatic Trials"

                    elif 'golemplains' in line:
                        activity = switch_image_mode(activity, ('golemplains', 'Titanic Plains'))
                    elif 'blackbeach' in line:
                        activity = switch_image_mode(activity, ('blackbeach', 'Distant Roost'))
                    elif 'goolake' in line:
                        activity = switch_image_mode(activity, ('goolake', 'Abandoned Aquaduct'))
                    elif 'frozenwall' in line:
                        activity = switch_image_mode(activity, ('frozenwall', 'Rallypoint Delta'))
                    elif 'dampcavesimple' in line:
                        activity = switch_image_mode(activity, ('dampcavesimple', 'Abyssal Depths'))
                    elif 'mysteryspace' in line:
                        activity = switch_image_mode(activity, ('mysteryspace', 'Hidden Realm: A Moment, Fractured'))
                    elif 'bazaar' in line:
                        activity = switch_image_mode(activity, ('bazaar', 'Hidden Realm: Bazaar Between Time'))
                    elif 'foggyswamp' in line:
                        activity = switch_image_mode(activity, ('foggyswamp', 'Wetland Aspect'))
                    elif 'wispgraveyard' in line:
                        activity = switch_image_mode(activity, ('wispgraveyard', 'Scorched Acres'))
                    elif 'goldshores' in line:
                        activity = switch_image_mode(activity, ('goldshores', 'Gilded Coast'))

                elif 'lobby creation succeeded' in line:
                    activity['details'] = "In lobby"
                    activity['state'] = "Multiplayer"
                    activity = switch_image_mode(activity)
                elif 'Left lobby' in line:
                    activity['details'] = "Main menu"
                    activity['state'] = "Not in lobby"
                    activity = switch_image_mode(activity)

            if time.time() - start_time < 10:
                activity['details'] = "Loading game"

            if old_details_state != (activity['details'], activity['state']):
                next_delay = 2

            print(activity['details'])
            print(activity['state'])
            time_elapsed = time.time() - start_time
            print("{:02}:{:02} elapsed\n".format(int(time_elapsed / 60), round(time_elapsed % 60)))

            if not os.path.exists('history.txt'):
                open('history.txt', 'w').close()

            activity_str = f'{activity}\n'
            with open('history.txt', 'r') as history_file_r:
                history = history_file_r.readlines()
            if activity_str not in history:
                with open('history.txt', 'a') as history_file_a:
                    history_file_a.write(activity_str)

            # send everything to discord
            client.update_activity(activity)
        elif not p_data['Discord']['running']:
            print("{}\nDiscord isn't running\n")
        else:
            if client_connected:
                try:
                    client.disconnect()  # doesn't work...
                except:
                    pass

                raise SystemExit  # ...but this does
            else:
                if not has_mention_not_running:
                    print("Risk of Rain 2 isn't running\n")
                    has_mention_not_running = True

            # to prevent connecting when already connected
            client_connected = False

        time.sleep(next_delay)


def switch_image_mode(temp_activity, stage=()):
    if stage == ():
        temp_activity['assets']['small_image'] = ' '
        temp_activity['assets']['large_image'] = 'logo'
        temp_activity['assets']['large_text'] = 'Risk of Rain 2'
    else:
        temp_activity['assets']['small_image'] = 'icon'
        temp_activity['assets']['large_image'] = stage[0]
        temp_activity['assets']['large_text'] = stage[1]
        temp_activity['details'] = stage[1]
        
        if temp_activity['state'] == "Not in lobby":
            temp_activity['state'] = "Spectating"

    return temp_activity


if __name__ == '__main__':
    main()
