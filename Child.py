from Drive import Drive


class Child(Drive):

    def __init__(self, data, parent: Drive):
        self.data = data
        self.name = self._get_attrib('name')
        self.uuid = self._get_attrib('uuid')
        self.fstype = self._get_attrib('fstype')
        self.serial = self._get_attrib('serial')
        self.size = int(self._get_attrib('size'))
        self.free = int(self._get_attrib('fsavail'))
        self.mount_point = self._get_attrib('mountpoint')
        self.parent = parent
        self.child = True

    def get_parent(self):
        return self.parent

    def is_child(self):
        return self.child