from datetime import datetime

import pytest

from selfie import selfie


def test_basic_decorator():

    @selfie
    class TestClass:
        def __init__(self):
            self.x = 1
            self.y = 2

    obj = TestClass()
    obj.x = 3
    obj.y = 4

    history = obj.get_change_history(format="attr")
    assert "x" in history
    assert "y" in history
    assert len(history["x"]) == 2
    assert len(history["y"]) == 2


def test_private_attributes_not_tracked_by_default():

    @selfie(track_private=False)
    class TestClass:
        def __init__(self):
            self.public = "public"
            self._private = "private"

    obj = TestClass()
    history = obj.get_change_history(format="attr")
    assert "public" in history
    assert "_private" not in history


def test_private_attributes_tracked_when_enabled():

    @selfie(track_private=True)
    class TestClass:
        def __init__(self):
            self.public = "public"
            self._private = "private"

    obj = TestClass()
    history = obj.get_change_history(format="attr")
    assert "public" in history
    assert "_private" in history


def test_dict_element_tracking():

    @selfie
    class TestClass:
        def __init__(self):
            self.data = {"key1": "value1"}

    obj = TestClass()
    obj.data["key1"] = "updated"
    obj.data["key2"] = "value2"

    history = obj.get_change_history("data")
    assert len(history) >= 3

    assert history[0]["from"] is None
    assert isinstance(history[0]["to"], dict)
    assert history[0]["to"] == {"key1": "value1"}
    assert history[1]["from"] == {"key1": "value1"}
    assert history[1]["to"] == {"key1": "updated"}
    assert history[2]["from"] == {"key1": "updated"}
    assert history[2]["to"] == {"key1": "updated", "key2": "value2"}


def test_list_element_tracking():

    @selfie
    class TestClass:
        def __init__(self):
            self.items = [1, 2, 3]

    obj = TestClass()
    obj.items[0] = 10
    obj.items.append(4)
    obj.items.pop()

    history = obj.get_change_history("items")
    assert len(history) >= 4

    assert history[0]["from"] is None
    assert isinstance(history[0]["to"], list)
    assert history[0]["to"] == [1, 2, 3]
    assert history[1]["from"] == [1, 2, 3]
    assert history[1]["to"] == [10, 2, 3]
    assert history[2]["from"] == [10, 2, 3]
    assert history[2]["to"] == [10, 2, 3, 4]
    assert history[3]["from"] == [10, 2, 3, 4]
    assert history[3]["to"] == [10, 2, 3]


def test_multiple_instances():

    @selfie
    class TestClass:
        def __init__(self, value):
            self.value = value

    obj1 = TestClass(1)
    obj2 = TestClass(2)

    obj1.value = 10
    obj2.value = 20

    history1 = obj1.get_change_history(format="attr")
    history2 = obj2.get_change_history(format="attr")

    assert history1["value"][1]["to"] == 10
    assert history2["value"][1]["to"] == 20


def test_get_change_history_format():

    @selfie
    class TestClass:
        def __init__(self):
            self.value = 0

    obj = TestClass()
    obj.value = 1
    obj.value = 2

    history = obj.get_change_history()
    assert isinstance(history, list)
    assert len(history) == 3

    for record in history:
        assert isinstance(record, dict)
        assert "time" in record
        assert "attr" in record
        assert "from" in record
        assert "to" in record
        assert isinstance(record["time"], datetime)
        assert record["attr"] == "value"

    assert history[0]["from"] is None
    assert history[0]["to"] == 0
    assert history[1]["from"] == 0
    assert history[1]["to"] == 1
    assert history[2]["from"] == 1
    assert history[2]["to"] == 2

    attr_history = obj.get_change_history(format="attr")
    assert isinstance(attr_history, dict)
    assert "value" in attr_history
    assert isinstance(attr_history["value"], list)
    assert len(attr_history["value"]) == 3

    value_history = obj.get_change_history("value")
    assert isinstance(value_history, list)
    assert len(value_history) == 3
    assert value_history[2]["to"] == 2


def test_empty_history():

    @selfie
    class TestClass:
        def __init__(self):
            pass

    obj = TestClass()

    history = obj.get_change_history()
    assert isinstance(history, list)
    assert len(history) == 0

    attr_history = obj.get_change_history(format="attr")
    assert isinstance(attr_history, dict)
    assert len(attr_history) == 0

    nonexistent_history = obj.get_change_history("nonexistent")
    assert isinstance(nonexistent_history, list)
    assert len(nonexistent_history) == 0


def test_mixed_features():

    @selfie(track_private=True)
    class TestClass:
        def __init__(self):
            self.public_dict = {"a": 1}
            self._private_list = [1, 2]

    obj = TestClass()
    obj.public_dict["b"] = 2
    obj._private_list.append(3)

    public_history = obj.get_change_history("public_dict")
    private_history = obj.get_change_history("_private_list")

    assert len(public_history) >= 2
    assert len(private_history) >= 2

    flat_history = obj.get_change_history(format="flat")
    assert isinstance(flat_history, list)
    assert len(flat_history) >= 4

    attr_history = obj.get_change_history(format="attr")
    assert isinstance(attr_history, dict)
    assert "public_dict" in attr_history
    assert "_private_list" in attr_history
    assert len(attr_history["public_dict"]) >= 2
    assert len(attr_history["_private_list"]) >= 2


def test_decorator_without_parentheses():

    @selfie
    class SimpleClass:
        def __init__(self):
            self.value = "test"

    obj = SimpleClass()
    obj.value = "updated"

    history = obj.get_change_history(format="attr")
    assert "value" in history
    assert len(history["value"]) == 2


def test_nested_containers():

    @selfie
    class TestClass:
        def __init__(self):
            self.nested = {"list": [1, 2, 3]}

    obj = TestClass()

    obj.nested["key"] = "value"

    history = obj.get_change_history("nested")
    assert len(history) >= 2

    assert history[0]["from"] is None
    assert isinstance(history[0]["to"], dict)
    assert history[0]["to"] == {"list": [1, 2, 3]}
    assert history[1]["from"] == {"list": [1, 2, 3]}
    assert history[1]["to"] == {"list": [1, 2, 3], "key": "value"}


def test_format_value_method():

    @selfie
    class TestClass:
        def __init__(self):
            self.str_val = "hello"
            self.int_val = 42
            self.float_val = 3.14
            self.bool_val = True
            self.none_val = None
            self.list_val = [1, 2, 3]
            self.dict_val = {"a": 1}

    obj = TestClass()

    history = obj.get_change_history(format="attr")
    for attr in ["str_val", "int_val", "float_val", "bool_val", "none_val"]:
        assert attr in history
        record = history[attr][0]
        assert (
            "'hello'" in str(record)
            or "42" in str(record)
            or "3.14" in str(record)
            or "True" in str(record)
            or "None" in str(record)
        )

    assert "[1, 2, 3]" in str(history["list_val"][0])
    assert "{'a': 1}" in str(history["dict_val"][0])


def test_pop_method_type_hint():

    @selfie
    class TestClass:
        def __init__(self):
            self.items = [1, 2, 3, 4, 5]

    obj = TestClass()

    popped = obj.items.pop()
    assert popped == 5

    popped = obj.items.pop(0)
    assert popped == 1

    class CustomIndex:
        def __index__(self):
            return 0

    custom_idx = CustomIndex()
    popped = obj.items.pop(custom_idx)
    assert popped == 2

    history = obj.get_change_history("items")
    assert len(history) >= 4

    assert history[0]["from"] is None
    assert isinstance(history[0]["to"], list)
    assert history[0]["to"] == [1, 2, 3, 4, 5]

    assert history[1]["from"] == [1, 2, 3, 4, 5]
    assert history[1]["to"] == [1, 2, 3, 4]

    assert history[2]["from"] == [1, 2, 3, 4]
    assert history[2]["to"] == [2, 3, 4]


def test_invalid_format_parameter():

    @selfie
    class TestClass:
        def __init__(self):
            self.value = 0

    obj = TestClass()
    obj.value = 1

    with pytest.raises(ValueError, match="format must be 'flat' or 'attr'"):
        obj.get_change_history(format="invalid")

    with pytest.raises(ValueError, match="format must be 'flat' or 'attr'"):
        obj.get_change_history(format="")

    flat_history = obj.get_change_history(format="flat")
    assert isinstance(flat_history, list)

    attr_history = obj.get_change_history(format="attr")
    assert isinstance(attr_history, dict)
