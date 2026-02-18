"""Test exclude feature of selv decorator."""

from selv import selv


def test_exclude_feature():
    """Test that excluded attributes are not tracked."""

    @selv(exclude=["password"])
    class User:
        def __init__(self):
            self.username = "alice"
            self.password = "secret123"

    user = User()
    user.password = "newsecret456"
    changelog = user.view_changelog(format="attr")

    assert "password" not in changelog
    assert "username" in changelog
