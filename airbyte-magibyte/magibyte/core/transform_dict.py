import collections

from magibyte.core.extrapolation import extrapolate


class TransformDict(collections.UserDict):
    def __init__(self, dict, transform=lambda x: x):
        super(TransformDict, self).__init__(dict)
        self.transform = transform

    def __getitem__(self, item):
        value = self.data[item]
        return self.transform(value)
