"""Container-specific tests for selv decorator."""

from selv import selv


def test_set_initialization():
    """Test set initialization is tracked."""

    @selv
    class TestClass:
        def __init__(self):
            self.items = {1, 2, 3}

    obj = TestClass()
    history = obj.view_changelog("items")

    assert len(history) >= 1
    assert history[0]["from"] is None
    assert isinstance(history[0]["to"], set)
    assert history[0]["to"] == {1, 2, 3}


def test_set_add_tracking():
    """Test set add operation is tracked."""

    @selv
    class TestClass:
        def __init__(self):
            self.items = {1, 2, 3}

    obj = TestClass()
    obj.items.add(4)

    history = obj.view_changelog("items")
    assert len(history) >= 2
    assert 4 in history[-1]["to"]


def test_set_remove_tracking():
    """Test set remove operation is tracked."""

    @selv
    class TestClass:
        def __init__(self):
            self.items = {1, 2, 3}

    obj = TestClass()
    obj.items.remove(2)

    history = obj.view_changelog("items")
    assert len(history) >= 2
    assert 2 not in history[-1]["to"]


def test_set_discard_tracking():
    """Test set discard operation is tracked."""

    @selv
    class TestClass:
        def __init__(self):
            self.items = {1, 2, 3}

    obj = TestClass()
    obj.items.discard(3)

    history = obj.view_changelog("items")
    assert len(history) >= 2
    assert 3 not in history[-1]["to"]


def test_set_pop_tracking():
    """Test set pop operation is tracked."""

    @selv
    class TestClass:
        def __init__(self):
            self.items = {1, 2, 3}

    obj = TestClass()
    original_size = len(obj.items)
    obj.items.pop()

    history = obj.view_changelog("items")
    assert len(history) >= 2
    assert len(history[-1]["to"]) == original_size - 1


def test_set_clear_tracking():
    """Test set clear operation is tracked."""

    @selv
    class TestClass:
        def __init__(self):
            self.items = {1, 2, 3}

    obj = TestClass()
    obj.items.clear()

    history = obj.view_changelog("items")
    assert len(history) >= 2
    assert len(history[-1]["to"]) == 0


def test_set_update_tracking():
    """Test set update operation is tracked."""

    @selv
    class TestClass:
        def __init__(self):
            self.items = {1, 2, 3}

    obj = TestClass()
    obj.items.update([4, 5])

    history = obj.view_changelog("items")
    assert len(history) >= 2
    assert 4 in history[-1]["to"]
    assert 5 in history[-1]["to"]


def test_set_intersection_update_tracking():
    """Test set intersection_update operation is tracked."""

    @selv
    class TestClass:
        def __init__(self):
            self.items = {1, 2, 3, 4, 5}

    obj = TestClass()
    obj.items.intersection_update({2, 3, 6})

    history = obj.view_changelog("items")
    assert len(history) >= 2
    assert 2 in history[-1]["to"]
    assert 3 in history[-1]["to"]
    assert 1 not in history[-1]["to"]


def test_set_difference_update_tracking():
    """Test set difference_update operation is tracked."""

    @selv
    class TestClass:
        def __init__(self):
            self.items = {1, 2, 3, 4, 5}

    obj = TestClass()
    obj.items.difference_update({3, 4})

    history = obj.view_changelog("items")
    assert len(history) >= 2
    assert 3 not in history[-1]["to"]
    assert 4 not in history[-1]["to"]


def test_set_symmetric_difference_update_tracking():
    """Test set symmetric_difference_update operation is tracked."""

    @selv
    class TestClass:
        def __init__(self):
            self.items = {1, 2, 3}

    obj = TestClass()
    obj.items.symmetric_difference_update({3, 4, 5})

    history = obj.view_changelog("items")
    assert len(history) >= 2
    assert 3 not in history[-1]["to"]  # Removed (was in both)
    assert 4 in history[-1]["to"]  # Added (was only in other)
    assert 5 in history[-1]["to"]  # Added (was only in other)


def test_tuple_initialization():
    """Test tuple initialization is tracked."""

    @selv
    class TestClass:
        def __init__(self):
            self.coords = (1, 2, 3)

    obj = TestClass()
    history = obj.view_changelog("coords")

    assert len(history) >= 1
    assert history[0]["from"] is None
    assert isinstance(history[0]["to"], tuple)
    assert history[0]["to"] == (1, 2, 3)


def test_tuple_reassignment_tracking():
    """Test tuple reassignment is tracked (tuples are immutable)."""

    @selv
    class TestClass:
        def __init__(self):
            self.coords = (1, 2, 3)

    obj = TestClass()
    obj.coords = (4, 5, 6)

    history = obj.view_changelog("coords")
    assert len(history) >= 2
    assert history[-1]["to"] == (4, 5, 6)


def test_empty_set_tracking():
    """Test empty set initialization and operations are tracked."""

    @selv
    class TestClass:
        def __init__(self):
            self.empty_set = set()

    obj = TestClass()

    history = obj.view_changelog("empty_set")
    assert len(history) >= 1
    assert history[0]["from"] is None
    assert history[0]["to"] == set()


def test_set_method_return_values():
    """Test set methods return correct values."""

    @selv
    class TestClass:
        def __init__(self):
            self.items = {1, 2, 3}

    obj = TestClass()

    # Test add returns None
    result = obj.items.add(4)
    assert result is None
    assert 4 in obj.items

    # Test remove returns None
    result = obj.items.remove(2)
    assert result is None
    assert 2 not in obj.items


def test_set_in_dict_tracking():
    """Test set inside dict is tracked."""

    @selv
    class TestClass:
        def __init__(self):
            self.data = {"tags": {"python", "decorator"}}

    obj = TestClass()
    obj.data["tags"].add("observable")

    history = obj.view_changelog("data")
    assert len(history) >= 2
    # When set inside dict is modified, it logs the set change
    # not the dict change (current architecture limitation)
    assert "observable" in history[-1]["to"]


def test_format_value_set():
    """Test _format_value method works for sets."""

    @selv
    class TestClass:
        def __init__(self):
            self.items = {1, 2, 3}

    obj = TestClass()

    history = obj.view_changelog(format="attr")
    assert "items" in history
    record_str = str(history["items"][0])
    assert "{" in record_str
    assert "}" in record_str


def test_format_value_tuple():
    """Test _format_value method works for tuples."""

    @selv
    class TestClass:
        def __init__(self):
            self.coords = (1, 2, 3)

    obj = TestClass()

    history = obj.view_changelog(format="attr")
    assert "coords" in history
    record_str = str(history["coords"][0])
    assert "(" in record_str
    assert ")" in record_str
