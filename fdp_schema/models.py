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
    # Optional glob (e.g. "json_indexes_*"). When set, index_dir is treated
    # as a PARENT and the latest matching subdir is selected at read time by
    # the consumers (ptdata JsonIndexPlugin / PtDataResolver). When None,
    # index_dir is used verbatim (a pinned, exact directory).
    index_pattern: str | None = None
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


class ZarrStoreLocator(BaseModel):
    """A Zarr object store with one store per shot, addressed by a base
    URL plus a per-shot filename template. `protocol` selects the fsspec
    backend; `endpoint` supplies the object-store host for non-AWS S3
    (e.g. STFC Echo)."""

    kind: Literal["zarr_store"] = "zarr_store"
    name: str
    protocol: Literal["https", "s3", "file"]
    base_url: str
    file_name_format: str = "{shot}.zarr"
    endpoint: str | None = None
    auth: AuthHint | None = None


class HttpCatalogLocator(BaseModel):
    """An HTTP metadata catalog exposing shot/signal tables (e.g. parquet
    endpoints). Paths are templated relative to `base_url`."""

    kind: Literal["http_catalog"] = "http_catalog"
    name: str
    base_url: str
    shots_path: str
    signals_path: str | None = None
    auth: AuthHint | None = None


Locator = Annotated[
    Union[
        MdsTreeLocator,
        PtDataIndexedLocator,
        SqlLocator,
        ZarrStoreLocator,
        HttpCatalogLocator,
    ],
    Field(discriminator="kind"),
]


class Tokamak(BaseModel):
    """One tokamak's data-locator catalog. Schema-versioned for forward
    compatibility — v2 (when it exists) will live as a separate class and
    the loader will dispatch on the declared version."""

    schema_version: Literal[1] = 1
    name: str
    description: str = ""
    pelican_root: str | None = None
    origin_server: str | None = None
    locators: list[Locator] = []
    extra_env: dict[str, str] = {}
    default_llm_preset: str | None = None
