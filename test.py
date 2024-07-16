class TestClass:
    name: str = "test1"

    def get_name(self):
        _name = self.name

        return _name


tc = TestClass()

name = tc.name
print(name)
name = "test2"
print(tc.name)
