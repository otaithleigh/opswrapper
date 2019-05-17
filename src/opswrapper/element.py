import dataclasses

from . import base
from . import integration


@dataclasses.dataclass
class ElasticBeamColumn2D(base.OpenSeesObject):
    """Elastic beam column element for 2D analysis.

    Does not include shear deformations.

    Parameters
    ----------
    tag : int
        Unique integer tag for the element.
    inode : int
        Tag of the i node.
    jnode : int
        Tag of the j node.
    A : float
        Cross-sectional area of the element.
    E : float
        Elastic modulus.
    Iz : float
        Major-axis moment of inertia.
    transf : int
        Tag of the geometric transformation to use.
    mass : float, optional
        Mass-per-length of the element. (default: None)
    cmass : bool, optional
        If True, use a consistent mass matrix instead of a lumped mass matrix.
        (default: False)
    """
    tag: int
    inode: int
    jnode: int
    A: float
    E: float
    Iz: float
    transf: int
    mass: float = None
    cmass: bool = False

    def tcl_code(self):
        code = [
            f'element elasticBeamColumn {self.tag:d} {self.inode:d} {self.jnode:d} '
            f'{self.A:g} {self.E:g} {self.Iz:g} {self.transf:d}'
        ]
        if self.mass is not None:
            code.append(f'-mass {self.mass:g}')
        if self.cmass:
            code.append('-cMass')
        return ' '.join(code)


@dataclasses.dataclass
class ElasticBeamColumn3D(base.OpenSeesObject):
    tag: int
    inode: int
    jnode: int
    A: float
    E: float
    G: float
    J: float
    Iy: float
    Iz: float
    transf: int
    mass: float = None
    cmass: bool = False

    def tcl_code(self):
        code = [
            f'element elasticBeamColumn {self.tag:d} {self.inode:d} {self.jnode:d} '
            f'{self.A:g} {self.E:g} {self.G:g} {self.J:g} {self.Iy:g} {self.Iz:g} {self.transf:d}'
        ]
        if self.mass is not None:
            code.append(f'-mass {self.mass:g}')
        if self.cmass:
            code.append('-cMass')
        return ' '.join(code)


@dataclasses.dataclass
class ForceBeamColumn(base.OpenSeesObject):
    """Force-based beam column element.

    Parameters
    ----------
    tag : int
        Unique integer tag for the element.
    inode : int
        Tag of the i node.
    jnode : int
        Tag of the j node.
    transf : int
        Tag of the geometric transformation to use.
    integration : integration.Integration
        Integration method to use for the element.
    mass : float, optional
        Mass-per-length of the member. (default: None)
    iterative : bool, optional
        If True, use the iterative form of the element solution. (default: False)
    maxiters : int, optional
        Maximum iterations for the iterative form. (default: 10)
    itertol : float, optional
        Tolerance for the iterative form. (default: 1e-12)
    """
    tag: int
    inode: int
    jnode: int
    transf: int
    integration: integration.Integration
    mass: float = None
    iterative: bool = False
    maxiters: int = 10
    itertol: float = 1e-12

    def tcl_code(self):
        code = [
            f"element forceBeamColumn {self.tag:d} {self.inode:d} {self.jnode:d} {self.transf:d}"
        ]
        code.append(str(self.integration))
        if self.mass is not None:
            code.append(f'-mass {self.mass}')
        if self.iterative:
            code.append(f'-iter {self.maxiters} {self.itertol}')
        return ' '.join(code)


@dataclasses.dataclass
class DispBeamColumn(base.OpenSeesObject):
    """Displacement-based beam column element.

    Parameters
    ----------
    tag : int
        Unique integer tag for the element.
    inode : int
        Tag of the i node.
    jnode : int
        Tag of the j node.
    npoints : int
        Number of integration points.
    section : int, list
        Tag of the section for the element, or a list of `npoints` section tags.
    transf : int
        Tag of the geometric transformation to use.
    mass : float, optional
        Mass-per-length of the element. (default: None)
    cmass : bool, optional
        If True, use a consistent mass matrix instead of a lumped mass matrix.
        (default: False)
    integration : str, optional
        Integration method to use: 'Lobotto', 'Legendre', 'Radau', 'NewtonCotes',
        or 'Trapezoidal'. (default: 'Legendre')
    """
    tag: int
    inode: int
    jnode: int
    npoints: int
    section: int
    transf: int
    mass: float = None
    cmass: bool = False
    integration: str = 'Legendre'

    def tcl_code(self):
        try:
            nsections = len(self.section)
            if nsections != self.npoints and nsections != 1:
                raise ValueError("DispBeamColumn: number of sections must be 1 or npoints")
            sections = self.section
        except TypeError:
            nsections = 1
            sections = [self.section]

        code = [
            f'element dispBeamColumn {self.tag:d} {self.inode:d} {self.jnode:d} {self.npoints:d}',
        ]
        if nsections == 1:
            code.append(f'{self.section:d} {self.transf:d}')
        else:
            code.append(f'-sections')
            code.extend([f'{s:d}' for s in sections])
            code.append(f'{self.transf:d}')
        if self.mass is not None:
            code.append(f'-mass {self.mass:g}')
        if self.cmass:
            code.append('-cMass')
        if self.integration != 'Legendre':
            code.append(f'-integration {self.integration!s}')

        return ' '.join(code)


@dataclasses.dataclass
class Truss(base.OpenSeesObject):
    """Truss element.

    Parameters
    ----------
    tag : int
        Unique integer tag for the element.
    inode : int
        Tag of the i node.
    jnode : int
        Tag of the j node.
    A : float
        Cross-sectional area of the truss.
    mat : int
        Tag of the material for the truss.
    rho : float, optional
        Mass-per-length of the truss. (default: None)
    cmass : bool, optional
        If True, use a consistent mass matrix instead of lumped mass. (default: False)
    do_rayleigh : bool, optional
        If True, include Rayleigh damping for this element. (default: False)
    """
    tag : int
    inode : int
    jnode : int
    A : float
    mat : int
    rho : float = None
    cmass : bool = False
    do_rayleigh : bool = False

    def tcl_code(self):
        code = [f'element truss {self.tag:d} {self.inode:d} {self.jnode:d} {self.A:g} {self.mat:d}']
        if self.rho is not None:
            code.append(f'-rho {self.rho:g}')
        if self.cmass:
            code.append(f'-cMass {self.cmass:d}')
        if self.do_rayleigh:
            code.append(f'-doRayleigh {self.do_rayleigh:d}')
        return ' '.join(code)


@dataclasses.dataclass
class TrussSection(base.OpenSeesObject):
    """Truss element specified by a section.

    Parameters
    ----------
    tag : int
        Unique integer tag for the element.
    inode : int
        Tag of the i node.
    jnode : int
        Tag of the j node.
    section : int
        Tag of the section for the element.
    rho : float, optional
        Mass-per-length of the truss. (default: None)
    cmass : bool, optional
        If True, use a consistent mass matrix instead of lumped mass. (default: False)
    do_rayleigh : bool, optional
        If True, include Rayleigh damping for this element. (default: False)
    """
    tag : int
    inode : int
    jnode : int
    section : int
    rho : float = None
    cmass : bool = False
    do_rayleigh : bool = False

    def tcl_code(self):
        code = [f'element trussSection {self.tag:d} {self.inode:d} {self.jnode:d} {self.section:d}']
        if self.rho is not None:
            code.append(f'-rho {self.rho:g}')
        if self.cmass:
            code.append(f'-cMass {self.cmass:d}')
        if self.do_rayleigh:
            code.append(f'-doRayleigh {self.do_rayleigh:d}')
        return ' '.join(code)
