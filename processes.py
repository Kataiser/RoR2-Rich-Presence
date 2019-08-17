import copy
import os
import subprocess
import time
from typing import Dict, Union

import psutil


class ProcessScanner:
    def __init__(self):
        self.has_cached_all_pids = False
        self.parsed_tasklist = {}
        self.process_data = {'ROR2': {'running': False, 'pid': None, 'path': None, 'time': None},
                             'Discord': {'running': False, 'pid': None}}
        self.p_data_default = copy.deepcopy(self.process_data)

    # basically psutil.process_iter(attrs=['pid', 'cmdline', 'create_time']) but WAY faster (and also highly specialized)
    def scan(self) -> Dict[str, Dict[str, Union[bool, str, int, None]]]:
        if not self.has_cached_all_pids:  # guaranteed on the first run
            print('a')
            self.parse_tasklist()

            if len(self.parsed_tasklist) == 2:
                self.has_cached_all_pids = True

            if 'Risk of Rain 2.exe' in self.parsed_tasklist:
                self.process_data['ROR2']['pid'] = self.parsed_tasklist['Risk of Rain 2.exe']
            if 'Discord' in self.parsed_tasklist:
                self.process_data['Discord']['pid'] = self.parsed_tasklist['Discord']

            self.get_all_extended_info()
        else:
            print('b')
            # all the PIDs are known, so don't use tasklist, saves 0.2 - 0.3 seconds :)
            self.get_all_extended_info()

            p_data_old = copy.deepcopy(self.process_data)

            if not self.process_data['ROR2']['running']:
                self.process_data['ROR2'] = self.p_data_default['ROR2']
            if not self.process_data['Discord']['running']:
                self.process_data['Discord'] = self.p_data_default['Discord']

            if self.process_data != p_data_old:
                self.has_cached_all_pids = False

        return self.process_data

    # get only the needed info (exe path and process start time) for each, and then apply it to self.p_data
    def get_all_extended_info(self):
        ror2_data = self.get_info_from_pid(self.process_data['ROR2']['pid'], ('time',))
        discord_data = self.get_info_from_pid(self.process_data['Discord']['pid'], ())

        # ugly
        self.process_data['ROR2']['running'], self.process_data['ROR2']['time'] = ror2_data['running'], ror2_data['time']
        self.process_data['Discord']['running'] = discord_data['running']

    # a mess of logic that gives process info from a PID
    def get_info_from_pid(self, pid: int, return_data: tuple = ('path', 'time')) -> dict:
        p_info = {'running': False, 'path': None, 'time': None}

        if pid is None:
            return p_info

        try:
            try:
                process = psutil.Process(pid=pid)
            except psutil.NoSuchProcess:
                pass
            else:
                p_info['running'] = [name for name in ('Risk of Rain 2.exe', 'Discord') if name in process.name()] != []

                if 'path' in return_data:
                    p_info['path'] = os.path.dirname(process.cmdline()[0])
                if 'time' in return_data:
                    p_info['time'] = int(process.create_time())
        except Exception:
            pass

        return p_info

    # https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/tasklist
    def parse_tasklist(self):
        processes = str(subprocess.check_output('tasklist /fi "STATUS eq running"')).split(r'\r\n')
        self.parsed_tasklist = {}

        for process_line in processes:
            process = process_line.replace('Risk of Rain 2.exe', 'Risk_of_Rain_2.exe').split()

            if 'Risk_of_Rain_2.exe' in process[0]:
                self.parsed_tasklist['Risk of Rain 2.exe'] = int(process[1])
            if 'Discord' in process[0]:
                self.parsed_tasklist['Discord'] = int(process[1])

        parsed_tasklist_keys = self.parsed_tasklist.keys()
        self.process_data['ROR2']['running'] = 'Risk of Rain 2.exe' in parsed_tasklist_keys
        self.process_data['Discord']['running'] = 'Discord' in parsed_tasklist_keys


if __name__ == '__main__':
    import pprint

    test_process_scanner = ProcessScanner()

    while True:
        scan_results = test_process_scanner.scan()
        pprint.pprint(scan_results)
        time.sleep(2)
        print()
