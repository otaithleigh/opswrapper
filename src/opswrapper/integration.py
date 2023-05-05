"""Integration methods for force-based beam-columns."""

import dataclasses
import typing as t

from . import base
from .utils import coerce_numeric


@dataclasses.dataclass
class Integration(base.OpenSeesObject):
    def tcl_code(self, formats=None) -> str:
        return '"' + " ".join(self.tcl_args(formats)) + '"'


# ======================================================================================
# Distributed plasticity
# ======================================================================================
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
        args = ["Lobatto", self.section, self.npoints]
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
        args = ["Legendre", self.section, self.npoints]
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
        args = ["Radau", self.section, self.npoints]
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
        args = ["NewtonCotes", self.section, self.npoints]
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
        args = ["FixedLocation", len(self.sections)]
        args.extend([coerce_numeric(tag, int) for tag in self.sections])
        args.extend([coerce_numeric(loc, float) for loc in self.locations])
        return self.format_objects(args, formats)


# ======================================================================================
# Plastic hinge
# ======================================================================================
@dataclasses.dataclass
class PlasticHinge(Integration):
    sec_i: int
    lp_i: float
    sec_j: int
    lp_j: float
    sec_e: int

    def tcl_args(self, formats=None) -> t.List[str]:
        typ = type(self).__name__
        return self.format_objects(
            [typ, self.sec_i, self.lp_i, self.sec_j, self.lp_j, self.sec_e], formats
        )


@dataclasses.dataclass
class HingeMidpoint(PlasticHinge):
    """One-point plastic hinge integration.

    Midpoint integration over each hinge region is the most accurate one-point
    integration rule. However, it does not place integration points at the
    element ends and there is a small integration error for linear curvature
    distributions along the element.

    Parameters
    ----------
    sec_i : int
        Tag of section to use for the hinge at the i-end of element.
    lp_i : float
        Length of plastic hinge at i-end of element.
    sec_j : int
        Tag of section to use for the hinge at the j-end of element.
    lp_j : float
        Length of plastic hinge at j-end of element.
    sec_e : int
        Tag of section to use in the middle of the element; usually, but
        not necessarily, elastic.
    """


@dataclasses.dataclass
class HingeRadau(PlasticHinge):
    """Modified two-point Gauss-Radau integration.

    Places an integration point at the element ends and at 8/3 the hinge length
    inside the element. This approach represents linear curvature distributions
    exactly and the characteristic length for softening plastic hinges is equal
    to the assumed plastic hinge length.

    Parameters
    ----------
    sec_i : int
        Tag of section to use for the hinge at the i-end of element.
    lp_i : float
        Length of plastic hinge at i-end of element.
    sec_j : int
        Tag of section to use for the hinge at the j-end of element.
    lp_j : float
        Length of plastic hinge at j-end of element.
    sec_e : int
        Tag of section to use in the middle of the element; usually, but
        not necessarily, elastic.
    """


@dataclasses.dataclass
class HingeRadauTwo(PlasticHinge):
    """Two-point Gauss-Radau integration.

    Places an integration point at the element ends and at 2/3 the hinge length
    inside the element. This approach represents linear curvature distributions
    exactly. However, the characteristic length for softening plastic hinges is
    not equal to the assumed plastic hinge length, and is instead equal to 1/4
    the plastic hinge length.

    Parameters
    ----------
    sec_i : int
        Tag of section to use for the hinge at the i-end of element.
    lp_i : float
        Length of plastic hinge at i-end of element.
    sec_j : int
        Tag of section to use for the hinge at the j-end of element.
    lp_j : float
        Length of plastic hinge at j-end of element.
    sec_e : int
        Tag of section to use in the middle of the element; usually, but
        not necessarily, elastic.
    """
