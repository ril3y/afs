import time

REMOTE_SERVER = '172.16.10.7'
PRIVATE_KEY = '/home/ril3y/.ssh/id_rsa'
USERNAME = 'ril3y'
from random import randint
from transfer_job import TransferJob
import paramiko
import sys
import socket
import os
import datetime

class ConnectionManager:
    CMD_DRIVE_ENUMERATION = 'lsblk  -b -o NAME,UUID,FSTYPE,FSAVAIL,SIZE,SERIAL,MOUNTPOINT --json'
    CMD_GET_DRIVE_FREESPACE = 'df -B1'
    CMD_OPEN_CONNECTION = 'nc -lnvp %d > %s '

    def __init__(self, server, private_key, username):
        self.client_connection = paramiko.SSHClient()
        self.client_connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.username = username
        self.private_key = private_key
        self.server = server
        self.is_connected = False
        self._connect()

    async def process_job(self, job):
        print("PROCESSING JOB")
        await self.open_file_connection(job)
        # await asyncio.sleep(1)
        print("JOB DONE")
        return

    def open_file_connection(self, job: TransferJob):
        port = randint(65000, 65535)  # Create random port to listen on
        # TODO: create a command to make sure the port is available
        print(
            f"Opening Connection @ {REMOTE_SERVER}:{port} sending file {job.get_filename()} to {job.build_remote_filename()}")
        stdin, stdout, stderr = self.client_connection.exec_command(
            self.CMD_OPEN_CONNECTION %
            (port, job.build_remote_filename()))

        # THIS BLOCKS If we get an error lets print it to the console
        # err = stdout.readlines()
        # for line in err:
        #     print(line)
        #     sys.exit()

        # Let the remote machine open a port to listen on
        print("[!] Please wait for the remote connection to open")
        time.sleep(5)

        # TODO: Create retry count here
        s = socket.socket()
        s.connect((REMOTE_SERVER, port))

        # progress = tqdm.tqdm(range(job.get_file_size()), f"Sending {job.get_filename()}", unit="B",
        # unit_scale=True, unit_divisor=1024)

        with s, open(job.get_filename(), 'rb') as f:
            start_time = time.time()
            print(f"[#] Sending File {job.get_filename() } to {job.build_remote_filename() } Please wait...")
            print(f"[#] File transfer took {datetime.timedelta((time.time() - start_time))} !")
            while True:
                bytes_read = f.read(4096)
                if not bytes_read:
                    print("[#] File has been sent.")
                    break
                s.sendall(bytes_read)
                # update the progress bar
                # progress.update(len(bytes_read))
            s.close()
            try:
                os.remove(job.get_filename())
                print(f"[!] Removed: {job.get_filename()} successfully\n")
            except IOError:
                print(f"[!] Error Removing: {job.get_filename()}")

    def get_drive_info(self):
        return self.client_connection.exec_command(self.CMD_DRIVE_ENUMERATION)

    def _connect(self):
        try:
            with open(PRIVATE_KEY, 'r') as _key:
                pk = paramiko.RSAKey.from_private_key(_key)
        except IOError:
            print("Cannot open key")
            sys.exit()
        self.client_connection.connect(REMOTE_SERVER, username=self.username, pkey=pk)
        self.is_connected = True

    def execute_command(self, command):
        i, d, e = self.client_connection.exec_command(command)
