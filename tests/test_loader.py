# Copyright 2024 General Atomics
# Licensed under the Apache License, Version 2.0.

"""Tests for fdp_schema.loader — YAML parsing and round-trip."""

from pathlib import Path
import textwrap
import pytest


class TestLoadTokamak:
    def test_load_from_path(self, tmp_path):
        from fdp_schema import load_tokamak, Tokamak
        p = tmp_path / "x.yaml"
        p.write_text(textwrap.dedent("""
            schema_version: 1
            name: x
            description: test
            locators:
              - kind: mds_tree
                name: main
                transport: pelican
                search_path: ["u1", "u2"]
        """))
        t = load_tokamak(p)
        assert isinstance(t, Tokamak)
        assert t.name == "x"
        assert len(t.locators) == 1
        assert t.locators[0].search_path == ["u1", "u2"]

    def test_load_from_str_path(self, tmp_path):
        from fdp_schema import load_tokamak
        p = tmp_path / "x.yaml"
        p.write_text("schema_version: 1\nname: x\n")
        t = load_tokamak(str(p))
        assert t.name == "x"

    def test_load_from_traversable(self, tmp_path):
        from fdp_schema import load_tokamak
        # Traversable is duck-typed: needs .read_text(). Use a Path (which qualifies).
        p = tmp_path / "x.yaml"
        p.write_text("schema_version: 1\nname: x\n")

        class FakeTraversable:
            def read_text(self):
                return p.read_text()

        t = load_tokamak(FakeTraversable())
        assert t.name == "x"

    def test_invalid_yaml_raises(self, tmp_path):
        from fdp_schema import load_tokamak
        p = tmp_path / "x.yaml"
        p.write_text("name: x\nlocators:\n  - kind: kafka\n")
        with pytest.raises(Exception):  # pydantic ValidationError
            load_tokamak(p)

    def test_round_trip(self, tmp_path):
        """model_dump() → yaml → load_tokamak() is identity."""
        import yaml
        from fdp_schema import (
            load_tokamak, Tokamak, MdsTreeLocator, AuthHint,
        )
        original = Tokamak(
            name="d3d",
            description="DIII-D",
            locators=[
                MdsTreeLocator(
                    name="main", transport="pelican",
                    search_path=["u1", "u2"],
                    auth=AuthHint(kind="bearer_token", env="BEARER_TOKEN"),
                ),
            ],
            extra_env={"K": "V"},
        )
        p = tmp_path / "x.yaml"
        p.write_text(yaml.safe_dump(original.model_dump()))
        loaded = load_tokamak(p)
        assert loaded == original

    def test_invalid_yaml_error_mentions_source(self, tmp_path):
        from fdp_schema import load_tokamak
        from pydantic import ValidationError
        p = tmp_path / "bad.yaml"
        p.write_text("name: x\nlocators:\n  - kind: kafka\n")
        with pytest.raises(ValidationError) as exc:
            load_tokamak(p)
        # The error message should make it possible to identify the source file.
        assert "bad.yaml" in str(exc.value) or "bad.yaml" in repr(exc.value)


class TestD3DFixture:
    def test_d3d_fixture_loads(self):
        from pathlib import Path
        from fdp_schema import load_tokamak
        fixture = Path(__file__).parent / "fixtures" / "d3d.yaml"
        t = load_tokamak(fixture)
        assert t.name == "d3d"
        assert len(t.locators) == 3
        kinds = {l.kind for l in t.locators}
        assert kinds == {"mds_tree", "ptdata_indexed", "sql"}
        assert t.extra_env["D3DATA"] == "yes"
        assert t.extra_env["SYS_D3_DELIM"] == ";"
