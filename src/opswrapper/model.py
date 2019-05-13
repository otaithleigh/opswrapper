"""Basic OpenSees modeling commands."""

import dataclasses

from . import base

__all__ = [
    "Model",
    "Node",
]


@dataclasses.dataclass
class Model(base.OpenSeesObject):
    """Model constructor.
    
    Parameters
    ----------
    ndm: int
        Number of dimensions.
    ndf: int
        Number of degrees-of-freedom per node.
    """
    ndm: int
    ndf: int

    def tcl_code(self) -> str:
        code = f"model basic -ndm {self.ndm} -ndf {self.ndf}"
        return code


@dataclasses.dataclass
class Node(base.OpenSeesObject):
    """Node in the model.
    
    Parameters
    ----------
    tag : int
        Integer tag identifying the node.
    coords : tuple
        Tuple of coordinates of the node.
    mass : tuple, optional
        NDF-length tuple of nodal masses.
    """
    tag: int
    coords: tuple
    mass: tuple = None

    def __post_init__(self):
        if not isinstance(self.coords, tuple):
            self.coords = (float(self.coords), )

    def tcl_code(self) -> str:
        code = [f"node {self.tag}", *[f" {c:g}" for c in self.coords]]
        if self.mass is not None:
            code.append(f" -mass")
            for m in self.mass:
                code.append(f" {m:g}")

        return "".join(code)
