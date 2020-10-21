"""Helpers for running OpenSees."""

import dataclasses
import pathlib
import subprocess as sub
import uuid
import warnings

import numpy as np
import xarray as xr

from . import config
from . import element
from . import utils
from .model import Model, Node
from .output import ElementRecorder


def scratch_file_factory(analysis_type: str, scratch_path=None, analysis_id=0):
    """Create a scratch file path generator.

    Parameters
    ----------
    analysis_type : str
        Type of the analysis, e.g. 'SectionAnalysis'.
    scratch_path : path_like
        Path to the scratch directory. If None, uses the system temp directory.
        (default: None)
    analysis_id : optional
        Unique ID for the analysis. Useful for parallel execution, for example.
        (default: 0)

    Returns
    -------
    scratch_file
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

    def scratch_file(name: str, suffix: str = '') -> pathlib.Path:
        """
        Parameters
        ----------
        name : str
            Name of the scratch file, e.g. 'displacement'.
        suffix : str, optional
            Suffix to use for the scratch file. (default: '')
        """
        return scratch_path/f'{analysis_type}_{name}_{analysis_id}{suffix}'

    return scratch_file


@dataclasses.dataclass
class AnalysisResults():
    """Results from an OpenSees analysis.

    Parameters
    ----------
    returncode
        The return code from OpenSees.
    stdout
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
        PosixPath('/home/ptalley2/Scratch/UniaxialMaterialAnalysis_disp_foo.dat')
        """
        if analysis_id is None:
            analysis_id = uuid.uuid4()
        return scratch_file_factory(self.__class__.__name__, self.scratch_path, analysis_id)

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


class UniaxialMaterialAnalysis(OpenSeesAnalysis):
    def __init__(
        self,
        material,
        tag=1,
        echo_output=False,
        delete_files=True,
        opensees_path=None,
        scratch_path=None
    ):
        super().__init__(
            echo_output=echo_output,
            delete_files=delete_files,
            opensees_path=opensees_path,
            scratch_path=scratch_path
        )
        self.material = material
        self.tag = tag

    def run_analysis(self, peak_points, rate_type=None, rate_value=None):
        """"""
        peak_points = np.array(peak_points)
        results = xr.Dataset()

        # Filenames
        prefix = 'UniaxialMaterialAnalysis_'
        analysis_id = uuid.uuid4()
        filename_input = self.scratch_file(f'{prefix}input_{analysis_id}.tcl')
        filename_pattern = self.scratch_file(f'{prefix}input_pattern_{analysis_id}.dat')
        filename_output_force = self.scratch_file(f'{prefix}output_force_{analysis_id}.dat')
        filename_output_disp = self.scratch_file(f'{prefix}output_disp_{analysis_id}.dat')
        filename_output_stiff = self.scratch_file(f'{prefix}output_stiff_{analysis_id}.dat')

        numbers = _generate_imposed_displacement(peak_points, rate_type, rate_value)
        numsteps = numbers.size - 2

        np.savetxt(filename_pattern, numbers)
        model = [
            Model(ndm=1, ndf=1),
            Node(1, 0.0),
            Node(2, 1.0),
            'fix 1 1',
            self.material,
            element.Truss(1, 1, 2, 1.0, mat=self.tag),
            f'pattern Plain 1 "Series -dt 1.0 -filePath {{{utils.path_for_tcl(filename_pattern)!s}}} -factor 1.0" {{',
            '    sp 2 1 1.0',
            '}',
            ElementRecorder(file=filename_output_force, precision=10, elements=1, response='force'),
            ElementRecorder(file=filename_output_disp, precision=10, elements=1, response='deformations'),
            ElementRecorder(file=filename_output_stiff, precision=10, elements=1, response='stiff'),
            'system UmfPack',
            'constraints Penalty 1.0e12 1.0e12',
            'test NormDispIncr 1.0e-8 10 0',
            'algorithm Newton',
            'numberer RCM',
            'integrator LoadControl 1.0',
            'analysis Static',
            f'set ok [analyze {numsteps:d}]',
            'if {$ok != 0} {exit 2}',
            'exit 1',
        ]
        utils.print_model(model, file=filename_input)

        process = self.run_opensees(filename_input)
        if process.returncode == 1:
            status = 'Analysis successful'
        elif process.returncode == 2:
            status = 'Analysis failed'
            warnings.warn("UniaxialMaterialAnalysis.run_analysis: analysis failed")
        else:
            raise RuntimeError(
                f"Analysis ended in an unknown manner, exit code: {process.returncode}"
            )

        # Read results
        disp = np.loadtxt(filename_output_disp)
        results['disp'] = xr.DataArray(disp, dims='time')

        force = np.loadtxt(filename_output_force)
        results['force'] = xr.DataArray(force[:, 1], dims='time')

        with warnings.catch_warnings() as cw:
            warnings.simplefilter('ignore')
            stiff = np.loadtxt(filename_output_stiff)
        if len(stiff) != 0:
            results['stiff'] = xr.DataArray(stiff, dims='time')

        results.attrs['status'] = status
        results.attrs['stdout'] = process.stdout

        # Cleanup
        if self.delete_files:
            for file in [
                filename_input,
                filename_output_disp,
                filename_output_force,
                filename_output_stiff,
                filename_pattern,
            ]:
                file.unlink()

        return results


def _generate_imposed_displacement(peak_points, rate_type=None, rate_value=None):
    if rate_type is not None and rate_value is None:
        raise TypeError("rate_value must be specified if rate_type is not None")

    rate = {
        'StrainRate': lambda: rate_value,
        'Steps': lambda: np.sum(np.abs(np.diff(peak_points)))/rate_value,
        None: lambda: np.max(np.abs(np.diff(peak_points))),
    }[rate_type]()

    numbers = utils.fill_out_numbers(peak_points, rate).flatten()
    return np.array([numbers[0], *numbers, numbers[-1]])
