class UserAlreadyExists(Exception):
    def __init__(self, *, email: str) -> None:
        super().__init__(f"User with the email '{email}' already exists")
