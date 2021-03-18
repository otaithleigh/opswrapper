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

    def tcl_code(self, formats=None) -> str:
        args = [
            'element', 'elasticBeamColumn', self.tag, self.inode, self.jnode, self.A, self.E,
            self.Iz, self.transf
        ]
        if self.mass is not None:
            args.extend(['-mass', self.mass])
        if self.cmass:
            args.append('-cMass')
        return self.format_objects(args, formats)


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

    def tcl_code(self, formats=None) -> str:
        args = [
            'element', 'elasticBeamColumn', self.tag, self.inode, self.jnode, self.A, self.E,
            self.G, self.J, self.Iy, self.Iz, self.transf
        ]
        if self.mass is not None:
            args.extend(['-mass', self.mass])
        if self.cmass:
            args.append('-cMass')
        return self.format_objects(args, formats)


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

    def tcl_code(self, formats=None) -> str:
        args = ['element', 'forceBeamColumn', self.tag, self.inode, self.jnode, self.transf]
        if isinstance(self.integration, integration.Integration):
            integr = self.integration.tcl_code(formats)
        else:
            integr = str(self.integration)
        args.append(integr)
        if self.mass is not None:
            args.extend(['-mass', self.mass])
        if self.iterative:
            args.extend(['-iter', self.maxiters, self.itertol])
        return self.format_objects(args, formats)


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

    def tcl_code(self, formats=None) -> str:
        try:
            nsections = len(self.section)
            if nsections != self.npoints and nsections != 1:
                raise ValueError("DispBeamColumn: number of sections must be 1 or npoints")
            sections = self.section
        except TypeError:
            nsections = 1
            sections = [self.section]

        args = ['element', 'dispBeamColumn', self.tag, self.inode, self.jnode, self.npoints]
        if nsections == 1:
            args.append(self.section)
            args.append(self.transf)
        else:
            args.append('-sections')
            args.extend(sections)
            args.append(self.transf)
        if self.mass is not None:
            args.extend(['-mass', self.mass])
        if self.cmass:
            args.append('-cMass')
        if self.integration != 'Legendre':
            args.extend('-integration', self.integration)

        return self.format_objects(args, formats)


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
    corot : bool, optional
        If True, construct a corotTruss instead of a truss. (default: False)
    """
    tag: int
    inode: int
    jnode: int
    A: float
    mat: int
    rho: float = None
    cmass: bool = False
    do_rayleigh: bool = False
    corot: bool = False

    def tcl_code(self, formats=None) -> str:
        element = 'corotTruss' if self.corot else 'truss'
        args = ['element', element, self.tag, self.inode, self.jnode, self.A, self.mat]
        if self.rho is not None:
            args.extend(['-rho', self.rho])
        if self.cmass:
            args.extend(['-cMass', self.cmass])
        if self.do_rayleigh:
            args.extend(['-doRayleigh', self.do_rayleigh])
        return self.format_objects(args, formats)


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
    corot : bool, optional
        If True, construct a corotTruss instead of a truss. (default: False)
    """
    tag: int
    inode: int
    jnode: int
    section: int
    rho: float = None
    cmass: bool = False
    do_rayleigh: bool = False
    corot: bool = False

    def tcl_code(self, formats=None) -> str:
        element = 'corotTrussSection' if self.corot else 'trussSection'
        args = ['element', element, self.tag, self.inode, self.jnode, self.section]
        if self.rho is not None:
            args.extend(['-rho', self.rho])
        if self.cmass:
            args.extend(['-cMass', self.cmass])
        if self.do_rayleigh:
            args.extend(['-doRayleigh', self.do_rayleigh])
        return self.format_objects(args, formats)
