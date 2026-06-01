# Copyright 2024 General Atomics
# Licensed under the Apache License, Version 2.0.

"""YAML loading and validation for tokamak catalog files."""

from pathlib import Path
import yaml
from pydantic import ValidationError

from .models import Tokamak


def load_tokamak(source) -> Tokamak:
    """Load a Tokamak from a YAML file.

    `source` may be:
    - a stdlib `importlib.abc.Traversable` (anything with `.read_text()`)
    - a `pathlib.Path`
    - a `str` filesystem path

    Raises:
      pydantic.ValidationError: with the source path prepended to the
        error message, so failures point at the offending YAML.
    """
    label = str(source) if not hasattr(source, "read_text") else repr(source)
    if hasattr(source, "read_text"):
        text = source.read_text()
    else:
        text = Path(source).read_text()
    try:
        return Tokamak.model_validate(yaml.safe_load(text))
    except ValidationError as e:
        raise ValidationError.from_exception_data(
            f"Tokamak (from {label})", e.errors(),
        ) from None
