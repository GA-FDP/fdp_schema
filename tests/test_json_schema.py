# Copyright 2024 General Atomics
# Licensed under the Apache License, Version 2.0.

"""Tests for fdp_schema's JSON Schema export."""


class TestJsonSchema:
    def test_export_returns_dict(self):
        from fdp_schema import tokamak_json_schema
        schema = tokamak_json_schema()
        assert isinstance(schema, dict)

    def test_exports_top_level_tokamak_properties(self):
        from fdp_schema import tokamak_json_schema
        schema = tokamak_json_schema()
        props = schema["properties"]
        assert "name" in props
        assert "schema_version" in props
        assert "locators" in props
        assert "extra_env" in props

    def test_defs_include_all_locator_types(self):
        from fdp_schema import tokamak_json_schema
        schema = tokamak_json_schema()
        defs = schema.get("$defs", schema.get("definitions", {}))
        names = set(defs.keys())
        assert "MdsTreeLocator" in names
        assert "PtDataIndexedLocator" in names
        assert "SqlLocator" in names
        assert "AuthHint" in names
