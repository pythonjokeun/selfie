from selv import selv


@selv
class DataModel:
    def __init__(self):
        self.name = "Untitled"
        self.count = 0
        self.settings = {"theme": "light", "notifications": True}
        self.tasks = ["task1", "task2"]
        self.tags = {"python", "programming"}
        self.coordinates = (0, 0)


model = DataModel()

model.name = "My Data Model"
model.count = 5

model.settings["theme"] = "dark"
model.settings["language"] = "en"
del model.settings["notifications"]

model.tasks.append("task3")
model.tasks[0] = "updated_task1"
model.tasks.pop()

model.tags.add("decorator")
model.tags.remove("python")

model.coordinates = (10, 20)

print("All changes:")
for change in model.view_changelog():
    print(f"  {change['attr']}: {change['from']} -> {change['to']}")

print("\nSettings changes only:")
for change in model.view_changelog("settings"):
    print(f"  {change['from']} -> {change['to']}")
