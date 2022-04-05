#!/usr/bin/env python3
from Child import Child

from utils import *
import sys
import pyinotify
import json
import asyncore
import asyncio
import zlib
import time
from watchgod import awatch
import os
import threading
from Drive import Drive
from connection_manager import ConnectionManager
from connection_manager import *
from multiprocessing.pool import ThreadPool
import multiprocessing
from random import randint
import threading
import time
import random
from asyncio import coroutine

EXCLUDED_DRIVES = {'loop', 'nvme0n1'}  # Drives to exclude
MAX_THREADS = 3  # Number of threads that can run concurrently.


class DirectoryWatcher:
    wm = pyinotify.WatchManager()

    def __init__(self, directory, handler, loop):
        self.watcher = pyinotify.WatchManager()
        # self.notifier = pyinotify.ThreadedNotifier(self.watcher, default_proc_fun=handler)
        self.notifier = pyinotify.AsyncioNotifier(self.watcher, loop, default_proc_fun=handler)
        self.add_dir_to_watch(directory)

    def add_dir_to_watch(self, directory):
        AfsClient.print_statement(f"Adding {directory} to watch list for file creation")
        self.watcher.add_watch(directory, pyinotify.ALL_EVENTS)


def main():
    afsclient = AfsClient()


class AfsClient:
    WATCH_DIRECTORY = '/mnt/output/testing'
    PENDING_JOBS = []
    Drives = []
    VERSION = 1.0
    BANNER = f"""
                                                                          
                                                                          
               AAA               FFFFFFFFFFFFFFFFFFFFFF   SSSSSSSSSSSSSSS 
              A:::A              F::::::::::::::::::::F SS:::::::::::::::S
             A:::::A             F::::::::::::::::::::FS:::::SSSSSS::::::S
            A:::::::A            FF::::::FFFFFFFFF::::FS:::::S     SSSSSSS
           A:::::::::A             F:::::F       FFFFFFS:::::S            
          A:::::A:::::A            F:::::F             S:::::S            
         A:::::A A:::::A           F::::::FFFFFFFFFF    S::::SSSS         
        A:::::A   A:::::A          F:::::::::::::::F     SS::::::SSSSS    
       A:::::A     A:::::A         F:::::::::::::::F       SSS::::::::SS  
      A:::::AAAAAAAAA:::::A        F::::::FFFFFFFFFF          SSSSSS::::S 
     A:::::::::::::::::::::A       F:::::F                         S:::::S
    A:::::AAAAAAAAAAAAA:::::A      F:::::F                         S:::::S
   A:::::A             A:::::A   FF:::::::FF           SSSSSSS     S:::::S
  A:::::A               A:::::A  F::::::::FF           S::::::SSSSSS:::::S
 A:::::A                 A:::::A F::::::::FF           S:::::::::::::::SS 
AAAAAAA                   AAAAAAAFFFFFFFFFFF            SSSSSSSSSSSSSSS   
                                                                          
                                                       version: {VERSION} """

    @staticmethod
    def print_statement(statement):
        print(f"[*] {statement}")

    def job_monitor(self):
        while True:
            job = self.work_queue.get()

            if job:
                # print("GOT JOB")
                self.loop.call_soon_threadsafe(self.connection.process_job(job))
                # self.queue.task_done()
            # if len(self.PENDING_JOBS) != 0:
            #     job = self.PENDING_JOBS.pop()
            #     await self.connection.process_job(job)
            # self.print_statement(" No Jobs....")
            # await asyncio.sleep(5)

    def query_drive_info_thread(self):
        # This thread is responsible for keeping the drive information current

        while True:
            self.print_statement("Querying Drive Info")
            self.populate_drive_info()
            time.sleep(5)

    async def rnd_sleep(self, t):
        # sleep for T seconds on average
        await asyncio.sleep(t * random.random() * 2)

    def create_job(self, job: TransferJob):
        if job not in self.PENDING_JOBS:
            self.print_statement(f"Added Job: {job.crc32} to Pending Jobs.")
            asyncio.run_coroutine_threadsafe(self.work_queue.put(job), self.loop)
            self.PENDING_JOBS.append(job)
            self.print_statement(f'Current #of Pending Jobs: {len(self.PENDING_JOBS)}')

    def remove_job(self, job):
        if job in self.PENDING_JOBS:
            self.print_statement(f"Removed {job.get_filename()} of size {job.get_filesize}")
            self.PENDING_JOBS.remove(job)

    def __init__(self):
        self.loop = asyncio.get_event_loop()

        print(self.BANNER)
        self.pool = ThreadPool(processes=MAX_THREADS)

        AfsClient.print_statement(f"Connecting to {REMOTE_SERVER}")
        self.connection = ConnectionManager(REMOTE_SERVER, PRIVATE_KEY, USERNAME)

        AfsClient.print_statement(f"Querying Server {REMOTE_SERVER} for drive information...")
        self.populate_drive_info()

        # sleep_time = 5
        # self.query_thread = threading.Thread(target=self.query_drive_info_thread(), name="QueryDriveInfo" )
        # self.query_thread.setDaemon(True)
        # self.query_thread.join()
        # self.query_thread.start()

        AfsClient.print_statement("Starting DirectoryWatcher...")
        # self.dir_watcher = DirectoryWatcher('/home/ril3y/tmp', self.watcher_callback)
        self.dir_watcher = DirectoryWatcher(self.WATCH_DIRECTORY, self.watcher_callback, self.loop)
        #self.dir_watcher.notifier.start()
        self.print_statement("AFS running, watching for new files")

        # self.procs = []
        # self.process = multiprocessing.Process(targe=self.query_drive_info_thread())

        self.tasks = []
        self.work_queue = asyncio.Queue()
        # asyncio.run(self.worker())
        # blocking_fut = self.loop.run_in_executor(None, self.job_monitor())
        # task = asyncio.Task(self.job_monitor())
        # messages = await self.queue.get()
        # self.loop.run_forever()
        self.loop.create_task(self.worker())

        self.loop.run_forever()


    async def worker(self):
        self.print_statement("Started Worker Loop")
        while True:
            # Get a "work item" out of the queue.
            job = await self.work_queue.get()

            # Sleep for the "sleep_for" seconds.
            self.print_statement(f"Processing Job {job.get_filename()}")
            self.connection.open_file_connection(job)
            await asyncio.sleep(.5)

            # Notify the queue that the "work item" has been processed.
            self.work_queue.task_done()

    def watcher_callback(self, evt: pyinotify.ProcessEvent):
        # if evt.maskname == "IN_ACCESS":
        #     pass
        # else:
        #     print(f"EVENT: {evt.maskname} : {evt}")
        if evt.maskname == "IN_MOVED_TO" and evt.pathname.endswith(
                ".plot"):  # This is used for my application but you can put IN_CREATE ETC
            self.print_statement(f"New File Detected: {evt.pathname}")
            start_time = time.time()
            self.print_statement(f"Calculating CRC32... Please wait...")
            crc = crc32(evt.pathname)
            print(f"CRC32 Calculation took {(time.time() - start_time)} seconds!")
            print(f"CRC32: {crc}")
            current_drive = self.get_drive_with_most_free_space()
            if current_drive.check_file_fits(evt.pathname):
                self.print_statement(
                    f'File {evt.pathname} is bytes {os.path.getsize(evt.pathname)} will fit in {current_drive.get_name()} with {current_drive.get_free_space()} bytes')
                j = TransferJob(evt.pathname, crc32=crc, destination_drive=current_drive)
                self.create_job(j)


        elif evt.maskname == "IN_DELETE" and evt.pathname.endswith(".plot"):
            self.print_statement(f"File: {evt.pathname} has been deleted....")

    def order_drives_by_free_space(self):
        ordered_list = []
        tmp_drive_iterator = self.Drives

        current_high_free_value = 0
        current_high_free_drive = None

        while len(tmp_drive_iterator) is not 0:
            for d in list(tmp_drive_iterator):
                if d.free is not None and d.free > current_high_free_value:
                    current_high_free_value = d.free
                    current_high_free_drive = d

                if 'children' in d.__dict__:
                    if len(d.children) != 0:
                        for c in d.children:
                            if c.free is not None and c.free > current_high_free_value:
                                current_high_free_drive = c
                                current_high_free_value = c.free

            if current_high_free_drive is None:
                # This means either all the remaining drives have the same free space:
                # Or more than likely they are all 0
                current_high_free_drive = d

            ordered_list.append(current_high_free_drive)
            # print(f'Added: {current_high_free_drive.name} with {current_high_free_drive.get_free_space(True)}')

            if current_high_free_drive.is_child():
                # Remove the high child from parent drive
                current_high_free_drive.get_parent().children.remove(current_high_free_drive)

                if len(current_high_free_drive.get_parent().children) == 0:
                    # if the children are 0 now on the parent remove the parent too!
                    tmp_drive_iterator.remove(current_high_free_drive.get_parent())

                # if len(current_high_free_drive.get_parent().get_children()) == 0 and current_high_free_drive.get_parent() in tmp_drive_iterator:
                #     tmp_drive_iterator.remove(current_high_free_drive.get_parent())
                # else:
                #     if len(current_high_free_drive.get_parent().children) != 0:
                #         tmp_drive_iterator.append(current_high_free_drive.get_parent())

            else:
                tmp_drive_iterator.remove(current_high_free_drive)

            current_high_free_drive = None
            current_high_free_value = 0
        return ordered_list

    def get_drive_with_most_free_space(self):
        self.populate_drive_info()  # Call this to refresh drive information since last time called
        current_hv_fs = 0
        cur_drive_free_space = 0
        for d in self.Drives:
            if d.free is not None and d.free > cur_drive_free_space:
                cur_drive_free_space = d.free
                current_hv_fs = d
            else:
                if 'children' in d.__dict__:
                    # walk children
                    for c in d.children:
                        if c.free is not None and c.free > cur_drive_free_space:
                            current_hv_fs = c
                            cur_drive_free_space = c.free

        return current_hv_fs

    def _get_drive_generic(self, attr: str, val: str):
        for d in self.Drives:
            if d.__dict__[attr] == val:
                return d
            if 'children' in d.__dict__:

                if len(d.children) != 0:
                    for c in d.children:
                        if c.__dict__[attr] == val:
                            return c

    def get_drive_by_serial(self, serial: str):
        return self._get_drive_generic('serial', serial)

    def get_drive_info_by_uuid(self, uuid: str):
        return self._get_drive_generic('uuid', uuid)

    def populate_drive_info(self):
        stdin, stdout, stderr = self.connection.get_drive_info()

        drive_info = json.loads(stdout.read())

        for drive in drive_info['blockdevices']:
            for excluded_drive in EXCLUDED_DRIVES:
                skip_flag = False
                if excluded_drive in drive['name']:
                    # print(f"Skipping {drive['name']} it's excluded")
                    skip_flag = True
                    break

            if not skip_flag:
                # Create new drive object
                d = Drive(drive)
                self.Drives.append(d)
                skip_flag = False


if __name__ == "__main__":
   main()
