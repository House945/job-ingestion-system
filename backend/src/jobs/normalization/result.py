from dataclasses import dataclass


@dataclass(frozen=True)
class Normalized[T]:
    """A normalized value together with anything that had to be guessed.

    Warnings are not errors. They record that a value was inferred rather than
    read, so that the distinction survives into storage and the UI.
    """

    value: T
    warnings: tuple[str, ...] = ()