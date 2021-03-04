"""Helpers for running OpenSees."""

import dataclasses
import pathlib
import subprocess as sub
import tempfile
import uuid
from typing import NamedTuple

from . import config


def scratch_file_factory(analysis_type: str, analysis_id=None, scratch_path=None):
    """Create a scratch file path generator.

    Parameters
    ----------
    analysis_type : str
        Type of the analysis, e.g. 'SectionAnalysis'.
    analysis_id : optional
        Unique ID for the analysis. Useful for parallel execution. If None, a
        random UUID is generated. (default: None)
    scratch_path : path_like
        Path to the scratch directory. If None, uses the system temp directory.
        (default: None)

    Returns
    -------
    scratch_file : (name: str, suffix: str = '') -> Path
        A function that takes two arguments, 'name' and 'suffix', returning a
        Path object.

    Example
    -------
    >>> scratch_file = scratch_file_factory('TestoPresto')
    >>> scratch_file('disp', '.dat')
    PosixPath('/tmp/TestoPresto_disp_0.dat')
    """
    if scratch_path is None:
        scratch_path = tempfile.gettempdir()
    scratch_path = pathlib.Path(scratch_path).resolve()

    if analysis_id is None:
        analysis_id = uuid.uuid4()

    def scratch_file(name: str, suffix: str = '') -> pathlib.Path:
        """
        Parameters
        ----------
        name : str
            Name of the scratch file, e.g. 'displacement'.
        suffix : str, optional
            Suffix to use for the scratch file. (default: '')
        """
        return scratch_path/f'{analysis_type}_{analysis_id}_{name}{suffix}'

    return scratch_file


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


@dataclasses.dataclass(init=False)
class OpenSeesAnalysis():
    """Wrapper for an OpenSees analysis.

    Parameters
    ----------
    echo_output : bool, optional
        If True, echo OpenSees output to stdout. (default: False)
    delete_files : bool, optional
        If True, delete temporary files after each run. (default: True)
    opensees_path : pathlib.Path, optional
        Path to the OpenSees binary to use. If None, uses the value from the
        global configuration. (default: None)
    scratch_path : pathlib.Path, optional
        Path to the directory for storing temporary files. If None, uses the
        value from the global configuration. (default: None)
    """

    echo_output: bool
    delete_files: bool
    opensees_path: pathlib.Path
    scratch_path: pathlib.Path

    def __init__(self, echo_output=False, delete_files=True, opensees_path=None, scratch_path=None):
        self.echo_output = echo_output
        self.delete_files = delete_files
        self.opensees_path = opensees_path
        self.scratch_path = scratch_path

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
        self._opensees_path = pathlib.Path(value)

    @property
    def scratch_path(self):
        return self._scratch_path

    @scratch_path.setter
    def scratch_path(self, value):
        if value is None:
            value = config.path_of.scratch
        self._scratch_path = pathlib.Path(value)

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
        PosixPath('/home/ptalley2/Scratch/UniaxialMaterialAnalysis_foo_disp.dat')
        """
        return scratch_file_factory(self.__class__.__name__, analysis_id, self.scratch_path)

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
