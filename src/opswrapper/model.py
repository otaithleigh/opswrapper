"""Basic OpenSees modeling commands."""

import dataclasses

import numpy as np

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

    def tcl_code(self, **format_spec) -> str:
        fmt = self.get_format_spec(**format_spec)
        i, f = fmt.int, fmt.float
        code = f'model basic -ndm {self.ndm:{i}} -ndf {self.ndf:{i}}'
        return code


@dataclasses.dataclass(init=False)
class Node(base.OpenSeesObject):
    """Node in the model.
    
    Parameters
    ----------
    tag : int
        Integer tag identifying the node.
    *coords : float
        NDM coordinates of the node.
    mass : tuple, optional
        NDF-length tuple of nodal masses.
    """
    tag: int
    coords: tuple
    mass: tuple = None

    def __init__(self, tag, *coords, mass=None):
        super().__init__()
        self.tag = tag
        self.coords = np.array(coords).flatten()
        if mass is not None:
            mass = np.array(mass).flatten()
        self.mass = mass

    def tcl_code(self, **format_spec) -> str:
        fmt = self.get_format_spec(**format_spec)
        i, f = fmt.int, fmt.float
        code = [f'node {self.tag:{i}}', *[f'{c:{f}}' for c in self.coords]]
        if self.mass is not None:
            code.append(f'-mass')
            code.extend([f'{m:{f}}' for m in self.mass])

        return ' '.join(code)
