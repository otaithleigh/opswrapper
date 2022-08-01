import warnings
from pathlib import Path
from typing import Union

import tomli

_CONFIG_FILE_NAME = '.path_of.toml'


class PathOf():
    """Paths to important files and directories.

    Works by looking for `.path_of.toml` files, starting from the current
    working directory and working back to the root, with the root having the
    lowest priority and the CWD the highest. Any time the CWD changes, the
    configuration is re-calculated.

    The following config options have defaults:

    - `'opensees'` -> `OpenSees` (i.e., look for it on the `PATH`)
    - `'scratch'` -> `$HOME/Scratch` (Linux) or `%USERPROFILE%\\Scratch` (Windows)

    These will be used if they are not defined in any configuration files.

    Configured paths may be accessed using either key (`path_of['opensees']`)
    or attribute (`path_of.opensees`) access.

    Temporary overrides may be set using key-value syntax
    (`path_of['opensees'] = '/path/to/OpenSees'`), but will be overridden if the
    CWD changes and the configuration recalculates.
    """
    _default = {
        'opensees': Path('OpenSees'),
        'scratch': Path.home()/'Scratch',
    }

    def __init__(self):
        self._cwd = Path.cwd()
        self._config: dict[str, Path] = {}
        self._build_config()

    def _build_config(self):
        """Starting from the CWD, walk up to root, accumulating .path_of.toml
        files, then apply them starting from root.
        """
        config_files = []
        if (p := self._cwd/_CONFIG_FILE_NAME).exists():
            config_files.append(p)

        for parent in self._cwd.parents:
            if (p := parent/_CONFIG_FILE_NAME).exists():
                config_files.append(p)

        for file in reversed(config_files):
            self._apply_config(file)

    def _apply_config(self, filename):
        try:
            with open(filename, 'rb') as f:
                config = tomli.load(f)
        except Exception as exc:
            warnings.warn(f'Could not load config file {filename} due to exception: {exc}')
            return

        config_bak = self._config.copy()
        pathed_config = zip(config.keys(), map(Path, config.values()))
        try:
            self._config.update(pathed_config)
        except Exception as exc:
            warnings.warn(f'Failed to apply config file {filename} due to exception: {exc}')
            self._config = config_bak

    def __setitem__(self, key: str, value: Union[str, Path]):
        self.set(key, value)

    def __getitem__(self, key: str) -> Path:
        return self.get(key)

    def __getattr__(self, name: str) -> Path:
        return self.get(name)

    def get(self, key: str) -> Path:
        """Retrieve a path from the configuration.

        Parameters
        ----------
        key : str
            Configured path to retrieve.

        Raises
        ------
        KeyError
            If `key` is not set in the configuration and is not present in
            `_default`.
        """
        if self._cwd != (cwd := Path.cwd()):
            self._cwd = cwd
            self._build_config()
        value = self._config.get(key)
        if value is None:
            try:
                return self._default[key]
            except KeyError as exc:
                raise KeyError(f'{key!r} is unset and no default is provided') from exc
        else:
            return value

    def set(self, key: str, value: Union[str, Path]):
        self._config[key] = Path(value)


path_of = PathOf()
