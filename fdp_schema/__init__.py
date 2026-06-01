# Copyright 2024 General Atomics
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""Package-neutral schema for tokamak data locator catalogs.

Defines pydantic models that describe how a tokamak's data lives across
backends (MDSplus trees, PTData indexes, SQL databases). Pure data: no
network, no XRootD, no GA-FDP dependencies beyond pydantic and pyyaml.

Consumers (fdp, MCP servers, future Julia tools) import the models and
load YAMLs that contributing packages ship via the `fdp_schema.catalogs`
entry-point group.
"""
from . import _version

__version__ = _version.get_versions()["version"]

from .models import (
    AuthHint,
    MdsTreeLocator,
    PtDataIndexedLocator,
    SqlLocator,
    Locator,
    Tokamak,
)
from .loader import load_tokamak

__all__ = [
    "__version__",
    "AuthHint",
    "MdsTreeLocator",
    "PtDataIndexedLocator",
    "SqlLocator",
    "Locator",
    "Tokamak",
    "load_tokamak",
]
