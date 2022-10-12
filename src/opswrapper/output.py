import dataclasses
from pathlib import Path
from typing import Optional, Tuple, Union

import numpy as np

from . import base
from . import utils


@dataclasses.dataclass
class ElementRecorder(base.OpenSeesObject):
    R"""Element recorder.

    Parameters
    ----------
    file : str, Path, optional
        Filename to record to. This is printed to the file within braces, so no
        variable substitution on the Tcl side is supported. If not given,
        '{file}' is printed instead, allowing for substitution later using
        ``.format(file='/path/to/file')``. Note that Tcl interprets backslashes
        as escape characters, so a more complete format might be ``.format(file=
        filename.replace('\\', '/'))``. (default: None)
    fileformat : str, optional
        File format to use. Options: 'file' (ASCII), 'xml', 'binary'.
        (default: 'file')
    precision : int, optional
        Precision (number of significant figures) of the recorder. If None, uses
        the default OpenSees precision (6). (default: None)
    elements : array-like or 'all'
        Element tags to record. If 'all', the `getEleTags` command is used to
        produce a list of all elements.
    region : int, optional
        Region tag whose elements to record.
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
    file: Optional[Union[str, Path]] = None
    fileformat: str = 'file'
    precision: int = None
    elements: np.ndarray = None
    region: int = None
    dofs: np.ndarray = None
    response: str = None

    def __post_init__(self):
        if self.fileformat not in ['file', 'xml', 'binary']:
            raise ValueError(
                "ElementRecorder: given file format is not recognized "
                f"(expected one of 'file', 'xml', 'binary'; got {self.fileformat!r}"
            )

    def tcl_code(self, formats=None) -> str:
        args = ['recorder Element', f'-{self.fileformat}']

        file_arg, tcl_list_expansion = _format_file_arg(self.file)
        args.append(file_arg)

        if str(self.elements) == 'all':
            args.append(f'-ele {tcl_list_expansion}[getEleTags]')
        elif self.elements is not None:
            args.append('-ele')
            args.extend(utils.coerce_numeric(tag, int) for tag in np.asarray(self.elements).flat)

        if self.region is not None:
            args.append('-region')
            args.append(self.region)

        if self.precision is not None:
            args.append('-precision')
            args.append(self.precision)

        if self.dofs is not None:
            args.append('-dof')
            args.extend(utils.coerce_numeric(dof, int) for dof in np.asarray(self.dofs).flat)

        args.append(self.response)
        return ' '.join(self.format_objects(args, formats))


@dataclasses.dataclass
class NodeRecorder(base.OpenSeesObject):
    R"""Node recorder.

    Parameters
    ----------
    file : str, Path, optional
        Filename to record to. This is printed to the file within braces, so no
        variable substitution on the Tcl side is supported. If not given,
        '{file}' is printed instead, allowing for substitution later using
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
    nodes : array-like or 'all', optional
        Node tags to record. If 'all', the `getNodeTags` command is used to
        produce a list of all nodes.
    node_range : 2-tuple or array-like, optional
        Pair of node tags that define the range to record.
    region : int, optional
        Region tag whose nodes to record.
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
    file: Optional[Union[str, Path]] = None
    fileformat: str = 'file'
    precision: int = None
    time_series: int = None
    time: bool = False
    nodes: np.ndarray = None
    node_range: np.ndarray = None
    region: int = None
    dofs: np.ndarray = None
    response: str = None

    def __post_init__(self):
        if self.fileformat not in ['file', 'xml', 'binary']:
            raise ValueError(
                "NodeRecorder: given file format is not recognized "
                f"(expected one of 'file', 'xml', 'binary'; got {self.fileformat!r}"
            )

    def tcl_code(self, formats=None) -> str:
        args = ['recorder Node', f'-{self.fileformat}']

        file_arg, tcl_list_expansion = _format_file_arg(self.file)
        args.append(file_arg)

        if self.precision is not None:
            args.append('-precision')
            args.append(self.precision)

        if self.time_series is not None:
            args.append('-timeSeries')
            args.append(self.time_series)

        if self.time:
            args.append('-time')

        if str(self.nodes) == 'all':
            args.append(f'-node {tcl_list_expansion}[getNodeTags]')
        elif self.nodes is not None:
            args.append('-node')
            args.extend(utils.coerce_numeric(tag, int) for tag in np.asarray(self.nodes).flat)

        if self.node_range is not None:
            args.append('-nodeRange')
            args.extend(self.node_range)

        if self.region is not None:
            args.append('-region')
            args.append(self.region)

        if self.dofs is not None:
            args.append('-dof')
            args.extend(utils.coerce_numeric(dof, int) for dof in np.asarray(self.dofs).flat)

        args.append(self.response)
        return ' '.join(self.format_objects(args, formats))


def _format_file_arg(file: Union[str, Path] = None) -> Tuple[str, str]:
    if file is None:
        # Escape enclosing brackets for a total of three brackets on either side
        file_arg = '{{{file}}}'
        # If the returned string is being returned with '{file}' in it to be formatted later,
        # need to escape the brackets in the list expansion operator. Otherwise, a completely
        # baffling KeyError will be raised when calling '.format'.
        tcl_list_expansion = '{{*}}'
    else:
        file = utils.path_for_tcl(file)
        file_arg = '{%s}' % file
        tcl_list_expansion = '{*}'
    return file_arg, tcl_list_expansion
