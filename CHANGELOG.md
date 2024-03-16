Changelog
=========

[6.0.0] - 2024-03-15
--------------------

### Added

- `tclescape()` function to escape Tcl meta-characters.
- `tcllist()` has a new argument `stringify`, which specifies the function used
  to convert objects to `str` before being escaped.
- `config.path_of` now supports reading configuration from environment variables
  prefixed with `OPENSEES_`.

### Changed

- Minimum Python has been updated to 3.9.
- `ScratchFile()` now creates a temporary directory, which by default is
  automatically cleaned up upon finalization.
- `tcllist()` uses `tclescape()` to escape arguments instead of enclosing in
  curly brackets.
- `path_for_tcl()` uses `pathlib.Path.as_posix()` instead of blindly replacing
  backslashes, which is technically incorrect on POSIX platforms.
- Configuration (`config.path_of`) no longer updates when the working directory
  changes. The configuration is loaded the first time any of the keys are
  accessed.

### Removed

- `analysis.scratch_file_factory()` has been removed. Use `ScratchFile` instead.
- The `analysis_id` argument to `ScratchFile` has been removed, as the temporary
  directory mechanism makes it completely redundant.


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
