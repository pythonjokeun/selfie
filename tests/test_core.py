"""Core functionality tests for selv decorator."""

import pytest

from selv import selv


def test_basic_attribute_tracking():
    """Test basic attribute assignment tracking."""

    @selv
    class TestClass:
        def __init__(self):
            self.x = 1

    obj = TestClass()
    obj.x = 2

    history = obj.view_changelog("x")
    assert len(history) == 2
    assert history[0]["from"] is None
    assert history[0]["to"] == 1
    assert history[1]["from"] == 1
    assert history[1]["to"] == 2


def test_multiple_attributes_tracked():
    """Test that multiple attributes are tracked independently."""

    @selv
    class TestClass:
        def __init__(self):
            self.x = 1
            self.y = 2

    obj = TestClass()
    history = obj.view_changelog(format="attr")

    assert "x" in history
    assert "y" in history
    assert len(history["x"]) == 1
    assert len(history["y"]) == 1


def test_private_attributes_not_tracked_by_default():
    """Test private attributes are not tracked when track_private=False."""

    @selv(track_private=False)
    class TestClass:
        def __init__(self):
            self.public = "public"
            self._private = "private"

    obj = TestClass()
    history = obj.view_changelog(format="attr")

    assert "public" in history
    assert "_private" not in history


def test_private_attributes_tracked_when_enabled():
    """Test private attributes are tracked when track_private=True."""

    @selv(track_private=True)
    class TestClass:
        def __init__(self):
            self.public = "public"
            self._private = "private"

    obj = TestClass()
    history = obj.view_changelog(format="attr")

    assert "public" in history
    assert "_private" in history


def test_dict_element_tracking_initialization():
    """Test dict initialization is tracked."""

    @selv
    class TestClass:
        def __init__(self):
            self.data = {"key1": "value1"}

    obj = TestClass()
    history = obj.view_changelog("data")

    assert len(history) >= 1
    assert history[0]["from"] is None
    assert isinstance(history[0]["to"], dict)
    assert history[0]["to"] == {"key1": "value1"}


def test_dict_element_update_tracking():
    """Test dict element updates are tracked."""

    @selv
    class TestClass:
        def __init__(self):
            self.data = {"key1": "value1"}

    obj = TestClass()
    obj.data["key1"] = "updated"

    history = obj.view_changelog("data")
    assert len(history) >= 2
    assert history[1]["from"] == {"key1": "value1"}
    assert history[1]["to"] == {"key1": "updated"}


def test_dict_element_addition_tracking():
    """Test dict element additions are tracked."""

    @selv
    class TestClass:
        def __init__(self):
            self.data = {"key1": "value1"}

    obj = TestClass()
    obj.data["key2"] = "value2"

    history = obj.view_changelog("data")
    assert len(history) >= 2
    assert "key2" in history[-1]["to"]
    assert history[-1]["to"]["key2"] == "value2"


def test_list_element_tracking_initialization():
    """Test list initialization is tracked."""

    @selv
    class TestClass:
        def __init__(self):
            self.items = [1, 2, 3]

    obj = TestClass()
    history = obj.view_changelog("items")

    assert len(history) >= 1
    assert history[0]["from"] is None
    assert isinstance(history[0]["to"], list)
    assert history[0]["to"] == [1, 2, 3]


def test_list_element_update_tracking():
    """Test list element updates are tracked."""

    @selv
    class TestClass:
        def __init__(self):
            self.items = [1, 2, 3]

    obj = TestClass()
    obj.items[0] = 10

    history = obj.view_changelog("items")
    assert len(history) >= 2
    assert history[1]["from"] == [1, 2, 3]
    assert history[1]["to"] == [10, 2, 3]


def test_list_append_tracking():
    """Test list append operations are tracked."""

    @selv
    class TestClass:
        def __init__(self):
            self.items = [1, 2, 3]

    obj = TestClass()
    obj.items.append(4)

    history = obj.view_changelog("items")
    assert len(history) >= 2
    assert history[-1]["to"] == [1, 2, 3, 4]


def test_list_pop_tracking():
    """Test list pop operations are tracked."""

    @selv
    class TestClass:
        def __init__(self):
            self.items = [1, 2, 3, 4]

    obj = TestClass()
    obj.items.pop()

    history = obj.view_changelog("items")
    assert len(history) >= 2
    assert len(history[-1]["to"]) == 3


def test_multiple_instances_independent():
    """Test multiple instances have independent change histories."""

    @selv
    class TestClass:
        def __init__(self, value):
            self.value = value

    obj1 = TestClass(1)
    obj2 = TestClass(2)

    obj1.value = 10
    obj2.value = 20

    history1 = obj1.view_changelog("value")
    history2 = obj2.view_changelog("value")

    assert history1[-1]["to"] == 10
    assert history2[-1]["to"] == 20


def test_get_change_history_flat_format():
    """Test get_change_history returns flat list format."""

    @selv
    class TestClass:
        def __init__(self):
            self.value = 0

    obj = TestClass()
    obj.value = 1

    history = obj.view_changelog()
    assert isinstance(history, list)
    assert len(history) == 2
    assert history[0]["attr"] == "value"
    assert history[1]["attr"] == "value"


def test_get_change_history_attr_format():
    """Test get_change_history returns attribute dict format."""

    @selv
    class TestClass:
        def __init__(self):
            self.value = 0

    obj = TestClass()

    history = obj.view_changelog(format="attr")
    assert isinstance(history, dict)
    assert "value" in history
    assert isinstance(history["value"], list)


def test_get_change_history_specific_attribute():
    """Test get_change_history for specific attribute."""

    @selv
    class TestClass:
        def __init__(self):
            self.value = 0

    obj = TestClass()

    history = obj.view_changelog("value")
    assert isinstance(history, list)
    assert len(history) == 1
    assert history[0]["to"] == 0


def test_empty_history():
    """Test empty change history."""

    @selv
    class TestClass:
        def __init__(self):
            pass

    obj = TestClass()

    history = obj.view_changelog()
    assert isinstance(history, list)
    assert len(history) == 0

    attr_history = obj.view_changelog(format="attr")
    assert isinstance(attr_history, dict)
    assert len(attr_history) == 0


def test_nonexistent_attribute_history():
    """Test get_change_history for nonexistent attribute."""

    @selv
    class TestClass:
        def __init__(self):
            pass

    obj = TestClass()

    history = obj.view_changelog("nonexistent")
    assert isinstance(history, list)
    assert len(history) == 0


def test_decorator_without_parentheses():
    """Test @selv decorator without parentheses."""

    @selv
    class SimpleClass:
        def __init__(self):
            self.value = "test"

    obj = SimpleClass()

    history = obj.view_changelog(format="attr")
    assert "value" in history
    assert len(history["value"]) == 1


def test_nested_dict_initialization():
    """Test nested dict initialization tracking."""

    @selv
    class TestClass:
        def __init__(self):
            self.nested = {"list": [1, 2, 3]}

    obj = TestClass()

    history = obj.view_changelog("nested")
    assert len(history) >= 1
    assert history[0]["from"] is None
    assert isinstance(history[0]["to"], dict)
    assert "list" in history[0]["to"]


def test_nested_dict_update():
    """Test nested dict updates are tracked."""

    @selv
    class TestClass:
        def __init__(self):
            self.nested = {"list": [1, 2, 3]}

    obj = TestClass()
    obj.nested["key"] = "value"

    history = obj.view_changelog("nested")
    assert len(history) >= 2
    assert "key" in history[-1]["to"]
    assert history[-1]["to"]["key"] == "value"


def test_invalid_format_parameter():
    """Test invalid format parameter raises ValueError."""

    @selv
    class TestClass:
        def __init__(self):
            self.value = 0

    obj = TestClass()

    with pytest.raises(ValueError, match="format must be 'flat' or 'attr'"):
        obj.view_changelog(format="invalid")

    with pytest.raises(ValueError, match="format must be 'flat' or 'attr'"):
        obj.view_changelog(format="")


def test_valid_format_parameters():
    """Test valid format parameters work correctly."""

    @selv
    class TestClass:
        def __init__(self):
            self.value = 0

    obj = TestClass()

    flat_history = obj.view_changelog(format="flat")
    assert isinstance(flat_history, list)

    attr_history = obj.view_changelog(format="attr")
    assert isinstance(attr_history, dict)
