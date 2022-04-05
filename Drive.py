import Child
import os

from utils import humanbytes


class Drive:

    def __init__(self, data):
        self.data = data
        self.name = self._get_attrib('name')
        self.uuid = self._get_attrib('uuid')
        self.fstype = self._get_attrib('fstype')
        self.serial = self._get_attrib('serial')
        self.size = int(self._get_attrib('size'))
        self.free = int(self._get_attrib('fsavail'))
        self.mount_point = self._get_attrib('mountpoint')
        self.child = False

        if "children" in data.keys():
            self.children = []
            for child in data['children']:
                self.children.append(Child.Child(child, self))

    def is_child(self):
        return self.child

    def get_name(self):
        return self.name

    def get_serial(self):
        return self.serial

    def get_fstype(self):
        return self.fstype

    def get_mountpoint(self):
        if self.mount_point is 0:
            return "not mounted"
        return self.mount_point

    def get_children(self):
        return self.children

    def get_uuid(self):
        return self.uuid

    def get_free_space(self, human=False):
        if human:
            return humanbytes(self.free)
        return self.free

    def get_size_space(self, human=False):
        if human:
            return humanbytes(self.size)
        return self.size

    def get_child_by_uuid(self, uuid: str):
        if len(self.children) != 0:
            for c in self.children:
                if c.uuid == uuid:
                    return c

    def _get_attrib(self, atr):
        if self.data[atr] == str:
            return self.data[atr].lower()
        else:
            if self.data[atr] is None:
                return 0
            return self.data[atr]

    def check_file_fits(self, filename):
        # This method is used to see if a file can fit in the free space of this drive
        if os.path.getsize(filename) < self.get_free_space():
            return True
        else:
            # Does not fit
            return False

    def __repr__(self):
        return f"Drive: {self.name} FileSystem: {self.fstype} Size: {self.size} Free: {self.free}"