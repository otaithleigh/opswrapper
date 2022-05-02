"""Uniaxial material wrappers."""

import dataclasses
import typing as t

from . import base


@dataclasses.dataclass
class UniaxialMaterial(base.OpenSeesObject):
    tag: int

    def tcl_code(self, formats=None) -> str:
        return 'uniaxialMaterial ' + ' '.join(self.tcl_args(formats))


#===================================================================================================
# Elastic-ish materials
#===================================================================================================
@dataclasses.dataclass
class Elastic(UniaxialMaterial):
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
    E: float
    eta: float = 0.0
    Eneg: float = None

    def tcl_args(self, formats=None) -> t.List[str]:
        args = ['Elastic', self.tag, self.E]
        if self.Eneg is not None:
            args.append(self.eta)
            args.append(self.Eneg)
        elif self.eta != 0.0:
            args.append(self.eta)

        return self.format_objects(args, formats)


@dataclasses.dataclass
class ElasticPP(UniaxialMaterial):
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
    E: float
    eps_y: float
    eps_yN: float = None
    eps0: float = 0.0

    def tcl_args(self, formats=None) -> t.List[str]:
        args = ['ElasticPP', self.tag, self.E, self.eps_y]
        eps_yN = self.eps_yN if self.eps_yN is not None else self.eps_y
        if self.eps0 != 0.0:
            args.append(eps_yN)
            args.append(self.eps0)
        elif self.eps_yN is not None:
            args.append(eps_yN)

        return self.format_objects(args, formats)


@dataclasses.dataclass
class Hardening(UniaxialMaterial):
    """Uniaxial material with combined linear kinematic and isotropic hardening.

    Wraps the OpenSees Tcl command Hardening:

        uniaxialMaterial Hardening $matTag $E $sigmaY $H_iso $H_kin <$eta>

    Parameters
    ----------
    tag : int
        Integer tag identifying the material.
    E : float
        Tangent stiffness/modulus of elasticity.
    sigma_y : float
        Yield stress/force
    h_iso : float
        Isotropic hardening modulus.
    h_kin : float
        Kinematic hardening modulus.
    eta : float, optional
        Visco-plastic coefficient. (default = 0.0)
    """
    E: float
    sigma_y: float
    h_iso: float
    h_kin: float
    eta: float = 0.0

    def tcl_args(self, formats=None) -> t.List[str]:
        args = [
            'Hardening',
            self.tag,
            self.E,
            self.sigma_y,
            self.h_iso,
            self.h_kin,
        ]
        if self.eta != 0.0:
            args.append(self.eta)

        return self.format_objects(args, formats)


#===================================================================================================
# Steels
#===================================================================================================
@dataclasses.dataclass
class Steel01(UniaxialMaterial):
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
        super().__post_init__()
        nparams = self._num_iso_params_defined()
        if nparams not in [0, 4]:
            raise ValueError('Steel01: isometric hardening definition incomplete '
                             f'(expected 4 params, got {nparams})')

    def tcl_args(self, formats=None) -> t.List[str]:
        args = ['Steel01', self.tag, self.Fy, self.E, self.b]
        if self._num_iso_params_defined() == 4:
            args.extend([self.a1, self.a2, self.a3, self.a4])

        return self.format_objects(args, formats)


@dataclasses.dataclass
class Steel02(UniaxialMaterial):
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

    def tcl_args(self, formats=None) -> t.List[str]:
        args = [
            'Steel02',
            self.tag,
            self.Fy,
            self.E,
            self.b,
            self.R0,
            self.cR1,
            self.cR2,
        ]

        n_iso_params = self._num_iso_params_defined()
        if self.sigma_i is not None:
            if n_iso_params == 0:
                args.extend([0.0, 1.0, 0.0, 1.0, self.sigma_i])
            elif n_iso_params == 4:
                args.extend([self.a1, self.a2, self.a3, self.a4, self.sigma_i])
        elif n_iso_params == 4:
            args.extend([self.a1, self.a2, self.a3, self.a4])

        return self.format_objects(args, formats)


#===================================================================================================
# Deterioration models
#===================================================================================================
@dataclasses.dataclass
class Bilin(UniaxialMaterial):
    """Deterioration model with bilinear hysteretic response.

    Parameters
    ----------
    tag : int
        Integer tag identifying the material.
    K0 : float
        Initial elastic stiffness.
    as_plus : float
        Strain hardening ratio for positive loading direction.
    as_neg : float
        Strain hardening ratio for negative loading direction.
    My_plus : float
        Effective yield strength for positive loading direction.
    My_neg : float
        Effective yield strength for negative loading direction. (negative value)
    lambda_s : float
        Cyclic deterioration parameter for strength deterioration: Et = lambda_s*My.
        Set to 0 to disable this mode of deterioration.
    lambda_c : float
        Cyclic deterioration parameter for post-capping strength deterioration:
        Et = lambda_c*My. Set to 0 to disable this mode of deterioration.
    lambda_a : float
        Cyclic deterioration parameter for acceleration reloading stiffness
        deterioration -- not a deterioration mode for a component with bilinear
        hysteretic response.
    lambda_k : float
        Cyclic deterioration parameter for unloading stiffness deterioration:
        Et = lambda_k*My. Set to 0 to disable this mode of deterioration.
    c_s : float
        Rate of strength deterioration.
    c_c : float
        Rate of post-capping strength deterioration.
    c_a : float
        Rate of accelerated reloading deterioration.
    c_k : float
        Rate of unloading stiffness deterioration.
    theta_p_plus : float
        Pre-capping rotation for positive loading direction.
    theta_p_neg : float
        Pre-capping rotation for negative loading direction. (positive value)
    theta_pc_plus : float
        Post-capping rotation for positive loading direction.
    theta_pc_neg : float
        Post-capping rotation for negative loading direction. (positive value)
    res_plus : float
        Residual strength ratio for positive loading direction.
    res_neg : float
        Residual strength ratio for negative loading direction. (positive value)
    theta_u_plus : float
        Ultimate rotation capacity for positive loading direction.
    theta_u_neg : float
        Ultimate rotation capacity for negative loading direction. (positive value)
    D_plus : float
        Rate of cyclic deterioration in the positive loading direction. This
        parameter is used to create asymmetric hysteretic behavior in the case
        of a composite beam. For symmetric hysteretic response use 1.0.
    D_neg : float
        Rate of cyclic deterioration in the negative loading direction. This
        parameter is used to create asymmetric hysteretic behavior in the case
        of a composite beam. For symmetric hysteretic response use 1.0.
    nfactor : float, optional
        Elastic stiffness amplification factor, mainly for use with concentrated
        plastic hinge elements. (default: 0.0)
    """
    K0: float
    as_plus: float
    as_neg: float
    My_plus: float
    My_neg: float
    lambda_s: float
    lambda_c: float
    lambda_a: float
    lambda_k: float
    c_s: float
    c_c: float
    c_a: float
    c_k: float
    theta_p_plus: float
    theta_p_neg: float
    theta_pc_plus: float
    theta_pc_neg: float
    res_plus: float
    res_neg: float
    theta_u_plus: float
    theta_u_neg: float
    D_plus: float = 1.0
    D_neg: float = 1.0
    nfactor: float = None

    def tcl_args(self, formats=None) -> t.List[str]:
        args = ['Bilin']
        args += [
            getattr(self, field.name) for field in dataclasses.fields(self)
            if field.name not in ('nfactor', )
        ]
        if self.nfactor is not None:
            args.append(self.nfactor)

        return self.format_objects(args, formats)
