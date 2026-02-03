class MissingRequiredField(Exception):
    def __init__(self, *, field: str) -> None:
        self.field = field
        super().__init__(f"Missing required field: {field}")
