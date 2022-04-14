from random import randint
from transfer_job import TransferJob
import paramiko
import sys
import socket
import os
import tqdm
import time

# TODO: Make a command line / config file to contain these settings
REMOTE_SERVER = '172.16.10.7'
PRIVATE_KEY = '/home/ril3y/.ssh/id_rsa'
USERNAME = 'ril3y'


class ConnectionManager:
    CMD_DRIVE_ENUMERATION = 'lsblk -b -o NAME,UUID,FSTYPE,FSAVAIL,SIZE,SERIAL,MOUNTPOINT --json'
    CMD_GET_DRIVE_FREESPACE = 'df -B1'
    CMD_OPEN_CONNECTION = 'nc -lnvp %d > %s '

    def __init__(self, server, private_key, username):
        self.client_connection = paramiko.SSHClient()
        self.client_connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.username = username
        self.private_key = private_key
        self.server = server
        self._connect()

    def remote_server_checks(self):
        # TODO: Create this check to ensure netcat is (others?) available
        pass

    def send_file(self, job: TransferJob, port: int):
        MAX_RETRIES = 5
        s = socket.socket()
        for count in range(0, MAX_RETRIES):
            try:
                s.connect((REMOTE_SERVER, port))
                break
            except:
                print(f"Connecting.... #{count} of {MAX_RETRIES}")
                count = count + 1
                time.sleep(.5)

            if count == MAX_RETRIES:
                print("Error connecting to remote server")
                sys.exit()

        # TODO: Create a progress bar and normalize output to work from threads (bytes per second / percentage etc)
        # progress = tqdm.tqdm(range(job.get_file_size()), f"Sending {job.get_filename()}", unit="B", unit_scale=True,
        #                      unit_divisor=1024)

        with open(job.get_filename(), 'rb') as f:
            start_time = time.time()
            print(f"[#] Sending File {job.get_filename()} to {job.build_remote_filename()} Please wait...")
            while True:
                bytes_read = f.read(128096)
                if not bytes_read:
                    print("[#] File has been sent.")
                    print(f"[#] File transfer took {(time.time() - start_time) / 60} minutes!")

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

    def open_file_connection(self, job: TransferJob, port: int):
        # Let the remote machine open a port to listen on
        print("[!] Please wait for the remote connection to open")
        time.sleep(5)
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

    def is_connected(self):
        transport = self.client_connection.get_transport() if self.client_connection else None
        return transport and transport.is_active()

    def get_drive_info(self):
        if not self.is_connected():
            self._connect()
        return self.client_connection.exec_command(self.CMD_DRIVE_ENUMERATION)

    def _connect(self):
        try:
            with open(PRIVATE_KEY, 'r') as _key:
                pk = paramiko.RSAKey.from_private_key(_key)
        except IOError:
            print("Cannot open key")
            sys.exit()
        self.client_connection.connect(REMOTE_SERVER, username=self.username, pkey=pk)

    def execute_command(self, command):
        i, d, e = self.client_connection.exec_command(command)
