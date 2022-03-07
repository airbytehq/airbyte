class DataType:
    def __init__(self, name: str, length: str = None):
        self.name = name
        self.length = length

    def __str__(self):
        if self.length:
            return f"{self.name}({self.length})"
        else:
            return self.name


class Field:
    def __init__(self, name: str, data_type: DataType, value: object = None):
        self.name = name
        self.data_type = data_type
        self.value = value

    def __str__(self):
        return f""""{self.name}" {self.data_type}"""

