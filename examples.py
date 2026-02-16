import random

from selfie import selfie


@selfie
class TestClass:
    def __init__(self):
        self.number = 0
        self.kv = {"key": 0}
        self.list = [1, 2, 3]

    def increment(self):
        self.number += 1

    def decrement(self):
        self.number -= 1

    def modify_kv(self):
        self.kv["key"] = random.randint(1, 100)

    def modify_list(self):
        self.list[0] = random.randint(10, 99)
        self.list.append(random.randint(10, 99))


if __name__ == "__main__":
    test_class = TestClass()
    test_class.increment()
    test_class.decrement()
    test_class.modify_kv()
    test_class.modify_kv()
    test_class.modify_list()

    print("\nChanges history (flat):")
    print(test_class.get_change_history())

    print("\nChanges history (attr):")
    print(test_class.get_change_history(format="attr"))
