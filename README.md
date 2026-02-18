# Selv

A Python decorator for logging attribute changes in class. Track every modification to your object's attributes with automatic logging and changelog.

## Motivation

Tracking attribute changes helps me understand how a complex class behaves and speeds up debugging when issues occur. Having said this, I need a simple way to log all attribute changes without writing boilerplate code for each attribute.

## Features

- **Automatic attribute change tracking**: Decorated class automatically log all attribute changes
- **Container support**: Tracks value modifications inside built-in containers (dict, list, set, tuple)
- **Flexible logging**: Use good ol `print` statement or any custom logger function
- **View changelog**: Query complete change history for any attribute
- **Exclude specific attributes**: Optionally exclude specific attributes from tracking

- **Custom actions**: Execute custom functions when specific attributes change

## Installation

```bash
pip install selv
```

Or using mighty `uv`:

```bash
uv add selv
```

## Usage

### Tracking changes

```python
from selv import selv

@selv
class Counter:
    def __init__(self):
        self.value = 0

    def increment(self):
        self.value += 1

    def decrement(self):
        self.value -= 1

# Create counter and use it
counter = Counter()
counter.increment()
counter.decrement()

# Changes are automatically logged:
# [Counter] value: 0 -> 1
# [Counter] value: 1 -> 0
```

### View changelog

```python
# View all changes
all_changes = counter.view_changelog()
print(all_changes)
# [
#   {'time': datetime, 'attr': 'value', 'from': None, 'to': 0},
#   {'time': datetime, 'attr': 'value', 'from': 0, 'to': 1},
#   {'time': datetime, 'attr': 'value', 'from': 1, 'to': 0}
# ]

# View changes for specific attribute
value_changes = counter.view_changelog("value")
print(value_changes)
# [
#   {'time': datetime, 'from': None, 'to': 0},
#   {'time': datetime, 'from': 0, 'to': 1},
#   {'time': datetime, 'from': 1, 'to': 0}
# ]

# View changes grouped by attribute
grouped = counter.view_changelog(format="attr")
print(grouped)
# {
#   'value': [
#     {'time': datetime, 'from': None, 'to': 0},
#     {'time': datetime, 'from': 0, 'to': 1},
#     {'time': datetime, 'from': 1, 'to': 0}
#   ]
# }
```

### Set custom action

```python
from selv import selv


def log_inventory_change(inventory):
    total = sum(inventory.values())
    print(f"Total items in inventory: {total}")

@selv(actions={"inventory": log_inventory_change})
class Store:
    def __init__(self):
        self.inventory = {"apples": 10, "bananas": 5}

store = Store()
store.inventory["oranges"] = 8
# [Store] inventory = {'apples': 10, 'bananas': 5} (initialized)
# Total items in inventory: 15
# [Store] inventory: {'apples': 10, 'bananas': 5} -> {'apples': 10, 'bananas': 5, 'oranges': 8}
# Total items in inventory: 23
```

### Parameters

The `@selv` decorator has a few parameters to customize its behavior.

1. **`track_private`** (`bool`, default: `True`)
   - When `True`: Tracks all attributes including those starting with `_` (private attributes)
   - When `False`: Only tracks public attributes (those not starting with `_`)

2. **`logger`** (`Callable[[str], None]`, default: `print`)
   - Function to use for logging change messages (e.g., `logging.info`, `logging.debug`)
   - Can be any function that accepts a string argument

3. **`exclude`** (`List[str]`, default: `None`)
   - List of attribute names to exclude from tracking
   - Useful for exclude sensitive data or unimportant attributes

4. **`actions`** (`Dict[str, Callable[[Any], None]]`, default: `None`)
   - Dictionary mapping attribute names to functions that are called when the attribute changes
   - Each function receives the new value of the attribute as its argument

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
