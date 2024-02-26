from .base_backend import BaseBackend


class FileBackend(BaseBackend):

    def __init__(self, output_directory: str):
        self.output_directory = output_directory

    def write(self):
        raise NotImplementedError

    def read(self):
        raise NotImplementedError

    def compare(self):
        raise NotImplementedError
