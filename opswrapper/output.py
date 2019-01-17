from __future__ import annotations

import dataclasses

import numpy as np

from . import base


@dataclasses.dataclass
class ElementRecorder(base.OpenSeesObject):
    """Element recorder.
        
    All parameters are keyword-only.

    Parameters
    ----------
    file : str
        Filename to record to. This is printed to the file within braces, so no
        variable substitution on the Tcl side is supported.
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
    file: str
    elements: np.ndarray
    response: str
    dofs: np.ndarray = None

    def tcl_code(self) -> str:
        command = f"recorder Element -file {{{self.file}}}"
        command += " -ele " + " ".join([f"{tag:d}" for tag in np.array(self.elements).flat])

        if self.dofs is not None:
            command += " -dof " + " ".join([f"{dof:d}" for dof in np.array(self.dofs).flat])

        command += f" {self.response}"

        return command


@dataclasses.dataclass
class NodeRecorder(base.OpenSeesObject):
    """Node recorder.
    
    All parameters are keyword-only.

    Parameters
    ----------
    file : str
        Filename to record to. This is printed to the file within braces, so no
        variable substitution on the Tcl side is supported.
    time : bool, optional
        If True, places domain time in the first entry of each line. (default=False)
    nodes : array-like
        Node tags to record.
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

    Returns
    -------
    command : str
        The formatted OpenSees command to create the element recorder.

    Example
    -------
    >>> NodeRecorder(file='/path/to/file', nodes=1, dofs=[1, 2], response='disp').tcl_code()
    'recorder Node -file {/path/to/file} -node 1 -dof 1 2 disp'
    """
    file: str
    nodes: np.ndarray
    response: str
    time: bool = False
    dofs: np.ndarray = None

    def tcl_code(self):
        command = f"recorder Node -file {{{self.file}}}"
        if self.time:
            command += " -time"

        command += " -node " + " ".join([f"{tag:d}" for tag in np.array(self.nodes).flat])

        if self.dofs is not None:
            command += " -dof " + " ".join([f"{dof:d}" for dof in np.array(self.dofs).flat])

        command += f" {self.response}"
        return command
