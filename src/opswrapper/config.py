import dataclasses
import pathlib

import toml

from . import utils

_ROOT = pathlib.Path(__file__).parent
_path_of_file = pathlib.Path.home()/'.path_of.toml'


@dataclasses.dataclass(repr=False)
class _PathOf():
    """Paths to important files and directories.

    Parameters
    ----------
    opensees
        Path to the OpenSees binary.
    scratch
        Path of the scratch directory.
    datadir
        Path of the data directory (for e.g. ground motions)
    """
    opensees: pathlib.Path = pathlib.Path('OpenSees')
    scratch: pathlib.Path = pathlib.Path.home()/'Scratch'
    datadir: pathlib.Path = (_ROOT/"../../data").resolve()

    def __repr__(self):
        return utils.list_dataclass_fields('path_of', self)

    def __setattr__(self, name, value):
        if name in (field.name for field in dataclasses.fields(self)):
            value = pathlib.Path(value)
        return super().__setattr__(name, value)

    def load_config(self, file):
        """Load paths from a TOML configuration file.

        Overwrites existing object with settings from the given file, if the key
        exists in the file. Example configuration file::

            opensees = "/home/ptalley2/.local/bin/OpenSees"
            scratch = "/home/ptalley2/Scratch"

        Parameters
        ----------
        file : path-like
            Path to the configuration file.
        """
        file_paths = toml.load(file)
        self.opensees = file_paths.get('opensees', self.opensees)
        self.scratch = file_paths.get('scratch', self.scratch)
        self.datadir = file_paths.get('datadir', self.datadir)

    @classmethod
    def from_config(cls, file):
        return cls().load_config(file)


path_of = _PathOf()
if _path_of_file.exists():
    path_of.load_config(_path_of_file)
