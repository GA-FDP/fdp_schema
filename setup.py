# Copyright 2024 General Atomics
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Shim to wire versioneer's cmdclass into the build. Without this,
# `_version.py` ships as the live 683-line template that runs `git
# describe` at import time -- which falls back to whatever .git directory
# happens to be on the import path and reports the wrong version.
# Versioneer 0.29 still requires this even when most metadata lives in
# pyproject.toml (see the fdp/setup.py for the matching pattern).

from setuptools import setup, find_packages
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import versioneer


setup(
    name="fdp-schema",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(include=["fdp_schema", "fdp_schema.*"]),
    include_package_data=True,
    zip_safe=False,
)
