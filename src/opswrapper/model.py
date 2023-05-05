"""Basic OpenSees modeling commands."""

import dataclasses
from typing import Iterable, Optional, Union

import numpy as np

from . import base
from .utils import coerce_numeric

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

    def tcl_code(self, formats=None) -> str:
        args = ["model", "basic", "-ndm", self.ndm, "-ndf", self.ndf]
        return " ".join(self.format_objects(args, formats))


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
    coords: np.ndarray
    mass: Optional[np.ndarray] = None

    def __init__(
        self,
        tag: int,
        *coords: Union[float, Iterable[float]],
        mass: Optional[Iterable[float]] = None
    ):
        super().__init__()
        self.tag = tag
        self.coords = np.array(coords).flatten()
        if mass is not None:
            mass = np.array(mass).flatten()
        self.mass = mass

    def tcl_code(self, formats=None) -> str:
        args = ["node", self.tag]
        args.extend([coerce_numeric(c, float) for c in self.coords])
        if self.mass is not None:
            args.append("-mass")
            args.extend([coerce_numeric(m, float) for m in self.mass])
        return " ".join(self.format_objects(args, formats))
