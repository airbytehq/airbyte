from magibyte.models.stream import Stream


class Source:
    def __iter__(self):
        return self

    def __next__(self):
        return Stream()