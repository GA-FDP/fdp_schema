# Copyright 2024 General Atomics
# Licensed under the Apache License, Version 2.0.

"""Pydantic models for the fdp_schema catalog format."""

from typing import Annotated, Literal, Union
from pydantic import BaseModel, Field


class AuthHint(BaseModel):
    """Tells consumers what credential to expect. Mechanism is out-of-band:
    the credential itself lives in an env var (`env=...`) or a file
    (`path=...`); this object never holds secrets."""

    kind: Literal["bearer_token", "password_file", "none"]
    env: str | None = None
    path: str | None = None


class MdsTreeLocator(BaseModel):
    """A search path of base URLs (with MDSplus tree-path tokens like ~t)
    consulted in order when opening an MDSplus tree."""

    kind: Literal["mds_tree"] = "mds_tree"
    name: str
    transport: Literal["pelican", "xrootd", "local"]
    search_path: list[str]
    auth: AuthHint | None = None


class PtDataIndexedLocator(BaseModel):
    """A PTData (shot, pointname) → shotfile resolution via a JSON index."""

    kind: Literal["ptdata_indexed"] = "ptdata_indexed"
    name: str
    transport: Literal["pelican", "xrootd", "local"]
    index_dir: str
    auth: AuthHint | None = None


class SqlLocator(BaseModel):
    """A SQL database holding shot metadata. v1 implements mssql only."""

    kind: Literal["sql"] = "sql"
    name: str
    driver: Literal["mssql", "postgres", "sqlite"]
    host: str
    port: int | None = None
    database: str
    tdsver: str | None = None
    auth: AuthHint | None = None


Locator = Annotated[
    Union[MdsTreeLocator, PtDataIndexedLocator, SqlLocator],
    Field(discriminator="kind"),
]
