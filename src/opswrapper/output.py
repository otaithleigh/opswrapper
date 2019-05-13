import dataclasses

import numpy as np

from . import base


@dataclasses.dataclass
class ElementRecorder(base.OpenSeesObject):
    """Element recorder.

    All parameters are keyword-only.

    Parameters
    ----------
    file : str, optional
        Filename to record to. This is printed to the file within braces, so no
        variable substitution on the Tcl side is supported. If not given,
        '{{file}}' is printed instead, allowing for substitution later using
        ``.format(file='/path/to/file')``.
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

    def tcl_code(self) -> str:
        if self.file is not None:
            command = f"recorder Element -{self.fileformat} {{{self.file!s}}}"
        else:
            command = f"recorder Element -{self.fileformat}" " {{{file!s}}}"

        command += " -ele " + " ".join([f"{tag:d}" for tag in np.array(self.elements).flat])

        if self.precision is not None:
            command += f" -precision {self.precision:d}"

        if self.dofs is not None:
            command += " -dof " + " ".join([f"{dof:d}" for dof in np.array(self.dofs).flat])

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
        ``.format(file='/path/to/file')``. (default: None)
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
    node_range : array-like, optional
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
    dofs: np.ndarray = None
    response: str = None

    def __post_init__(self):
        if self.fileformat not in ['file', 'xml', 'binary']:
            raise ValueError(
                "NodeRecorder: given file format is not recognized ",
                f"(expected one of 'file', 'xml', 'binary'; got {self.fileformat!r}"
            )

    def tcl_code(self):
        if self.file is not None:
            command = f"recorder Node -{self.fileformat} {{{self.file!s}}}"
        else:
            command = f"recorder Node -{self.fileformat}" " {{{file!s}}}"

        if self.precision is not None:
            command += f" -precision {self.precision:d}"

        if self.time_series is not None:
            command += f' -timeSeries {self.time_series:d}'

        if self.time:
            command += " -time"

        if self.nodes is not None:
            command += " -node " + " ".join([f"{tag:d}" for tag in np.array(self.nodes).flat])

        if self.node_range is not None:
            command += f" -nodeRange {self.node_range[0]:d} {self.node_range[1]:d}"

        if self.dofs is not None:
            command += " -dof " + " ".join([f"{dof:d}" for dof in np.array(self.dofs).flat])

        command += f" {self.response}"
        return command