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
