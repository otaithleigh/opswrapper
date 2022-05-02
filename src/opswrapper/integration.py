"""Integration methods for force-based beam-columns."""

import dataclasses
import typing as t

from . import base
from .utils import coerce_numeric


@dataclasses.dataclass
class Integration(base.OpenSeesObject):
    def tcl_code(self, formats=None) -> str:
        return '"' + ' '.join(self.tcl_args(formats)) + '"'


@dataclasses.dataclass
class Lobatto(Integration):
    """Gauss-Lobatto integration.

    Gauss-Lobatto integration places an integration point at each end of the
    element, where bending moments are largest in the absence of interior
    element loads. The order of accuracy is 2N-3.

    Parameters
    ----------
    section : int
        Tag of the section.
    npoints : int
        Number of integration points to use.
    """
    section: int
    npoints: int

    def tcl_args(self, formats=None) -> t.List[str]:
        args = ['Lobatto', self.section, self.npoints]
        return self.format_objects(args, formats)


@dataclasses.dataclass
class Legendre(Integration):
    """Gauss-Legendre integration.

    Gauss-Legendre integration is more accurate than Gauss-Lobatto, but is less
    common for force-based elements because there are no integration points at
    the element ends. The order of accuracy is 2N-1.

    Parameters
    ----------
    section : int
        Tag of the section.
    npoints : int
        Number of integration points to use.
    """
    section: int
    npoints: int

    def tcl_args(self, formats=None) -> t.List[str]:
        args = ['Legendre', self.section, self.npoints]
        return self.format_objects(args, formats)


@dataclasses.dataclass
class Radau(Integration):
    """Gauss-Radau integration.

    Gauss-Radau integration is not common in force-based elements because it
    places an integration point at only one end of the element; however, it
    forms the basis for optimal plastic hinge integration methods.The order of
    accuracy is 2N-2.

    Parameters
    ----------
    section : int
        Tag of the section.
    npoints : int
        Number of integration points to use.
    """
    section: int
    npoints: int

    def tcl_args(self, formats=None) -> t.List[str]:
        args = ['Radau', self.section, self.npoints]
        return self.format_objects(args, formats)


@dataclasses.dataclass
class NewtonCotes(Integration):
    """Newton-Cotes integration.

    Newton-Cotes places integration points uniformly along the element,
    including a point at each end of the element. The order of accuracy is N-1.

    Parameters
    ----------
    section : int
        Tag of the section.
    npoints : int
        Number of integration points to use.
    """
    section: int
    npoints: int

    def tcl_args(self, formats=None) -> t.List[str]:
        args = ['NewtonCotes', self.section, self.npoints]
        return self.format_objects(args, formats)


@dataclasses.dataclass()
class FixedLocation(Integration):
    """Integration at user-specified points.

    Parameters
    ----------
    sections : tuple[int]
        Tuple of section tags.
    locations : tuple[float]
        Tuple of locations, specified as factors of the element length.
    """
    sections: t.Tuple[int, ...]
    locations: t.Tuple[float, ...]

    def __post_init__(self):
        if len(self.sections) != len(self.locations):
            raise ValueError("FixedLocation: len(sections) must equal len(locations)")

    def tcl_args(self, formats=None) -> t.List[str]:
        args = ['FixedLocation', len(self.sections)]
        args.extend([coerce_numeric(tag, int) for tag in self.sections])
        args.extend([coerce_numeric(loc, float) for loc in self.locations])
        return self.format_objects(args, formats)
