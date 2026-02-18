"""Tests for custom actions functionality in selv decorator."""

from selv import selv


def test_basic_custom_action():
    """Test basic custom action on attribute change."""
    action_called = []
    action_value = None

    def my_action(value):
        nonlocal action_called, action_value
        action_called.append(True)
        action_value = value

    @selv(actions={"x": my_action})
    class TestClass:
        def __init__(self):
            self.x = 1

    obj = TestClass()
    # Action should be called on initialization
    assert len(action_called) == 1
    assert action_value == 1

    # Reset tracking
    action_called.clear()
    action_value = None

    # Change the attribute
    obj.x = 2
    # Action should be called on change
    assert len(action_called) == 1
    assert action_value == 2


def test_multiple_attributes_with_actions():
    """Test multiple attributes with different actions."""
    x_called = []
    y_called = []

    def x_action(value):
        x_called.append(value)

    def y_action(value):
        y_called.append(value)

    @selv(actions={"x": x_action, "y": y_action})
    class TestClass:
        def __init__(self):
            self.x = 1
            self.y = 2

    obj = TestClass()
    assert len(x_called) == 1
    assert x_called[0] == 1
    assert len(y_called) == 1
    assert y_called[0] == 2

    # Change attributes
    obj.x = 10
    obj.y = 20

    assert len(x_called) == 2
    assert x_called[1] == 10
    assert len(y_called) == 2
    assert y_called[1] == 20


def test_action_not_called_for_other_attributes():
    """Test that actions are only called for specified attributes."""
    action_called = []

    def my_action(value):
        action_called.append(value)

    @selv(actions={"x": my_action})
    class TestClass:
        def __init__(self):
            self.x = 1
            self.y = 2  # No action for y

    obj = TestClass()
    assert len(action_called) == 1  # Only for x initialization
    assert action_called[0] == 1

    # Change y - action should not be called
    obj.y = 3
    assert len(action_called) == 1  # Still only 1 call


def test_action_with_container_attributes():
    """Test actions work with container attributes (dict, list, set)."""
    dict_action_called = []
    list_action_called = []
    set_action_called = []

    def dict_action(value):
        dict_action_called.append(value)

    def list_action(value):
        list_action_called.append(value)

    def set_action(value):
        set_action_called.append(value)

    @selv(
        actions={"my_dict": dict_action, "my_list": list_action, "my_set": set_action}
    )
    class TestClass:
        def __init__(self):
            self.my_dict = {"a": 1}
            self.my_list = [1, 2, 3]
            self.my_set = {1, 2, 3}

    obj = TestClass()
    assert len(dict_action_called) == 1
    assert dict_action_called[0] == {"a": 1}
    assert len(list_action_called) == 1
    assert list_action_called[0] == [1, 2, 3]
    assert len(set_action_called) == 1
    assert set_action_called[0] == {1, 2, 3}

    # Modify containers
    obj.my_dict["b"] = 2
    obj.my_list.append(4)
    obj.my_set.add(5)

    # Actions should be called for container modifications
    assert len(dict_action_called) == 2
    assert dict_action_called[1] == {"a": 1, "b": 2}
    assert len(list_action_called) == 2
    assert list_action_called[1] == [1, 2, 3, 4]
    assert len(set_action_called) == 2
    assert set_action_called[1] == {1, 2, 3, 5}


def test_action_receives_correct_value():
    """Test that action receives the actual new value."""
    received_values = []

    def my_action(value):
        received_values.append(value)

    @selv(actions={"x": my_action})
    class TestClass:
        def __init__(self):
            self.x = "initial"

    obj = TestClass()
    assert received_values == ["initial"]

    obj.x = "changed"
    assert received_values == ["initial", "changed"]

    obj.x = 123
    assert received_values == ["initial", "changed", 123]

    obj.x = None
    assert received_values == ["initial", "changed", 123, None]


def test_action_with_excluded_attributes():
    """Test that actions work with excluded attributes."""
    action_called = []

    def my_action(value):
        action_called.append(value)

    @selv(actions={"x": my_action}, exclude=["y"])
    class TestClass:
        def __init__(self):
            self.x = 1  # Has action
            self.y = 2  # Excluded, no tracking

    obj = TestClass()
    assert len(action_called) == 1
    assert action_called[0] == 1

    # Change x - action should be called
    obj.x = 3
    assert len(action_called) == 2
    assert action_called[1] == 3

    # Change y - no action since it's excluded
    obj.y = 4
    assert len(action_called) == 2  # No change


def test_action_with_private_attributes():
    """Test actions with private attributes when track_private=True."""
    action_called = []

    def my_action(value):
        action_called.append(value)

    @selv(actions={"_private": my_action}, track_private=True)
    class TestClass:
        def __init__(self):
            self._private = "secret"

    obj = TestClass()
    assert len(action_called) == 1
    assert action_called[0] == "secret"

    obj._private = "new_secret"
    assert len(action_called) == 2
    assert action_called[1] == "new_secret"


def test_no_action_for_private_when_track_private_false():
    """Test that actions are not called for untracked private attributes"""
    action_called = []

    def my_action(value):
        action_called.append(value)

    @selv(actions={"_private": my_action}, track_private=False)
    class TestClass:
        def __init__(self):
            self._private = "secret"

    obj = TestClass()
    # Action should not be called because private attributes aren't tracked
    assert len(action_called) == 0

    obj._private = "new_secret"
    assert len(action_called) == 0


def test_action_with_custom_logger():
    """Test that actions work with custom logger."""
    action_called = []
    log_messages = []

    def my_action(value):
        action_called.append(value)

    def my_logger(message):
        log_messages.append(message)

    @selv(actions={"x": my_action}, logger=my_logger)
    class TestClass:
        def __init__(self):
            self.x = 1

    obj = TestClass()
    assert len(action_called) == 1
    assert action_called[0] == 1
    assert len(log_messages) > 0  # Logger should have been called

    # Change attribute
    obj.x = 2
    assert len(action_called) == 2
    assert action_called[1] == 2


def test_action_with_lambda():
    """Test that lambda functions can be used as actions."""
    results = []

    @selv(actions={"x": lambda v: results.append(f"x={v}")})
    class TestClass:
        def __init__(self):
            self.x = 1

    obj = TestClass()
    assert results == ["x=1"]

    obj.x = 2
    assert results == ["x=1", "x=2"]
