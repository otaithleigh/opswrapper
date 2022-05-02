import dataclasses
import typing as t

from .base import OpenSeesObject

__all__ = [
    'ArcLength',
    'CentralDifference',
    'DisplacementControl',
    'HHT',
    'Integrator',
    'LoadControl',
    'MinUnbalDispNorm',
    'Newmark',
    'StaticIntegrator',
    'TransientIntegrator',
]


class Integrator(OpenSeesObject):
    def tcl_code(self, formats=None) -> str:
        return ' '.join(['integrator', *self.tcl_args(formats)])


#===================================================================================================
# Static integrators
#===================================================================================================
class StaticIntegrator(Integrator):
    pass


@dataclasses.dataclass
class LoadControl(StaticIntegrator):
    """
    Parameters
    ----------
    incr : float
        The load factor increment, λ.
    num_iters : int, optional
        The number of iterations the user would like to occur in the solution
        algorithm. (default: 1)
    min_incr : float, optional
        The minimum load increment, λ, the user will allow. (default: `λ`)
    max_incr : float, optional
        The maximum load increment, λ, the user will allow. (default: `λ`)

    Notes
    -----
    1. The change in applied loads that this causes depends on the active load
       patterns (i.e., those load patterns not set constant) and the loads in
       the load patterns. If the only active loads acting on the domain are in
       load patterns with a Linear time series with a factor of 1.0, this
       integrator is the same as the classical load control method.
    2. The optional arguments are supplied to speed up the step size in cases
       where convergence is too fast and slow down the step size in cases where
       convergence is too slow.
    """
    incr: float
    num_iters: int = 1
    min_incr: float = None
    max_incr: float = None

    def tcl_args(self, formats=None) -> t.List[str]:
        min_incr = self.incr if self.min_incr is None else self.min_incr
        max_incr = self.incr if self.max_incr is None else self.max_incr
        args = ['LoadControl', self.incr, self.num_iters, min_incr, max_incr]
        return self.format_objects(args, formats)


@dataclasses.dataclass
class DisplacementControl(StaticIntegrator):
    """
    Parameters
    ----------
    node : int
        Node whose response controls the solution.
    dof : int
        Degree of freedom at `node` to get response from. Valid options are in
        the range [1, NDF].
    incr : float
        The first displacement increment.
    num_iters : int, optional
        The number of iterations the user would like to occur in the solution
        algorithm. (default: 1)
    min_incr : float, optional
        The minimum step size to allow. (default: `incr`)
    max_incr : float, optional
        The maximum step size to allow. (default: `incr`)
    """
    node: int
    dof: int
    incr: float
    num_iters: int = 1
    min_incr: float = None
    max_incr: float = None

    def tcl_args(self, formats=None) -> t.List[str]:
        min_incr = self.incr if self.min_incr is None else self.min_incr
        max_incr = self.incr if self.max_incr is None else self.max_incr
        args = [
            'DisplacementControl',
            self.node,
            self.dof,
            self.incr,
            self.num_iters,
            min_incr,
            max_incr,
        ]
        return self.format_objects(args, formats)


@dataclasses.dataclass
class MinUnbalDispNorm(StaticIntegrator):
    """Static integrator using the minimum unbalanced displacement norm scheme.

    The load increment at iteration i, dλ_i, is related to the load increment at
    i - 1, dλ_(i - 1), and the number of iterations at i - 1, J_(i - 1), by::

        dλ_i = dλ_(i - 1) * Jd / J_(i - 1)

    Parameters
    ----------
    incr : float
        First load increment (pseudo-time step) at the first iteration in the
        next invocation of the analyze command.
    Jd : float, optional
        Factor relating first load increment at subsequent time steps.
        (default: 1.0)
    min_incr : float, optional
        Minimum load increment. (default: `incr`)
    max_incr : float, optional
        Maximum load increment. (default: `incr`)
    """
    incr: float
    Jd: float = 1.0
    min_incr: float = None
    max_incr: float = None

    def tcl_args(self, formats=None) -> t.List[str]:
        min_incr = self.incr if self.min_incr is None else self.min_incr
        max_incr = self.incr if self.max_incr is None else self.max_incr
        args = ['MinUnbalDispNorm', self.incr, self.Jd, min_incr, max_incr]
        return self.format_objects(args, formats)


@dataclasses.dataclass
class ArcLength(StaticIntegrator):
    """Static integrator using the arc length scheme.

    Within a load step, the following constraint is enforced::

        dU^T dU + α^2 dΛ^2 = s^2

    where dU is the change in nodal displacements for the step, dΛ is the change
    in applied load, and s is a control parameter (the arc length).

    Parameters
    ----------
    s : float
        Arc length.
    alpha : float
        Scaling factor on the reference loads.
    """
    s: float
    alpha: float

    def tcl_args(self, formats=None) -> t.List[str]:
        return self.format_objects(['ArcLength', self.s, self.alpha], formats)


#===================================================================================================
# Transient integrators
#===================================================================================================
class TransientIntegrator(Integrator):
    pass


@dataclasses.dataclass
class CentralDifference(TransientIntegrator):
    """Explicit integration by the central difference method.

    Notes
    -----
    1. As an explicit integration method, the calculation of U_(t + Δt) is based
       on the equilibrium equation at time t.
    2. If there is no Rayleigh damping and the C matrix is 0, for a diagonal
       mass matrix a diagonal solver can (and should) be used.
    3. For stability, Δt/Tn < 1/π.
    """
    def tcl_args(self, formats) -> t.List[str]:
        return ['CentralDifference']


@dataclasses.dataclass
class Newmark(TransientIntegrator):
    """Newmark integration.

    Parameters
    ----------
    gamma : float
        Newmark factor γ
    beta : float
        Newmark factor β

    Notes
    -----
    1. If the accelerations are chosen as the unknowns and β is chosen as 0, the
       formulation results in the fast but conditionally stable explicit Central
       Difference method. Otherwise the method is implicit and requires an
       iterative solution process.
    2. Two common sets of choices are
       - Average Acceleration Method (γ = 1/2, β = 1/4)
       - Linear Acceleration Method (γ = 1/2, β = 1/6)
    3. γ > 1/2 results in numerical damping proportional to γ - 1/2
    4. The method is second order accurate if and only if γ = 1/2
    5. The method is conditionally stable for β >= γ/2 >= 1/4
    """
    gamma: float
    beta: float

    def tcl_args(self, formats=None) -> t.List[str]:
        return self.format_objects(['Newmark', self.gamma, self.beta], formats)


@dataclasses.dataclass
class HHT(TransientIntegrator):
    """Hilber-Hughes-Taylor integrator.

    HHT is a one-step implicit method that allows for energy dissipation and
    second-order accuracy, which is not possible with the regular Newmark
    method. Depending on the choice of input parameters, the method can be
    unconditionally stable. HHT attempts to increase the amount of numerical
    damping present without degrading the order of accuracy.

    Parameters
    ----------
    alpha : float
        HHT factor α
    gamma : float, optional
        HHT factor γ. (default: (2 - α)**2 / 4)
    beta : float, optional
        HHT factor β. (default: 3/2 - α)

    Notes
    -----
    1. α = 1.0 corresponds to the Newmark method.
    2. α should be between 2/3 and 1.0. The smaller the α, the greater the
       numerical damping.
    3. The default values for γ and β ensure the method is second-order accurate
       and unconditionally stable when α is between 2/3 and 1.
    """
    alpha: float
    gamma: float = None
    beta: float = None

    @property
    def default_gamma(self):
        return 0.25*(2 - self.alpha)**2

    @property
    def default_beta(self):
        return 1.5 - self.alpha

    def tcl_args(self, formats=None) -> t.List[str]:
        args = ['HHT', self.alpha]
        if self.gamma is not None or self.beta is not None:
            # OpenSees wants gamma and beta both specified if either is not default
            args.append(self.gamma if self.gamma is not None else self.default_gamma)
            args.append(self.beta if self.beta is not None else self.default_beta)

        return self.format_objects(args, formats)
