class Stream:

    def __init__(self, name, schema):
        self.name = name
        self.schema = schema

    def __iter__(self):
        return self

    def __next__(self):
        return {}, {}
