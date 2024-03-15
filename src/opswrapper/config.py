import keyword
import os
import warnings
from collections.abc import MutableMapping
from functools import cached_property
from pathlib import Path
from typing import ClassVar, Dict, Union

import tomli

_CONFIG_FILE_NAME = ".path_of.toml"


class PathOf(MutableMapping[str, Path]):
    """Paths to important files and directories.

    Paths are collected from the following sources, in order of increasing
    priority:

    - Default values
    - `.path_of.toml` files, starting from the root directory and down to
      the current directory
    - Environment variables starting with `OPENSEES_` (e.g., `OPENSEES_SCRATCH`)
    - Values set directly on the config object

    The following config options have defaults:

    - `'opensees'` -> `OpenSees` (i.e., look for it on the `PATH`)
    - `'scratch'` -> `$HOME/Scratch` (Linux) or `%USERPROFILE%\\Scratch` (Windows)

    These will be used if they are not defined in any configuration files.

    Configured paths may be accessed using either key (`path_of['opensees']`)
    or attribute (`path_of.opensees`) access.

    Overrides may be set using either key-value or attribute syntax::

        path_of['opensees'] = '/path/to/OpenSees'
        path_of.opensees = '/path/to/OpenSees'
    """

    _default: ClassVar[Dict[str, Path]] = {
        "opensees": Path("OpenSees"),
        "scratch": Path.home() / "Scratch",
    }
    _env_prefix = "OPENSEES_"

    def _load_config_files(self):
        config = {}

        cwd = Path.cwd()
        for directory in [*reversed(cwd.parents), cwd]:
            possible_config = directory / _CONFIG_FILE_NAME
            try:
                contents = possible_config.read_text(encoding="utf-8")
            except FileNotFoundError:
                continue
            except Exception as exc:
                warnings.warn(
                    f"error reading config file {str(possible_config)!r}: {exc}",
                    stacklevel=1,
                )
                continue

            try:
                config.update(
                    {key: Path(value) for key, value in tomli.loads(contents).items()}
                )
            except Exception as exc:
                warnings.warn(
                    f"error reading config file {str(possible_config)!r}: {exc}",
                    stacklevel=1,
                )
                continue

        return config

    def _load_env(self):
        return {
            key[len(self._env_prefix) :].lower(): Path(value)
            for key, value in os.environ.items()
            if key.startswith(self._env_prefix)
        }

    @cached_property
    def _config(self):
        config = self._default.copy()
        config.update(self._load_config_files())
        config.update(self._load_env())
        return config

    def __setitem__(self, key: str, value: Union[str, Path]):
        self._config[key] = Path(value)

    def __getitem__(self, key: str) -> Path:
        return self._config[key]

    def __getattr__(self, name: str) -> Path:
        try:
            return self._config[name]
        except KeyError:
            raise AttributeError(repr(name)) from None

    def __setattr__(self, name, value):
        self._config[name] = Path(value)

    def __iter__(self):
        return iter(self._config)

    def __len__(self):
        return len(self._config)

    def __delitem__(self, key: str):
        del self._config[key]

    def __dir__(self):
        return super().__dir__() + [
            key
            for key in self._config.keys()
            if isinstance(key, str)
            and key.isidentifier()
            and not keyword.iskeyword(key)
        ]


path_of = PathOf()
