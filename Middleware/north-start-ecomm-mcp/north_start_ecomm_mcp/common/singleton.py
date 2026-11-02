from __future__ import annotations


class Singleton(type):
    """One instance per class for facades, DAOs, and the database gateway."""

    _instances: dict[type, object] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

    def clear(cls) -> None:
        Singleton._instances.pop(cls, None)
