# Copyright 2024 General Atomics
# Licensed under the Apache License, Version 2.0.

"""Pydantic models for the fdp_schema catalog format."""

from typing import Literal
from pydantic import BaseModel


class AuthHint(BaseModel):
    """Tells consumers what credential to expect. Mechanism is out-of-band:
    the credential itself lives in an env var (`env=...`) or a file
    (`path=...`); this object never holds secrets."""

    kind: Literal["bearer_token", "password_file", "none"]
    env: str | None = None
    path: str | None = None
