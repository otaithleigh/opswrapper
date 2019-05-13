"""Helpers for running OpenSees."""

import dataclasses
import pathlib
import subprocess as sub
import uuid
import warnings

import numpy as np
import xarray as xr

from . import config
from . import utils
from .model import Model, Node
from .output import ElementRecorder


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

    def scratch_file(self, filename: str) -> pathlib.Path:
        """Return the path to `filename` in the scratch directory."""
        return self.scratch_path/filename

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

        cmd = [str(self.opensees_path), inputfile]
        stdout = []

        with sub.Popen(cmd, bufsize=1, stdout=sub.PIPE, stderr=sub.STDOUT, text=True) as p:
            if echo:
                for line in p.stdout:
                    print(line, end='')
                    stdout.append(line)
            else:
                for line in p.stdout:
                    stdout.append(line)

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
            f'element truss 1 1 2 1.0 {self.tag:d}',
            f'pattern Plain 1 "Series -dt 1.0 -filePath {{{filename_pattern!s}}} -factor 1.0" {{',
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
