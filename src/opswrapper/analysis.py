"""Helpers for running OpenSees."""

import shutil
import subprocess as sub
from functools import partial
from pathlib import Path
from typing import NamedTuple, Optional, Union

from . import config
from .backports import TemporaryDirectory


def _get_default_scratch_path():
    return config.path_of.scratch


class ScratchFile:
    """Create a scratch file path generator.

    Generates paths to scratch files inside a temporary directory.

    Parameters
    ----------
    name : str
        Name prefixed onto the temporary directory. Commonly the type of the
        analysis, e.g. ``'SectionAnalysis'``.
    scratch_path : path_like, optional
        Path to the scratch directory. If None, uses `config.path_of.scratch`.
        (default: None)
    delete : bool, optional
        If True, automatically remove the temporary directory. This removal
        is triggered on object finalization. If False, be sure to remove the
        temporary directory by calling `cleanup()`.

    Returns
    -------
    scratch_file : (name: str, suffix: str = '') -> Path
        A callable object that takes two arguments, 'name' and 'suffix',
        returning a Path object.

    Example
    -------
    >>> scratch_file = ScratchFile('TestoPresto')
    >>> scratch_file('disp', '.dat')
    PosixPath('/tmp/TestoPresto-5psb4f7s/disp.dat')
    """

    def __init__(
        self,
        name: str,
        scratch_path: Optional[Path] = None,
        delete: bool = True,
    ):
        if scratch_path is None:
            scratch_path = _get_default_scratch_path()

        prefix = str(name) + "-"

        # TODO: Replace backported TemporaryDirectory with stdlib
        # once Python 3.12 becomes minimum supported version.
        self._tempdir = TemporaryDirectory(
            prefix=prefix,
            dir=scratch_path,
            ignore_cleanup_errors=True,
            delete=delete,
        )
        self.tempdir = self._tempdir.name

    def __repr__(self) -> str:
        return f"<ScratchFile {self.tempdir!r}>"

    def __call__(self, name: str, suffix: str = "") -> Path:
        """
        Parameters
        ----------
        name : str
            Name of the scratch file, e.g. 'displacement'.
        suffix : str, optional
            Suffix to use for the scratch file. (default: '')

        Returns
        -------
        path : Path
            Path to the scratch file.
        """
        return Path(self.tempdir, name + suffix)

    def cleanup(self):
        self._tempdir.cleanup()


class AnalysisResults(NamedTuple):
    """Results from an OpenSees analysis.

    Parameters
    ----------
    returncode : int
        The return code from OpenSees.
    stdout : str
        Captured console output from OpenSees.
    """

    returncode: int
    stdout: str


class OpenSeesAnalysis:
    """Wrapper for an OpenSees analysis.

    Parameters
    ----------
    name : str, optional
        Descriptive name for the analysis object. Defaults to the class name.
    echo_output : bool, optional
        If True, echo OpenSees output to stdout. (default: False)
    delete_files : bool, optional
        If True, automatically delete temporary files. (default: True)
    opensees_path : Path, optional
        Path to the OpenSees binary to use. If None, uses the value from the
        global configuration. (default: None)
    scratch_path : Path, optional
        Path to the directory for storing temporary files. If None, uses the
        value from the global configuration. (default: None)
    """

    def __init__(
        self,
        name: Union[str, None] = None,
        echo_output: bool = False,
        delete_files: bool = True,
        opensees_path: Union[Path, None] = None,
        scratch_path: Union[Path, None] = None,
    ):
        if name is None:
            name = self.__class__.__name__

        self.name = name
        self.echo_output = echo_output
        self.delete_files = delete_files
        self.opensees_path = opensees_path
        self.scratch_path = scratch_path

    def __repr__(self):
        clsname = self.__class__.__module__ + "." + self.__class__.__name__
        return f"<{clsname} {self.name!r} at {id(self):#x}>"

    @property
    def opensees_path(self):
        """Path to the OpenSees binary to use.

        If None, uses the value of ``config.path_of.opensees``.
        """
        return self._opensees_path

    @opensees_path.setter
    def opensees_path(self, value):
        if value is None:
            value = config.path_of.opensees
        self._opensees_path = Path(value)

    @property
    def scratch_path(self):
        """Path to the base scratch directory.

        If None, uses the value of ``config.path_of.scratch``.
        """
        return self._scratch_path

    @scratch_path.setter
    def scratch_path(self, value):
        if value is None:
            value = config.path_of.scratch
        self._scratch_path = Path(value)

    def create_scratch_filer(self, *, delete: Union[bool, None] = None):
        """Create a new scratch filer.

        Parameters
        ----------
        delete : bool, optional
            Automatically remove the temporary directory created by the
            scratch filer upon finalization. (default: `self.delete_files`)

        Example
        -------
        >>> analysis = OpenSeesAnalysis(scratch_path='/path/to/scratchdir')
        >>> scratch_file = analysis.create_scratch_filer()
        >>> scratch_file('disp', '.dat')
        PosixPath('/path/to/scratchdir/OpenSeesAnalysis-5psb4f7s/disp.dat')

        Non-default name:

        >>> analysis = OpenSeesAnalysis(name='Steel04Test', scratch_path='/path/to/scratchdir')
        >>> scratch_file = analysis.create_scratch_filer()
        >>> scratch_file('disp', '.dat')
        PosixPath('/path/to/scratchdir/Steel04Test-5psb4f7s/disp.dat')
        """
        if delete is None:
            delete = self.delete_files
        return ScratchFile(self.name, self.scratch_path, delete=delete)

    def run_opensees(
        self, inputfile: str, echo: Union[bool, None] = None
    ) -> AnalysisResults:
        """Run an OpenSees script.

        Note that all script output is redirected to stdout.

        Parameters
        ----------
        inputfile
            Script to execute.
        echo : optional
            If True, echo output to console. If not provided, uses the
            `self.echoOutput` setting.

        Returns
        -------
        results : AnalysisResults
            Completed process information.
        """
        if echo is None:
            echo = self.echo_output

        opensees = shutil.which(self.opensees_path)
        if opensees is None:
            raise RuntimeError(f"No executable found at {str(self.opensees_path)!r}")

        LINE_BUFFERED = 1
        popen = partial(
            sub.Popen,
            [opensees, str(inputfile)],
            bufsize=LINE_BUFFERED,
            stdout=sub.PIPE,
            stderr=sub.STDOUT,
            text=True,
        )

        stdout = []
        if echo:
            with popen() as p:
                for line in p.stdout:
                    print(line, end="")
                    stdout.append(line)
        else:
            with popen() as p:
                for line in p.stdout:
                    stdout.append(line)

        stdout = "".join(stdout)
        return AnalysisResults(p.returncode, stdout)
