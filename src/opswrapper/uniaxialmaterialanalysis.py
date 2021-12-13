import functools
import warnings

import numpy as np
import xarray as xr

from . import constraints
from . import element
from . import test
from . import utils
from .analysis import OpenSeesAnalysis
from .output import ElementRecorder
from .model import Model, Node


class UniaxialMaterialAnalysis(OpenSeesAnalysis):
    """Analyze an OpenSees uniaxial material via imposed displacement/strain.

    Parameters
    ----------
    material : OpenSeesDef, list[OpenSeesDef]
        Definition of the uniaxial material.
    tag : int
        Tag of the uniaxial material being tested.
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

    def _process_material_definition(self):
        """Sanitize the given material definition into a list of str."""
        try:
            matdef = [str(m) for m in self.material]
        except TypeError:
            matdef = [str(self.material)]

        return matdef

    def run_analysis(
        self,
        peak_points,
        rate_type: str = None,
        rate_value: float = None,
        echo: bool = None,
        analysis_id: str = None
    ):
        """
        Parameters
        ----------
        peak_points : array_like
            Peak displacements (strains) to cycle between.
        rate_type : {'StrainRate', 'Steps', None}, default None
            How to fill in points between those in `peak_points`. 'StrainRate'
            linearly spaces points between each peak at the given rate.
            'Steps' linearly spaces the given number of points between each
            peak. None does no interpolation.
        rate_value : float, optional
            Rate for rate types 'StrainRate' and 'Steps'.
        echo : bool, optional
            Whether to echo OpenSees output to console. (default: `self.echo_output`)
        analysis_id : optional
            Unique identifier for the analysis.

        Example
        -------
        Run an analysis that runs from 0 to 1 to -1 to 2 to -2, with 100
        analysis steps between each peak.

        >>> results = analysis.run_analysis([0, 1, -1, 2, -2], 'Steps', 100)
        """
        peak_points = np.array(peak_points)
        results = xr.Dataset()

        # Filenames
        scratch_file = self.create_scratch_filer(analysis_id)
        files = utils.Namespace()
        files.input = scratch_file('input', '.tcl')
        files.pattern = scratch_file('pattern', '.dat')
        files.output_force = scratch_file('output_force', '.dat')
        files.output_disp = scratch_file('output_disp', '.dat')
        files.output_stiff = scratch_file('output_stiff', '.dat')

        numbers = self._generate_imposed_displacement(peak_points, rate_type, rate_value)
        numsteps = numbers.size - 2

        pattern_filepath = '{' + utils.path_for_tcl(files.pattern) + '}'
        new_recorder = functools.partial(ElementRecorder, precision=10, elements=1)
        material_definition = self._process_material_definition()
        model = [
            Model(ndm=1, ndf=1),
            Node(1, 0.0),
            Node(2, 1.0),
            'fix 1 1',
            *material_definition,
            element.Truss(1, 1, 2, 1.0, mat=self.tag),
            f'pattern Plain 1 "Series -dt 1.0 -filePath {pattern_filepath} -factor 1.0" {{',
            '    sp 2 1 1.0',
            '}',
            new_recorder(file=files.output_force, response='force'),
            new_recorder(file=files.output_disp, response='deformations'),
            new_recorder(file=files.output_stiff, response='stiff'),
            'system UmfPack',
            constraints.Transformation(),
            test.NormDispIncr(tolerance=1e-8, max_iters=10, print_flag=0),
            'algorithm Newton',
            'numberer RCM',
            'integrator LoadControl 1.0',
            'analysis Static',
            f'set ok [analyze {numsteps:d}]',
            'if {$ok != 0} {exit 2}',
            'exit 1',
        ]

        # Write files to disk
        np.savetxt(files.pattern, numbers)
        utils.print_model(model, file=files.input)

        # Run the analysis
        process = self.run_opensees(files.input, echo=echo)
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
        disp = np.loadtxt(files.output_disp)
        results['disp'] = xr.DataArray(disp, dims='time')

        force = np.loadtxt(files.output_force)
        results['force'] = xr.DataArray(force[:, 1], dims='time')

        with warnings.catch_warnings() as cw:
            warnings.simplefilter('ignore')
            stiff = np.loadtxt(files.output_stiff)
        if len(stiff) != 0:
            results['stiff'] = xr.DataArray(stiff, dims='time')

        results.attrs['status'] = status
        results.attrs['stdout'] = process.stdout

        # Cleanup
        if self.delete_files:
            for _, file in files:
                try:
                    file.unlink()
                except FileNotFoundError:
                    continue

        return results

    @staticmethod
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
