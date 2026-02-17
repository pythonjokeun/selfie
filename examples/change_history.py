from selv import selv


@selv
class Document:
    def __init__(self, title):
        self.title = title
        self.content = ""
        self.version = 1


doc = Document("Untitled")
doc.content = "Hello world"
doc.version = 2
doc.title = "My Document"

print("All changes (flat format):")
for change in doc.view_changelog():
    print(f"  {change['attr']}: {change['from']} -> {change['to']}")

print("\nGrouped by attribute:")
grouped = doc.view_changelog(format="attr")
for attr, changes in grouped.items():
    print(f"  {attr}: {len(changes)} changes")

print("\nTitle changes only:")
for change in doc.view_changelog("title"):
    print(f"  {change['from']} -> {change['to']}")
