from typing import override, Annotated, get_args

print("running..........")

haha = object()

Name = Annotated[str, "Must be non-empty and capitalized", {"gt": 0, "lt": 10}, haha]
Age = Annotated[int, "Range: 0-120"]

print(Name)
print(get_args(Name))


class Human:
    name: Name
    age: int

    def __init__(self, name: Name, age: int) -> None:
        self.name = name
        self.age = age

    def walk(self):
        pass


class Child(Human):
    school_name: str

    @override
    def __init__(self, name: Name, age: int, school_name: str) -> None:
        super().__init__(name, age)
        self.school_name = school_name

    @override
    def walk(self):
        pass
