# Copyright 2024 General Atomics
# Licensed under the Apache License, Version 2.0.

"""Tests for fdp_schema.models — pure pydantic validation, no I/O."""

import pytest
from pydantic import ValidationError


class TestAuthHint:
    def test_bearer_token_with_env(self):
        from fdp_schema.models import AuthHint
        a = AuthHint(kind="bearer_token", env="BEARER_TOKEN")
        assert a.kind == "bearer_token"
        assert a.env == "BEARER_TOKEN"
        assert a.path is None

    def test_password_file_with_path(self):
        from fdp_schema.models import AuthHint
        a = AuthHint(kind="password_file", path="~/.fdp/token")
        assert a.kind == "password_file"
        assert a.path == "~/.fdp/token"

    def test_kind_none(self):
        from fdp_schema.models import AuthHint
        a = AuthHint(kind="none")
        assert a.kind == "none"

    def test_unknown_kind_rejected(self):
        from fdp_schema.models import AuthHint
        with pytest.raises(ValidationError):
            AuthHint(kind="oauth2")


class TestMdsTreeLocator:
    def test_minimal(self):
        from fdp_schema.models import MdsTreeLocator
        m = MdsTreeLocator(
            name="main",
            transport="pelican",
            search_path=["pelican://host/tree1", "pelican://host/tree2"],
        )
        assert m.kind == "mds_tree"
        assert m.search_path == ["pelican://host/tree1", "pelican://host/tree2"]
        assert m.auth is None

    def test_with_auth(self):
        from fdp_schema.models import MdsTreeLocator, AuthHint
        m = MdsTreeLocator(
            name="main",
            transport="pelican",
            search_path=["pelican://host/tree"],
            auth=AuthHint(kind="bearer_token", env="BEARER_TOKEN"),
        )
        assert m.auth.kind == "bearer_token"

    def test_kind_immutable_via_init(self):
        # Pydantic accepts the literal default; explicit kind=mds_tree also ok.
        from fdp_schema.models import MdsTreeLocator
        m = MdsTreeLocator(
            kind="mds_tree", name="main", transport="pelican", search_path=[]
        )
        assert m.kind == "mds_tree"

    def test_unknown_transport_rejected(self):
        from fdp_schema.models import MdsTreeLocator
        with pytest.raises(ValidationError):
            MdsTreeLocator(name="main", transport="smb", search_path=[])


class TestPtDataIndexedLocator:
    def test_minimal(self):
        from fdp_schema.models import PtDataIndexedLocator
        p = PtDataIndexedLocator(
            name="main",
            transport="pelican",
            index_dir="pelican://host/index",
        )
        assert p.kind == "ptdata_indexed"
        assert p.index_dir == "pelican://host/index"


class TestSqlLocator:
    def test_mssql_full(self):
        from fdp_schema.models import SqlLocator
        s = SqlLocator(
            name="d3drdb",
            driver="mssql",
            host="d3drdb.gat.com",
            port=8001,
            database="d3drdb",
            tdsver="7.0",
        )
        assert s.kind == "sql"
        assert s.host == "d3drdb.gat.com"
        assert s.port == 8001
        assert s.tdsver == "7.0"

    def test_unknown_driver_rejected(self):
        from fdp_schema.models import SqlLocator
        with pytest.raises(ValidationError):
            SqlLocator(name="x", driver="oracle", host="h", database="d")


class TestLocatorDispatch:
    """The Locator union must dispatch on `kind` to the right subtype."""

    def test_dispatch_mds_tree(self):
        from pydantic import TypeAdapter
        from fdp_schema.models import Locator, MdsTreeLocator
        adapter = TypeAdapter(Locator)
        loc = adapter.validate_python(
            {"kind": "mds_tree", "name": "main", "transport": "pelican",
             "search_path": ["url1"]}
        )
        assert isinstance(loc, MdsTreeLocator)

    def test_dispatch_ptdata(self):
        from pydantic import TypeAdapter
        from fdp_schema.models import Locator, PtDataIndexedLocator
        adapter = TypeAdapter(Locator)
        loc = adapter.validate_python(
            {"kind": "ptdata_indexed", "name": "main",
             "transport": "pelican", "index_dir": "u"}
        )
        assert isinstance(loc, PtDataIndexedLocator)

    def test_dispatch_sql(self):
        from pydantic import TypeAdapter
        from fdp_schema.models import Locator, SqlLocator
        adapter = TypeAdapter(Locator)
        loc = adapter.validate_python(
            {"kind": "sql", "name": "d", "driver": "mssql",
             "host": "h", "database": "d"}
        )
        assert isinstance(loc, SqlLocator)

    def test_unknown_kind_rejected(self):
        from pydantic import TypeAdapter, ValidationError
        from fdp_schema.models import Locator
        adapter = TypeAdapter(Locator)
        with pytest.raises(ValidationError):
            adapter.validate_python({"kind": "kafka", "name": "x"})


class TestTokamak:
    def test_minimal(self):
        from fdp_schema.models import Tokamak
        t = Tokamak(name="x")
        assert t.schema_version == 1
        assert t.name == "x"
        assert t.description == ""
        assert t.locators == []
        assert t.extra_env == {}

    def test_full(self):
        from fdp_schema.models import (
            Tokamak, MdsTreeLocator, PtDataIndexedLocator
        )
        t = Tokamak(
            name="d3d",
            description="DIII-D",
            pelican_root="pelican://host/d3d",
            origin_server="root://host:8443",
            locators=[
                MdsTreeLocator(name="main", transport="pelican",
                               search_path=["u"]),
                PtDataIndexedLocator(name="main", transport="pelican",
                                     index_dir="u"),
            ],
            extra_env={"D3DATA": "yes"},
        )
        assert t.name == "d3d"
        assert len(t.locators) == 2
        assert t.locators[0].kind == "mds_tree"
        assert t.locators[1].kind == "ptdata_indexed"
        assert t.extra_env == {"D3DATA": "yes"}

    def test_locator_dispatch_from_dict(self):
        from fdp_schema.models import Tokamak, MdsTreeLocator
        t = Tokamak.model_validate({
            "name": "x",
            "locators": [
                {"kind": "mds_tree", "name": "main", "transport": "pelican",
                 "search_path": ["u"]},
            ],
        })
        assert isinstance(t.locators[0], MdsTreeLocator)

    def test_schema_version_must_be_1(self):
        from fdp_schema.models import Tokamak
        with pytest.raises(ValidationError):
            Tokamak(schema_version=2, name="x")

    def test_extra_env_rejects_non_string_values(self):
        from fdp_schema.models import Tokamak
        with pytest.raises(ValidationError):
            Tokamak(name="x", extra_env={"K": 42})

    def test_default_llm_preset_field(self):
        from fdp_schema.models import Tokamak
        # Default is None.
        t = Tokamak(name="x")
        assert t.default_llm_preset is None
        # Accepts a string.
        t = Tokamak(name="x", default_llm_preset="amsc")
        assert t.default_llm_preset == "amsc"
        # YAML-style round-trip.
        t2 = Tokamak.model_validate(
            {"name": "x", "default_llm_preset": "amsc"}
        )
        assert t2.default_llm_preset == "amsc"
