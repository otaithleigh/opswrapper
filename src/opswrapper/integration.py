"""Integration methods for force-based beam-columns."""


import dataclasses

from . import base


class Integration:
    pass


@dataclasses.dataclass
class Lobatto(base.OpenSeesObject, Integration):
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

    def tcl_code(self, **format_spec) -> str:
        fmt = self.get_format_spec(**format_spec)
        i, f = fmt.int, fmt.float
        return f'Lobatto {self.section:{i}} {self.npoints:{i}}'


@dataclasses.dataclass
class Legendre(base.OpenSeesObject, Integration):
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

    def tcl_code(self, **format_spec) -> str:
        fmt = self.get_format_spec(**format_spec)
        i, f = fmt.int, fmt.float
        return f'Legendre {self.section:{i}} {self.npoints:{i}}'


@dataclasses.dataclass
class Radau(base.OpenSeesObject, Integration):
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

    def tcl_code(self, **format_spec) -> str:
        fmt = self.get_format_spec(**format_spec)
        i, f = fmt.int, fmt.float
        return f'Radau {self.section:{i}} {self.npoints:{i}}'


@dataclasses.dataclass
class NewtonCotes(base.OpenSeesObject, Integration):
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

    def tcl_code(self, **format_spec) -> str:
        fmt = self.get_format_spec(**format_spec)
        i, f = fmt.int, fmt.float
        return f'NewtonCotes {self.section:{i}} {self.npoints:{i}}'


@dataclasses.dataclass()
class FixedLocation(base.OpenSeesObject, Integration):
    """Integration at user-specified points.

    Parameters
    ----------
    sections : tuple
        Tuple of section tags.
    locations : tuple
        Tuple of locations, specified by factors on the element length.
    """
    sections: tuple
    locations: tuple

    def __post_init__(self):
        if len(self.sections) != len(self.locations):
            raise ValueError("FixedLocation: len(sections) must equal len(locations)")

    def tcl_code(self, **format_spec) -> str:
        fmt = self.get_format_spec(**format_spec)
        i, f = fmt.int, fmt.float
        return ' '.join([
            f'FixedLocation {len(self.sections):{i}}',
            *[f'{tag:{i}}' for tag in self.sections],
            *[f'{loc:{f}}' for loc in self.locations],
        ])
