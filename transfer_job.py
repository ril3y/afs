from Drive import Drive
import os

class TransferJob:

    def __init__(self, filename, crc32, destination_drive: Drive):
        self.filename = filename
        self.destination_drive = destination_drive
        self.file_size = os.path.getsize(filename)
        self.is_complete = False
        self.destination = destination_drive.get_mountpoint()
        self.crc32 = 0

    def build_remote_filename(self):
        return self.get_destination()+os.sep+os.path.basename(self.filename)

    def get_filename(self):
        return self.filename

    def set_crc32(self, _crc32):
        self.crc32 = _crc32

    def get_crc32(self):
        return self.crc32

    def get_file_size(self):
        return self.file_size

    def get_destination(self):
        return self.destination

    def set_destination(self, location):
        self.destination = location
