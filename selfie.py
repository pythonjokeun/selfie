"""Python decorator for logging attribute changes."""

__all__ = ["selfie"]

import copy
from datetime import datetime
from typing import (
    Any,
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
        self._parent = None
        self._attr_name = None
        super().__init__(*args, **kwargs)
        self._parent = parent
        self._attr_name = attr_name

    def __setitem__(self, key, value):
        old_container_state = self.copy() if self._parent else None
        super().__setitem__(key, value)
        if self._parent and self._attr_name:
            new_container_state = self.copy()
            self._parent._selfie_log_container_change(
                self._attr_name, old_container_state, new_container_state
            )

    def __delitem__(self, key):
        old_container_state = self.copy() if self._parent else None
        super().__delitem__(key)
        if self._parent and self._attr_name:
            new_container_state = self.copy()
            self._parent._selfie_log_container_change(
                self._attr_name, old_container_state, new_container_state
            )


class ObservableList(list):
    """List that notifies parent of changes."""

    def __init__(self, *args, parent=None, attr_name=None, **kwargs):
        self._parent = None
        self._attr_name = None
        super().__init__(*args, **kwargs)
        self._parent = parent
        self._attr_name = attr_name

    def __setitem__(self, key, value):
        old_container_state = self.copy() if self._parent else None
        super().__setitem__(key, value)
        if self._parent and self._attr_name:
            new_container_state = self.copy()
            self._parent._selfie_log_container_change(
                self._attr_name, old_container_state, new_container_state
            )

    def __delitem__(self, key):
        old_container_state = self.copy() if self._parent else None
        super().__delitem__(key)
        if self._parent and self._attr_name:
            new_container_state = self.copy()
            self._parent._selfie_log_container_change(
                self._attr_name, old_container_state, new_container_state
            )

    def append(self, value):
        old_container_state = self.copy() if self._parent else None
        super().append(value)
        if self._parent and self._attr_name:
            new_container_state = self.copy()
            self._parent._selfie_log_container_change(
                self._attr_name, old_container_state, new_container_state
            )

    def pop(self, index: SupportsIndex = -1):
        old_container_state = self.copy() if self._parent else None
        result = super().pop(index)
        if self._parent and self._attr_name:
            new_container_state = self.copy()
            self._parent._selfie_log_container_change(
                self._attr_name, old_container_state, new_container_state
            )
        return result


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
        time_str = self.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        if self.container_key is not None:
            if isinstance(self.container_key, int):
                attr_str = f"{self.attribute}[{self.container_key}]"
            else:
                attr_str = f"{self.attribute}['{self.container_key}']"
        else:
            attr_str = self.attribute

        if self.old_value is None and self.new_value is not None:
            return f"[{time_str}] {attr_str} = {self._format_value(self.new_value)}"
        elif self.new_value is None:
            return f"[{time_str}] {attr_str}: {self._format_value(self.old_value)} -> deleted"
        else:
            return f"[{time_str}] {attr_str}: {self._format_value(self.old_value)} -> {self._format_value(self.new_value)}"

    def _format_value(self, value: Any) -> str:
        """Format value for display."""
        if value is None:
            return "None"
        elif isinstance(value, str):
            return f"'{value}'"
        elif isinstance(value, (int, float, bool)):
            return str(value)
        elif isinstance(value, dict):
            items = []
            for k, v in value.items():
                if isinstance(k, str):
                    items.append(f"'{k}': {self._format_value(v)}")
                else:
                    items.append(f"{k}: {self._format_value(v)}")
            return "{" + ", ".join(items) + "}"
        elif isinstance(value, list):
            items = [self._format_value(item) for item in value]
            return "[" + ", ".join(items) + "]"
        elif isinstance(value, tuple):
            items = [self._format_value(item) for item in value]
            return "(" + ", ".join(items) + ")"
        elif isinstance(value, set):
            items = [self._format_value(item) for item in sorted(value)]
            return "{" + ", ".join(items) + "}"
        else:
            return f"{type(value).__name__} instance"


def _selfie(track_private: bool = True) -> Any:
    """Class decorator for logging attribute changes."""

    def decorator(cls: Type[T]) -> Any:
        original_setattr = getattr(cls, "__setattr__", None)

        def _selfie_wrap_container(self, name: str, value: Any) -> Any:
            """Wrap dict/list values."""
            if isinstance(value, dict):
                return ObservableDict(value, parent=self, attr_name=name)
            elif isinstance(value, list):
                return ObservableList(value, parent=self, attr_name=name)
            return value

        def _selfie_log_change(
            self,
            name: str,
            old_value: Any,
            new_value: Any,
            container_key: Optional[Union[str, int]] = None,
            is_initial: bool = False,
        ) -> None:
            """Log attribute change."""
            if not hasattr(self, "_selfie_change_history"):
                self._selfie_change_history = {}

            if name not in self._selfie_change_history:
                self._selfie_change_history[name] = []

            old_value_copy = copy.deepcopy(old_value) if old_value is not None else None
            new_value_copy = copy.deepcopy(new_value) if new_value is not None else None

            record = _ChangeRecord(
                timestamp=datetime.now(),
                attribute=name,
                old_value=old_value_copy,
                new_value=new_value_copy,
                container_key=container_key,
            )
            self._selfie_change_history[name].append(record)

            time_str = record.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            if container_key is not None:
                if isinstance(container_key, int):
                    attr_str = f"{name}[{container_key}]"
                else:
                    attr_str = f"{name}['{container_key}']"
            else:
                attr_str = name

            if is_initial:
                print(
                    f"[{time_str}] [{cls.__name__}] {attr_str} = {record._format_value(new_value)} (initialized)"
                )
            elif new_value is None:
                print(
                    f"[{time_str}] [{cls.__name__}] {attr_str}: {record._format_value(old_value)} -> deleted"
                )
            else:
                print(
                    f"[{time_str}] [{cls.__name__}] {attr_str}: {record._format_value(old_value)} -> {record._format_value(new_value)}"
                )

        def _selfie_log_container_change(
            self,
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
            self._selfie_log_change(attr_name, old_copy, new_copy, container_key=None)

        def new_setattr(self, name: str, value: Any) -> None:
            if name.startswith("_") and not track_private:
                if original_setattr:
                    original_setattr(self, name, value)
                else:
                    object.__setattr__(self, name, value)
                return

            if name.startswith("_selfie_"):
                if original_setattr:
                    original_setattr(self, name, value)
                else:
                    object.__setattr__(self, name, value)
                return

            has_old_value = hasattr(self, name)
            old_value = getattr(self, name, None) if has_old_value else None

            wrapped_value = self._selfie_wrap_container(name, value)

            if original_setattr:
                original_setattr(self, name, wrapped_value)
            else:
                object.__setattr__(self, name, wrapped_value)

            if not name.startswith("_selfie_"):
                self._selfie_log_change(
                    name, old_value, wrapped_value, is_initial=not has_old_value
                )

        def get_change_history(
            self,
            attribute: Optional[str] = None,
            format: Literal["flat", "attr"] = "flat",
        ) -> Union[Dict[str, List[Dict[str, Any]]], List[Dict[str, Any]]]:
            """Get change history for attributes."""
            if format not in ("flat", "attr"):
                raise ValueError(f"format must be 'flat' or 'attr', got {format!r}")

            if not hasattr(self, "_selfie_change_history"):
                if attribute is None:
                    return [] if format == "flat" else {}
                return []

            if attribute is None:
                if format == "flat":
                    result = []
                    for attr_name, records in self._selfie_change_history.items():
                        for record in records:
                            result.append(
                                {
                                    "time": record.timestamp,
                                    "attr": attr_name,
                                    "from": record.old_value,
                                    "to": record.new_value,
                                }
                            )
                    return result
                else:  # format == "attr"
                    result = {}
                    for attr_name, records in self._selfie_change_history.items():
                        result[attr_name] = [
                            {
                                "time": record.timestamp,
                                "from": record.old_value,
                                "to": record.new_value,
                            }
                            for record in records
                        ]
                    return result
            else:
                records = self._selfie_change_history.get(attribute, [])
                return [
                    {
                        "time": record.timestamp,
                        "from": record.old_value,
                        "to": record.new_value,
                    }
                    for record in records
                ]

        cls.__setattr__ = new_setattr
        cls.get_change_history = get_change_history
        cls._selfie_wrap_container = _selfie_wrap_container
        cls._selfie_log_change = _selfie_log_change
        cls._selfie_log_container_change = _selfie_log_container_change

        return cls

    return decorator


def selfie_decorator(*args: Any, **kwargs: Any) -> Any:
    """Decorator for @selfie and @selfie(...) syntax."""
    if args and not kwargs and callable(args[0]):
        return _selfie()(args[0])

    return _selfie(*args, **kwargs)


selfie = selfie_decorator
