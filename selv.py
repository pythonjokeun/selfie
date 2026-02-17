"""Python decorator for logging attribute changes."""

__all__ = ["selv"]

import copy
from datetime import datetime
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    SupportsIndex,
    Type,
    TypeVar,
    Union,
)

T = TypeVar("T", bound=Any)


class ObservableDict(dict):
    """Dictionary that notifies parent of changes."""

    def __init__(self, *args, parent=None, attr_name=None, **kwargs):
        self._parent = parent
        self._attr_name = attr_name
        self._initializing = True
        super().__init__()
        # Process initial items and wrap them
        if len(args) > 0:
            if len(args) > 1:
                raise TypeError("expected at most 1 argument, got %d" % len(args))
            # Extract first argument safely
            first_arg = args[0]
            for key, value in dict(first_arg).items():
                self[key] = value
        for key, value in kwargs.items():
            self[key] = value
        self._initializing = False

    def __setitem__(self, key, value):
        old_container_state = self.copy() if self._parent else None
        wrapped_value = self._wrap_value(value)
        super().__setitem__(key, wrapped_value)
        if self._parent and self._attr_name and not self._initializing:
            new_container_state = self.copy()
            self._parent._selv_log_container_change(
                self._attr_name, old_container_state, new_container_state
            )

    def _wrap_value(self, value):
        """Wrap container values for observation."""
        if isinstance(value, dict):
            return ObservableDict(value, parent=self._parent, attr_name=self._attr_name)
        elif isinstance(value, list):
            return ObservableList(value, parent=self._parent, attr_name=self._attr_name)
        elif isinstance(value, set):
            return ObservableSet(value, parent=self._parent, attr_name=self._attr_name)
        return value

    def __delitem__(self, key):
        old_container_state = self.copy() if self._parent else None
        super().__delitem__(key)
        if self._parent and self._attr_name and not self._initializing:
            new_container_state = self.copy()
            self._parent._selv_log_container_change(
                self._attr_name, old_container_state, new_container_state
            )


class ObservableList(list):
    """List that notifies parent of changes."""

    def __init__(self, *args, parent=None, attr_name=None, **kwargs):
        self._parent = parent
        self._attr_name = attr_name
        self._initializing = True
        super().__init__()
        # Process initial items and wrap them
        if len(args) > 0:
            # Extract first argument safely
            first_arg = args[0]
            for value in first_arg:
                self.append(value)
        self._initializing = False

    def __setitem__(self, key, value):
        old_container_state = self.copy() if self._parent else None
        wrapped_value = self._wrap_value(value)
        super().__setitem__(key, wrapped_value)
        if self._parent and self._attr_name and not self._initializing:
            new_container_state = self.copy()
            self._parent._selv_log_container_change(
                self._attr_name, old_container_state, new_container_state
            )

    def _wrap_value(self, value):
        """Wrap container values for observation."""
        if isinstance(value, dict):
            return ObservableDict(value, parent=self._parent, attr_name=self._attr_name)
        elif isinstance(value, list):
            return ObservableList(value, parent=self._parent, attr_name=self._attr_name)
        elif isinstance(value, set):
            return ObservableSet(value, parent=self._parent, attr_name=self._attr_name)
        return value

    def __delitem__(self, key):
        old_container_state = self.copy() if self._parent else None
        super().__delitem__(key)
        if self._parent and self._attr_name and not self._initializing:
            new_container_state = self.copy()
            self._parent._selv_log_container_change(
                self._attr_name, old_container_state, new_container_state
            )

    def append(self, value):
        old_container_state = self.copy() if self._parent else None
        wrapped_value = self._wrap_value(value)
        super().append(wrapped_value)
        if self._parent and self._attr_name and not self._initializing:
            new_container_state = self.copy()
            self._parent._selv_log_container_change(
                self._attr_name, old_container_state, new_container_state
            )

    def pop(self, index: SupportsIndex = -1):
        old_container_state = self.copy() if self._parent else None
        result = super().pop(index)
        if self._parent and self._attr_name and not self._initializing:
            new_container_state = self.copy()
            self._parent._selv_log_container_change(
                self._attr_name, old_container_state, new_container_state
            )
        return result


class ObservableSet(set):
    """Set that notifies parent of changes."""

    def __init__(self, *args, parent=None, attr_name=None, **kwargs):
        self._parent = parent
        self._attr_name = attr_name
        self._initializing = True
        super().__init__()
        # Process initial items and wrap them
        if len(args) > 0:
            # Extract first argument safely
            first_arg = args[0]
            for value in first_arg:
                self.add(value)
        self._initializing = False

    def add(self, element):
        old_container_state = self.copy() if self._parent else None
        wrapped_element = self._wrap_value(element)
        super().add(wrapped_element)
        if self._parent and self._attr_name and not self._initializing:
            new_container_state = self.copy()
            self._parent._selv_log_container_change(
                self._attr_name, old_container_state, new_container_state
            )

    def _wrap_value(self, value):
        """Wrap container values for observation."""
        if isinstance(value, dict):
            return ObservableDict(value, parent=self._parent, attr_name=self._attr_name)
        elif isinstance(value, list):
            return ObservableList(value, parent=self._parent, attr_name=self._attr_name)
        elif isinstance(value, set):
            return ObservableSet(value, parent=self._parent, attr_name=self._attr_name)
        return value

    def remove(self, element):
        old_container_state = self.copy() if self._parent else None
        super().remove(element)
        if self._parent and self._attr_name and not self._initializing:
            new_container_state = self.copy()
            self._parent._selv_log_container_change(
                self._attr_name, old_container_state, new_container_state
            )

    def discard(self, element):
        old_container_state = self.copy() if self._parent else None
        super().discard(element)
        if self._parent and self._attr_name and not self._initializing:
            new_container_state = self.copy()
            self._parent._selv_log_container_change(
                self._attr_name, old_container_state, new_container_state
            )

    def pop(self):
        old_container_state = self.copy() if self._parent else None
        result = super().pop()
        if self._parent and self._attr_name and not self._initializing:
            new_container_state = self.copy()
            self._parent._selv_log_container_change(
                self._attr_name, old_container_state, new_container_state
            )
        return result

    def clear(self):
        old_container_state = self.copy() if self._parent else None
        super().clear()
        if self._parent and self._attr_name and not self._initializing:
            new_container_state = self.copy()
            self._parent._selv_log_container_change(
                self._attr_name, old_container_state, new_container_state
            )

    def update(self, *others):
        old_container_state = self.copy() if self._parent else None
        # Update with original values, wrapping happens in add() method
        super().update(*others)
        if self._parent and self._attr_name and not self._initializing:
            new_container_state = self.copy()
            self._parent._selv_log_container_change(
                self._attr_name, old_container_state, new_container_state
            )

    def intersection_update(self, *others):
        old_container_state = self.copy() if self._parent else None
        super().intersection_update(*others)
        if self._parent and self._attr_name and not self._initializing:
            new_container_state = self.copy()
            self._parent._selv_log_container_change(
                self._attr_name, old_container_state, new_container_state
            )

    def difference_update(self, *others):
        old_container_state = self.copy() if self._parent else None
        super().difference_update(*others)
        if self._parent and self._attr_name and not self._initializing:
            new_container_state = self.copy()
            self._parent._selv_log_container_change(
                self._attr_name, old_container_state, new_container_state
            )

    def symmetric_difference_update(self, other):
        old_container_state = self.copy() if self._parent else None
        super().symmetric_difference_update(other)
        if self._parent and self._attr_name and not self._initializing:
            new_container_state = self.copy()
            self._parent._selv_log_container_change(
                self._attr_name, old_container_state, new_container_state
            )


class _ChangeRecord:
    """Record of a single attribute change."""

    def __init__(
        self,
        timestamp: datetime,
        attribute: str,
        old_value: Any,
        new_value: Any,
        container_key: Optional[Union[str, int]] = None,
    ):
        self.timestamp = timestamp
        self.attribute = attribute
        self.old_value = old_value
        self.new_value = new_value
        self.container_key = container_key

    def __repr__(self) -> str:
        if self.container_key is not None:
            if isinstance(self.container_key, int):
                attr_str = f"{self.attribute}[{self.container_key}]"
            else:
                attr_str = f"{self.attribute}['{self.container_key}']"
        else:
            attr_str = self.attribute

        if self.old_value is None and self.new_value is not None:
            return f"{attr_str} = {self._format_value(self.new_value)}"
        elif self.new_value is None:
            return f"{attr_str}: {self._format_value(self.old_value)} -> deleted"
        else:
            old_val = self._format_value(self.old_value)
            new_val = self._format_value(self.new_value)
            return f"{attr_str}: {old_val} -> {new_val}"

    def _format_value(self, value: Any) -> str:
        """Format value for display."""
        if value is None:
            return "None"
        elif isinstance(value, str):
            return f"'{value}'"
        elif isinstance(value, (int, float, bool)):
            return str(value)
        elif isinstance(value, dict):
            return self._format_dict(value)
        elif isinstance(value, list):
            return self._format_list(value)
        elif isinstance(value, tuple):
            return self._format_tuple(value)
        elif isinstance(value, set):
            return self._format_set(value)
        else:
            return f"{type(value).__name__} instance"

    def _format_dict(self, value: dict) -> str:
        """Format dictionary value."""
        items = []
        for k, v in value.items():
            if isinstance(k, str):
                items.append(f"'{k}': {self._format_value(v)}")
            else:
                items.append(f"{k}: {self._format_value(v)}")
        return "{" + ", ".join(items) + "}"

    def _format_list(self, value: list) -> str:
        """Format list value."""
        items = [self._format_value(item) for item in value]
        return "[" + ", ".join(items) + "]"

    def _format_tuple(self, value: tuple) -> str:
        """Format tuple value."""
        items = [self._format_value(item) for item in value]
        return "(" + ", ".join(items) + ")"

    def _format_set(self, value: set) -> str:
        """Format set value."""
        try:
            # Try to sort for consistent output
            sorted_items = sorted(value)
        except TypeError:
            # If sorting fails (mixed types), use natural order
            sorted_items = list(value)
        items = [self._format_value(item) for item in sorted_items]
        return "{" + ", ".join(items) + "}"


class _SelvDecorator:
    """Internal class to handle selv decorator logic."""

    def __init__(
        self,
        track_private: bool = True,
        logger: Optional[Callable[[str], None]] = None,
    ):
        self.track_private = track_private
        self.logger = logger

    def wrap_container(self, self_obj: Any, name: str, value: Any) -> Any:
        """Wrap dict/list/set values."""
        if isinstance(value, dict):
            return ObservableDict(value, parent=self_obj, attr_name=name)
        elif isinstance(value, list):
            return ObservableList(value, parent=self_obj, attr_name=name)
        elif isinstance(value, set):
            return ObservableSet(value, parent=self_obj, attr_name=name)
        return value

    def log_change(
        self,
        self_obj: Any,
        cls_name: str,
        name: str,
        old_value: Any,
        new_value: Any,
        container_key: Optional[Union[str, int]] = None,
        is_initial: bool = False,
    ) -> None:
        """Log attribute change."""
        if not hasattr(self_obj, "_selv_change_history"):
            self_obj._selv_change_history = {}

        if name not in self_obj._selv_change_history:
            self_obj._selv_change_history[name] = []

        old_value_copy = copy.deepcopy(old_value) if old_value is not None else None
        new_value_copy = copy.deepcopy(new_value) if new_value is not None else None

        record = _ChangeRecord(
            timestamp=datetime.now(),
            attribute=name,
            old_value=old_value_copy,
            new_value=new_value_copy,
            container_key=container_key,
        )
        self_obj._selv_change_history[name].append(record)

        attr_str = self._get_attribute_string(name, container_key)
        log_func = self.logger if self.logger is not None else print

        if is_initial:
            formatted_val = record._format_value(new_value)
            log_func(f"[{cls_name}] {attr_str} = {formatted_val} (initialized)")
        elif new_value is None:
            formatted_old = record._format_value(old_value)
            log_func(f"[{cls_name}] {attr_str}: {formatted_old} -> deleted")
        else:
            formatted_old = record._format_value(old_value)
            formatted_new = record._format_value(new_value)
            log_func(f"[{cls_name}] {attr_str}: {formatted_old} -> {formatted_new}")

    def _get_attribute_string(
        self, name: str, container_key: Optional[Union[str, int]]
    ) -> str:
        """Get formatted attribute string."""
        if container_key is not None:
            if isinstance(container_key, int):
                return f"{name}[{container_key}]"
            else:
                return f"{name}['{container_key}']"
        return name

    def log_container_change(
        self,
        self_obj: Any,
        cls_name: str,
        attr_name: str,
        old_container_state: Any,
        new_container_state: Any,
    ) -> None:
        """Log container change."""
        old_copy = (
            copy.deepcopy(old_container_state)
            if old_container_state is not None
            else None
        )
        new_copy = (
            copy.deepcopy(new_container_state)
            if new_container_state is not None
            else None
        )
        self.log_change(self_obj, cls_name, attr_name, old_copy, new_copy)

    def create_setattr(
        self, cls: Type[T], original_setattr: Optional[Callable]
    ) -> Callable:
        """Create the __setattr__ method for the decorated class."""

        def new_setattr(self_obj: Any, name: str, value: Any) -> None:
            if name.startswith("_") and not self.track_private:
                if original_setattr:
                    original_setattr(self_obj, name, value)
                else:
                    object.__setattr__(self_obj, name, value)
                return

            if name.startswith("_selv_"):
                if original_setattr:
                    original_setattr(self_obj, name, value)
                else:
                    object.__setattr__(self_obj, name, value)
                return

            has_old_value = hasattr(self_obj, name)
            old_value = getattr(self_obj, name, None) if has_old_value else None

            wrapped_value = self.wrap_container(self_obj, name, value)

            if original_setattr:
                original_setattr(self_obj, name, wrapped_value)
            else:
                object.__setattr__(self_obj, name, wrapped_value)

            if not name.startswith("_selv_"):
                self.log_change(
                    self_obj,
                    cls.__name__,
                    name,
                    old_value,
                    wrapped_value,
                    is_initial=not has_old_value,
                )

        return new_setattr

    def create_view_changelog(self) -> Callable:
        """Create the view_changelog method for the decorated class."""

        def view_changelog(
            self_obj: Any,
            attribute: Optional[str] = None,
            format: Literal["flat", "attr"] = "flat",
        ) -> Union[Dict[str, List[Dict[str, Any]]], List[Dict[str, Any]]]:
            """View changelog for attributes."""
            if format not in ("flat", "attr"):
                raise ValueError(f"format must be 'flat' or 'attr', got {format!r}")

            if not hasattr(self_obj, "_selv_change_history"):
                return self._get_empty_history(attribute, format)

            if attribute is None:
                return self._get_all_history(self_obj, format)
            else:
                return self._get_attribute_history(self_obj, attribute)

        return view_changelog

    def _get_empty_history(
        self, attribute: Optional[str], format: Literal["flat", "attr"]
    ) -> Union[Dict[str, List[Dict[str, Any]]], List[Dict[str, Any]]]:
        """Return empty history when no change history exists."""
        if attribute is None:
            return [] if format == "flat" else {}
        return []

    def _get_all_history(
        self, self_obj: Any, format: Literal["flat", "attr"]
    ) -> Union[Dict[str, List[Dict[str, Any]]], List[Dict[str, Any]]]:
        """Get history for all attributes."""
        if format == "flat":
            return self._get_all_history_flat(self_obj)
        else:
            return self._get_all_history_attr(self_obj)

    def _get_all_history_flat(self, self_obj: Any) -> List[Dict[str, Any]]:
        """Get flat format history for all attributes."""
        result = []
        for attr_name, records in self_obj._selv_change_history.items():
            for record in records:
                result.append(self._format_record(record, attr_name))
        return result

    def _get_all_history_attr(self, self_obj: Any) -> Dict[str, List[Dict[str, Any]]]:
        """Get attribute format history for all attributes."""
        result = {}
        for attr_name, records in self_obj._selv_change_history.items():
            result[attr_name] = [self._format_record(record) for record in records]
        return result

    def _get_attribute_history(
        self, self_obj: Any, attribute: str
    ) -> List[Dict[str, Any]]:
        """Get history for a specific attribute."""
        records = self_obj._selv_change_history.get(attribute, [])
        return [self._format_record(record) for record in records]

    def _format_record(
        self, record: _ChangeRecord, attr_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Format a single change record."""
        formatted = {
            "time": record.timestamp,
            "from": record.old_value,
            "to": record.new_value,
        }
        if attr_name is not None:
            formatted["attr"] = attr_name
        return formatted


def _selv(
    track_private: bool = True, logger: Optional[Callable[[str], None]] = None
) -> Any:
    """Class decorator for logging attribute changes."""

    def decorator(cls: Type[T]) -> Any:
        decorator_instance = _SelvDecorator(track_private, logger)
        original_setattr = getattr(cls, "__setattr__", None)

        # Create bound methods for the class
        def wrap_container(self_obj: Any, name: str, value: Any) -> Any:
            return decorator_instance.wrap_container(self_obj, name, value)

        def log_change(
            self_obj: Any,
            name: str,
            old_value: Any,
            new_value: Any,
            container_key: Optional[Union[str, int]] = None,
            is_initial: bool = False,
        ) -> None:
            decorator_instance.log_change(
                self_obj,
                cls.__name__,
                name,
                old_value,
                new_value,
                container_key,
                is_initial,
            )

        def log_container_change(
            self_obj: Any,
            attr_name: str,
            old_container_state: Any,
            new_container_state: Any,
        ) -> None:
            decorator_instance.log_container_change(
                self_obj,
                cls.__name__,
                attr_name,
                old_container_state,
                new_container_state,
            )

        # Set methods on the class
        cls.__setattr__ = decorator_instance.create_setattr(cls, original_setattr)
        cls.view_changelog = decorator_instance.create_view_changelog()
        cls._selv_wrap_container = wrap_container
        cls._selv_log_change = log_change
        cls._selv_log_container_change = log_container_change

        return cls

    return decorator


def selv_decorator(*args: Any, **kwargs: Any) -> Any:
    """Decorator for @selv and @selv(...) syntax."""
    if args and not kwargs and callable(args[0]):
        return _selv()(args[0])

    return _selv(*args, **kwargs)


selv = selv_decorator
