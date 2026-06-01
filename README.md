# fdp-schema

Package-neutral pydantic schema for tokamak data locator catalogs.

The schema describes where a tokamak's data lives across backends (MDSplus
trees, PTData indexes, SQL databases). Other packages (e.g., `fdp`,
`toksearch_d3d`) consume the schema; tokamak packages contribute a YAML via
the `fdp_schema.catalogs` entry-point group.

See `docs/` and the design spec in
`toksearch_d3d/docs/superpowers/specs/2026-06-01-fdp-schema-design.md`.
