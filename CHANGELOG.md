Changelog
=========

[5.2.0] - 2023-05-08
--------------------

### Added

- Added plastic hinge methods to the integration module.

### Changed

- Increased default float precision from 6 to 12 significant figures.

### Fixed

- Typing on `Node` now correctly identifies the stored type of `coords` and
  `mass` as `ndarray` and `Optional[ndarray]`, respectively.


[5.1.0] - 2022-10-13
--------------------

### Added

- Recorders now support the `region` argument.
- `CHANGELOG.md`

### Fixed

- TOML files are read as binary, to support `tomli` 2.0 (and silence deprecation
  warning on `tomli` 1.2)
- `utils.coerce_numeric` doesn't use bare except anymore.


[5.0.0] - 2022-05-16
--------------------

### Added

- Recorders can now receive `Path` objects as the `file` argument.
- Elements now inherit from a shared `Element` class instead of directly from
  `OpenSeesObject`.
- Uniaxial materials now inherit from a shared `UniaxialMaterial` class instead
  of directly from `OpenSeesObject`.
- Sections now inherit from a shared `Section` class instead of directly from
  `OpenSeesObject`.

### Changed

- `config.PathOf` has been reworked. Instead of a single `.path_of.toml` file in
  the home directory, the config object works by looking for `.path_of.toml`
  files, starting from the current working directory and working back to the
  root, with the root having the lowest priority and the CWD the highest. Any
  time the CWD changes, the configuration is re-calculated.
- Replace `toml` with `tomli` as the TOML parser.
- Fiber section definition objects are no longer namespaced within
  `section.Fiber`, and don't take a reference back to the `Fiber` section.

### Removed

- The `format_objects` method of `OpenSeesObject`s no longer takes a `join`
  parameter. It will now always return a `list[str]`.
