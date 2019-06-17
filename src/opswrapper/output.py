import dataclasses

import numpy as np

from . import base
from . import utils


@dataclasses.dataclass
class ElementRecorder(base.OpenSeesObject):
    R"""Element recorder.

    Parameters
    ----------
    file : str, optional
        Filename to record to. This is printed to the file within braces, so no
        variable substitution on the Tcl side is supported. If not given,
        '{{file}}' is printed instead, allowing for substitution later using
        ``.format(file='/path/to/file')``. Note that Tcl interprets backslashes
        as escape characters, so a more complete format might be ``.format(file=
        filename.replace('\\', '/'))``. (default: None)
    fileformat : str, optional
        File format to use. Options: 'file' (ASCII), 'xml', 'binary'.
        (default: 'file')
    precision : int, optional
        Precision (number of significant figures) of the recorder. If None, uses
        the default OpenSees precision (6). (default: None)
    elements : array-like
        Element tags to record.
    dofs : array-like, optional
        DOFs to record.
    response : str
        Response to record. Valid options depend on the elements being queried.

    Example
    -------
    >>> ElementRecorder(file='/path/to/file', elements=1, dofs=[1, 2],
    ... response='localForce').tcl_code()
    'recorder Element -file {/path/to/file} -ele 1 -dof 1 2 localForce'
    """
    file: str = None
    fileformat: str = 'file'
    precision: int = None
    elements: np.ndarray = None
    dofs: np.ndarray = None
    response: str = None

    def __post_init__(self):
        if self.fileformat not in ['file', 'xml', 'binary']:
            raise ValueError(
                "ElementRecorder: given file format is not recognized "
                f"(expected one of 'file', 'xml', 'binary'; got {self.fileformat!r}"
            )

    def tcl_code(self, **format_spec) -> str:
        fmt = self.get_format_spec(**format_spec)
        i, f = fmt.int, fmt.float
        if self.file is not None:
            file = utils.path_for_tcl(self.file)
            command = f"recorder Element -{self.fileformat} {{{file!s}}}"
        else:
            command = f"recorder Element -{self.fileformat}" " {{{file!s}}}"

        command += " -ele " + " ".join([f"{tag:{i}}" for tag in np.array(self.elements).flat])

        if self.precision is not None:
            command += f" -precision {self.precision:{i}}"

        if self.dofs is not None:
            command += " -dof " + " ".join([f"{dof:{i}}" for dof in np.array(self.dofs).flat])

        command += f" {self.response}"

        return command


@dataclasses.dataclass
class NodeRecorder(base.OpenSeesObject):
    """Node recorder.

    Parameters
    ----------
    file : str, optional
        Filename to record to. This is printed to the file within braces, so no
        variable substitution on the Tcl side is supported. If not given,
        '{{file}}' is printed instead, allowing for substitution later using
        ``.format(file='/path/to/file')``. Note that Tcl interprets backslashes
        as escape characters, so a more complete format might be ``.format(file=
        filename.replace('\\', '/'))``. (default: None)
    fileformat : str, optional
        File format to use. Options: 'file' (ASCII), 'xml', 'binary'.
        (default: 'file')
    precision : int, optional
        Precision (number of significant figures) of the recorder. If None, uses
        the default OpenSees precision (6). (default: None)
    time_series : int, optional
        Tag of an existing timeSeries. If provided, results from the nodes at each
        time step are added to the load factor from the series.
    time : bool, optional
        If True, places domain time in the first entry of each line. (default=False)
    nodes : array-like
        Node tags to record.
    node_range : 2-tuple or array-like, optional
        Pair of node tags that define the range to record.
    dofs : array-like, optional
        DOFs to record.
    response : str
        Response to record. See below for valid responses.

    Valid Responses
    ---------------

    ==============  =========================
    Response        Description
    ==============  =========================
    disp            displacement
    vel             velocity
    accel           acceleration
    incrDisp        incremental displacement
    "eigen i"       eigenvector for mode i
    reaction        nodal reaction
    rayleighForces  damping forces
    ==============  =========================

    Example
    -------
    >>> NodeRecorder(file='/path/to/file', nodes=1, dofs=[1, 2], response='disp').tcl_code()
    'recorder Node -file {/path/to/file} -node 1 -dof 1 2 disp'
    """
    file: str = None
    fileformat: str = 'file'
    precision: int = None
    time_series: int = None
    time: bool = False
    nodes: np.ndarray = None
    node_range: np.ndarray = None
    dofs: np.ndarray = None
    response: str = None

    def __post_init__(self):
        if self.fileformat not in ['file', 'xml', 'binary']:
            raise ValueError(
                "NodeRecorder: given file format is not recognized "
                f"(expected one of 'file', 'xml', 'binary'; got {self.fileformat!r}"
            )

    def tcl_code(self, **format_spec) -> str:
        fmt = self.get_format_spec(**format_spec)
        i, f = fmt.int, fmt.float
        if self.file is not None:
            file = utils.path_for_tcl(self.file)
            command = f"recorder Node -{self.fileformat} {{{file!s}}}"
        else:
            command = f"recorder Node -{self.fileformat}" " {{{file!s}}}"

        if self.precision is not None:
            command += f" -precision {self.precision:{i}}"

        if self.time_series is not None:
            command += f' -timeSeries {self.time_series:{i}}'

        if self.time:
            command += " -time"

        if self.nodes is not None:
            command += " -node " + " ".join([f"{tag:{i}}" for tag in np.array(self.nodes).flat])

        if self.node_range is not None:
            command += f" -nodeRange {self.node_range[0]:{i}} {self.node_range[1]:{i}}"

        if self.dofs is not None:
            command += " -dof " + " ".join([f"{dof:{i}}" for dof in np.array(self.dofs).flat])

        command += f" {self.response}"
        return command
