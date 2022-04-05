#!/bin/env python3

import psutil
import os
import json
import logging
import shutil

GET_DRIVES_COMMAND = "lsblk --raw -oPATH,FSSIZE,FSTYPE,MOUNTPOINT,UUID"
#GET_DRIVES_COMMAND = "lsblk --raw -o NAME,PATH,FSSIZE,FSTYPE,MOUNTPOINT,UUID"


class DiskUtils:

    def __init__(self, config_file: str):
        self.config_file = config_file

    @staticmethod
    def get_all_drives(self):
        _drives = []
        os.system(GET_DRIVES_COMMAND)

        shutil.disk_usage()


    @staticmethod
    def get_free_space(mount_point: str) -> int:
        """Gets the free space by mount point in bytes
        :rtype: int
        """
        return psutil.disk_usage(mount_point).free



def main():
    print("Main")
    diskutils = DiskUtils('../config.json')
    for disk in diskutils.config['available_drives']:
        diskutils.get_free_space(disk)
    # disks = psutil.disk_partitions()
    # for disk in disks:
    #     print(disk)


if __name__ == "__main__":
    main()