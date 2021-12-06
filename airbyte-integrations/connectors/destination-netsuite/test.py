class Letter:
    def __init__(self, name: str):
        self._name=name

    def get_name(self):
        return self._name

    def get_name_plus(self, prefix: str):
        return prefix + self._name
        
    def get_method(self, name: str):
        return getattr(self, name)

    def solve_for(self, name: str):
        do = f"{name}"
        if hasattr(self, do) and callable(func := getattr(self, do)):
            print(func())

class A(Letter):
    def __init__(self, name: str = "A"):
        super().__init__(name)

a = A("A")
method=a.get_method("get_name_plus")
print(method(prefix="Hello "))