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
