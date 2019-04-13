import copy
import os
import sys
import time

sys.path.append(os.path.abspath(os.path.join('python', 'packages')))
sys.path.append(os.path.abspath(os.path.join('python')))
import psutil
import psutil._exceptions as ps_exceptions
from discoIPC import ipc


def main():
    output_log_txt_path = "{}\\AppData\\LocalLow\\Hopoo Games, LLC\\Risk of Rain 2\\output_log.txt".format(os.getenv('UserProfile'))

    start_time = int(time.time())
    activity = {'details': 'Loading game',  # this is what gets modified and sent to Discord via discoIPC
                'timestamps': {'start': start_time},
                'assets': {'small_image': ' ', 'small_text': 'yeet', 'large_image': 'logo', 'large_text': 'Risk of Rain 2'},
                'state': 'Not in lobby'}
    client_connected = False
    has_mention_not_running = False

    while True:
        game_is_running = False
        discord_is_running = False
        next_delay = 5

        for process in psutil.process_iter():
            if game_is_running and discord_is_running:
                break
            else:
                try:
                    with process.oneshot():
                        p_name = process.name()

                        if p_name == 'Risk of Rain 2.exe':
                            start_time = int(process.create_time())
                            activity['timestamps']['start'] = start_time
                            game_is_running = True
                        elif 'Discord' in p_name:
                            discord_is_running = True
                except ps_exceptions.NoSuchProcess:
                    pass
                except ps_exceptions.AccessDenied:
                    pass

                time.sleep(0.001)

        if game_is_running and discord_is_running:
            if not client_connected:
                # connects to Discord
                client = ipc.DiscordIPC('566395208858861569')
                client.connect()
                client_connected = True

            with open(output_log_txt_path, 'r', errors='replace') as output_log_txt:
                output_log = output_log_txt.readlines()

            old_details_state = copy.copy((activity['details'], activity['state']))

            for line in output_log:
                if "Loaded scene" in line:
                    if "title" in line:
                        activity['details'] = "Main menu"
                        activity['state'] = "Not in lobby"
                    elif "lobby loadSceneMode=Single" in line:
                        activity['details'] = "In lobby"
                        activity['state'] = "Singleplayer"
                    elif "crystalworld" in line:
                        activity['state'] = "Prismatic Trials"

                    elif "golemplains" in line:
                        activity['details'] = "Titanic Plains"
                    elif "blackbeach" in line:
                        activity['details'] = "Distant Roost"
                    elif "goolake" in line:
                        activity['details'] = "Abandoned Aquaduct"
                    elif "frozenwall" in line:
                        activity['details'] = "Rallypoint Delta"
                    elif "dampcavesimple" in line:
                        activity['details'] = "Abyssal Depths"
                    elif "mysteryspace" in line:
                        activity['details'] = "Hidden Realm: A Moment, Fractured"
                    elif "bazaar" in line:
                        activity['details'] = "Hidden Realm: Bazaar Between Time"
                    elif "foggyswamp" in line:
                        activity['details'] = "Wetland Aspect"

                elif "lobby creation succeeded" in line:
                    activity['details'] = "In lobby"
                    activity['state'] = "Multiplayer"
                elif "Left lobby" in line:
                    activity['details'] = "Main menu"
                    activity['state'] = "Not in lobby"

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
        elif not discord_is_running:
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


if __name__ == '__main__':
    main()
