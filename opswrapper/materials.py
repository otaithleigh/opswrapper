"""Uniaxial material wrappers."""

from __future__ import annotations

import dataclasses

from . import base


@dataclasses.dataclass
class Elastic(base.OpenSeesObject):
    """Elastic uniaxial material.
    
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

    def tcl_code(self, fid=None) -> str:
        code = f"uniaxialMaterial ElasticPP {self.tag:d} {self.E:g} {self.eps_y:g}"

        eps_yN = self.eps_yN if self.eps_yN is not None else self.eps_y
        if self.eps0 != 0.0:
            code += f" {eps_yN:g} {self.eps0:g}"
        elif self.eps_yN is not None:
            code += f" {eps_yN:g}"

        return code
