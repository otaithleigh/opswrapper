"""Helpers for running OpenSees."""

import subprocess as sub
import uuid
import warnings
from pathlib import Path
from typing import NamedTuple, Optional

from . import config


def _get_str_uuid4():
    return str(uuid.uuid4())


def _get_default_scratch_path():
    return config.path_of.scratch


class ScratchFile():
    """Create a scratch file path generator.

    Parameters
    ----------
    analysis_type : str
        Type of the analysis, e.g. 'SectionAnalysis'.
    analysis_id : optional
        Unique ID for the analysis. Useful for parallel execution. If None, a
        random UUID is generated. (default: None)
    scratch_path : path_like
        Path to the scratch directory. If None, uses `config.path_of.scratch`.
        (default: None)

    Returns
    -------
    scratch_file : (name: str, suffix: str = '') -> Path
        A function that takes two arguments, 'name' and 'suffix', returning a
        Path object.

    Example
    -------
    >>> scratch_file = scratch_file_factory('TestoPresto', 0)
    >>> scratch_file('disp', '.dat')
    PosixPath('/tmp/TestoPresto_0_disp.dat')
    """
    def __init__(
        self,
        analysis_type: str,
        analysis_id: Optional[str] = None,
        scratch_path: Optional[Path] = None
    ):
        if analysis_id is None:
            analysis_id = _get_str_uuid4()
        if scratch_path is None:
            scratch_path = _get_default_scratch_path()

        self.analysis_type = str(analysis_type)
        self.analysis_id = str(analysis_id)
        self.scratch_path = Path(scratch_path).resolve()

    def __repr__(self) -> str:
        analysis_type = self.analysis_type
        analysis_id = self.analysis_id
        scratch_path = self.scratch_path
        return f'ScratchFile({analysis_type=}, {analysis_id=}, {scratch_path=})'

    def __call__(self, name: str, suffix: str = '') -> Path:
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
        components = []
        if self.analysis_type:
            components.append(self.analysis_type)
        if self.analysis_id:
            components.append(self.analysis_id)
        components.append(f'{name}{suffix}')
        filename = '_'.join(components)

        return self.scratch_path/filename


def scratch_file_factory(*args, **kwargs):
    warnings.warn('opswrapper.analysis.scratch_file_factory is deprecated.'
                  'Use opswrapper.analysis.ScratchFile instead.')
    return ScratchFile(*args, **kwargs)


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


class OpenSeesAnalysis():
    """Wrapper for an OpenSees analysis.

    Parameters
    ----------
    name : str, optional
        Descriptive name for the analysis object. Defaults to the class name.
    echo_output : bool, optional
        If True, echo OpenSees output to stdout. (default: False)
    delete_files : bool, optional
        If True, delete temporary files after each run. (default: True)
    opensees_path : Path, optional
        Path to the OpenSees binary to use. If None, uses the value from the
        global configuration. (default: None)
    scratch_path : Path, optional
        Path to the directory for storing temporary files. If None, uses the
        value from the global configuration. (default: None)
    """
    def __init__(
        self,
        name: str = None,
        echo_output: bool = False,
        delete_files: bool = True,
        opensees_path: Path = None,
        scratch_path: Path = None,
    ):
        if name is None:
            name = self.__class__.__name__

        self.name = name
        self.echo_output = echo_output
        self.delete_files = delete_files
        self.opensees_path = opensees_path
        self.scratch_path = scratch_path

    def __repr__(self):
        clsname = self.__class__.__module__ + '.' + self.__class__.__name__
        return f'<{clsname} {self.name!r} at {id(self):#x}>'

    @property
    def opensees_path(self):
        """Path to the OpenSees binary to use.

        If None, looks for 'OpenSees' on the system PATH.
        """
        return self._opensees_path

    @opensees_path.setter
    def opensees_path(self, value):
        if value is None:
            value = config.path_of.opensees
        self._opensees_path = Path(value)

    @property
    def scratch_path(self):
        return self._scratch_path

    @scratch_path.setter
    def scratch_path(self, value):
        if value is None:
            value = config.path_of.scratch
        self._scratch_path = Path(value)

    def create_scratch_filer(self, analysis_id=None):
        """Create a new scratch file function with a particular analysis id.

        Parameters
        ----------
        analysis_id : optional
            Unique analysis ID. If not provided, a random UUID is generated to
            serve as the analysis ID.

        Example
        -------
        >>> analysis = UniaxialMaterialAnalysis(...)
        >>> scratch_file = analysis.create_scratch_filer('foo')
        >>> scratch_file('disp', '.dat')
        PosixPath('/path/to/scratchdir/UniaxialMaterialAnalysis_foo_disp.dat')

        Non-default name:

        >>> analysis = UniaxialMaterialAnalysis(name='Steel04Test', ...)
        >>> scratch_file = analysis.create_scratch_filer('bar')
        >>> scratch_file('disp', '.dat')
        PosixPath('/path/to/scratchdir/Steel04Test_bar_disp.dat')
        """
        return ScratchFile(self.name, analysis_id, self.scratch_path)

    def run_opensees(self, inputfile: str, echo: bool = None) -> AnalysisResults:
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

        cmd = [str(self.opensees_path), str(inputfile)]
        stdout = []
        if echo:
            def handle_stdout(line):
                print(line, end='')
                stdout.append(line)
        else:
            def handle_stdout(line):
                stdout.append(line)

        with sub.Popen(cmd, bufsize=1, stdout=sub.PIPE, stderr=sub.STDOUT, text=True) as p:
            for line in p.stdout:
                handle_stdout(line)

        stdout = ''.join(stdout)

        return AnalysisResults(p.returncode, stdout)
