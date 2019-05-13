"""Uniaxial material wrappers."""

import dataclasses

from . import base


@dataclasses.dataclass
class Elastic(base.OpenSeesObject):
    """Elastic uniaxial material.

    Wraps the OpenSees Tcl command Elastic:

        uniaxialMaterial Elastic $matTag $E <$eta> <$Eneg>

    Parameters
    ----------
    tag : int
        Integer tag identifying the material
    E : float
        Tangent/modulus of elasticity
    eta : float, optional
        Damping tangent (default = 0.0)
    Eneg : float, optional
        Tangent in compression (default = E)
    """
    tag: int
    E: float
    eta: float = 0.0
    Eneg: float = None

    def tcl_code(self) -> str:
        code = f"uniaxialMaterial Elastic {self.tag:d} {self.E:g}"

        if (self.Eneg is not None):
            code += f" {self.eta:g} {self.Eneg:g}"
        elif (self.eta != 0.0):
            code += f" {self.eta:g}"

        return code


@dataclasses.dataclass
class ElasticPP(base.OpenSeesObject):
    """Elastic-perfectly-plastic uniaxial material.

    Wraps the OpenSees Tcl command ElasticPP:

        uniaxialMaterial ElasticPP $matTag $E $epsyP <$epsyN $eps0>

    Parameters
    ----------
    tag : int
        Integer tag identifying the material
    E : float
        Tangent/modulus of elasticity
    eps_y : float
        Strain/deformation at which the material reaches plastic state in tension.
    eps_yN : float, optional
        Strain/deformation at which the material reaches plastic state in compression.
        (default = eps_y)
    eps0 : float, optional
        Initial strain/deformation. (default = 0.0)
    """
    tag: int
    E: float
    eps_y: float
    eps_yN: float = None
    eps0: float = 0.0

    def tcl_code(self) -> str:
        code = f"uniaxialMaterial ElasticPP {self.tag:d} {self.E:g} {self.eps_y:g}"

        eps_yN = self.eps_yN if self.eps_yN is not None else self.eps_y
        if self.eps0 != 0.0:
            code += f" {eps_yN:g} {self.eps0:g}"
        elif self.eps_yN is not None:
            code += f" {eps_yN:g}"

        return code


@dataclasses.dataclass
class Steel01(base.OpenSeesObject):
    """Bilinear steel model with optional isotropic hardening.

    Wraps the OpenSees Tcl command Steel01:

        uniaxialMaterial Steel01 $matTag $Fy $E0 $b <$a1 $a2 $a3 $a4>

    Parameters
    ----------
    tag : int
        Integer tag identifying the material.
    Fy : float
        Yield strength
    E : float
        Modulus of elasticity
    b : float
        Strain hardening ratio
    a1 : float, optional
        Isotropic hardening parameter; increase of compression yield envelope as
        proportion of yield strength after a plastic strain of a2*Fy/E0.
    a2 : float, optional
        Isotropic hardening parameter; see `a1`.
    a3 : float, optional
        Isotropic hardening parameter; increase of tension yield envelope as
        proportion of yield strength after a plastic strain of a4*Fy/E0.
    a4 : float, optional
        Isotropic hardening parameter; see `a3`.
    """
    tag: int
    Fy: float
    E: float
    b: float
    a1: float = None
    a2: float = None
    a3: float = None
    a4: float = None

    def _num_iso_params_defined(self):
        return sum([a is not None for a in (self.a1, self.a2, self.a3, self.a4)])

    def __post_init__(self):
        nparams = self._num_iso_params_defined()
        if nparams not in [0, 4]:
            raise ValueError('Steel01: isometric hardening definition incomplete ',
                             f'(expected 4 params, got {nparams})')

    def tcl_code(self):
        code = f'uniaxialMaterial Steel01 {self.tag:d} {self.Fy:g} {self.E0:g} {self.b:g}'
        if self._num_iso_params_defined() == 4:
            code += f' {self.a1:g} {self.a2:g} {self.a3:g} {self.a4:g}'

        return code


@dataclasses.dataclass
class Steel02(base.OpenSeesObject):
    """Giuffré-Menegotto-Pinto model with optional isotropic strain hardening.

    Wraps the OpenSees Tcl command Steel02:

        uniaxialMaterial Steel02 $matTag $Fy $E $b $R0 $cR1 $cR2 <$a1 $a2 $a3 $a4 $sigInit>

    Parameters
    ----------
    tag : int
        Integer tag identifying the material.
    Fy : float
        Yield strength
    E : float
        Modulus of elasticity
    b : float
        Strain hardening ratio
    R0 : float, optional
        Parameter that controls transition from elastic to plastic branches.
        Recommended value between 10 and 20. (default: 20)
    cR1 : float, optional
        Parameter that controls transition from elastic to plastic branches.
        Recommended value is 0.925. (default: 0.925)
    cR2 : float, optional
        Parameter that controls transition from elastic to plastic branches.
        Recommended value is 0.15. (default: 0.15)
    a1 : float, optional
        Isotropic hardening parameter; increase of compression yield envelope as
        proportion of yield strength after a plastic strain of a2*Fy/E0.
        (default: 0.0)
    a2 : float, optional
        Isotropic hardening parameter; see `a1`. (default: 1.0)
    a3 : float, optional
        Isotropic hardening parameter; increase of tension yield envelope as
        proportion of yield strength after a plastic strain of a4*Fy/E0.
        (default: 0.0)
    a4 : float, optional
        Isotropic hardening parameter; see `a3`. (default: 1.0)
    sigma_i : float, optional
        Initial stress. Initial strain is not zero; it is calculated from
        sigma_i/E. (default: 0.0)
    """
    tag: int
    Fy: float
    E: float
    b: float
    R0: float = 20
    cR1: float = 0.925
    cR2: float = 0.15
    a1: float = None
    a2: float = None
    a3: float = None
    a4: float = None
    sigma_i: float = None

    def _num_iso_params_defined(self):
        return sum([a is not None for a in (self.a1, self.a2, self.a3, self.a4)])

    def tcl_code(self):
        code = (
            f'uniaxialMaterial Steel02 {self.tag:d} {self.Fy:g} {self.E:g} '
            f'{self.b:g} {self.R0:g} {self.cR1:g} {self.cR2:g}'
        )

        n_iso_params = self._num_iso_params_defined()
        if self.sigma_i is not None:
            if n_iso_params == 0:
                code += f' 0.0 1.0 0.0 1.0 {self.sigma_i:g}'
            elif n_iso_params == 4:
                code += f' {self.a1:g} {self.a2:g} {self.a3:g} {self.a4:g} {self.sigma_i:g}'
        elif n_iso_params == 4:
            code += f' {self.a1:g} {self.a2:g} {self.a3:g} {self.a4:g}'

        return code
