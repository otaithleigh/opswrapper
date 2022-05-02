import dataclasses
import typing as t

from .base import OpenSeesObject
from .utils import ValueTypeDispatch

__all__ = [
    'Algorithm',
    'BFGS',
    'Broyden',
    'KrylovNewton',
    'Linear',
    'ModifiedNewton',
    'Newton',
    'NewtonLineSearch',
    'SecantNewton',
]


class Algorithm(OpenSeesObject):
    _tangent_flag_dispatch: t.ClassVar[ValueTypeDispatch[str, t.Union[str, None]]]

    def __init_subclass__(cls, tangent_dispatch: t.Optional[dict] = None, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if tangent_dispatch is not None:
            cls._tangent_flag_dispatch = ValueTypeDispatch('tangent', tangent_dispatch)

    def tcl_code(self, formats=None) -> str:
        return ' '.join(['algorithm', *self.tcl_args(formats)])

    # The only option to most algorithm commands is the tangent type, handled
    # here by `_tangent_flag_dispatch`. Since these are just str, they don't
    # need to go through `format_objects`.

    def tcl_args(self, formats=None) -> t.List[str]:
        args = [self.__class__.__name__]
        tangent_flag = self._tangent_flag_dispatch[self.tangent]
        if tangent_flag is not None:
            args.append(tangent_flag)

        return args


#===================================================================================================
# Classical methods
#===================================================================================================
@dataclasses.dataclass
class Linear(
    Algorithm,
    tangent_dispatch={
        'current': None,
        'initial': '-initial',
        'secant': '-secant',
    },
):
    """Linear algorithm which takes one iteration to solve the system of
    equations::

        ΔU = K^-1 R(U)

    Parameters
    ----------
    tangent : {'current', 'initial', 'secant'}
        Which stiffness to use for iterating. (default: 'current')
    factor_once : bool, optional
        If True, only set up and factor the matrix once. (default: False)
    """
    tangent: str = 'current'
    factor_once: bool = False

    def tcl_args(self, formats=None) -> t.List[str]:
        args = super().tcl_args(formats)
        if self.factor_once:
            args.append('-factorOnce')
        return args


@dataclasses.dataclass
class Newton(
    Algorithm,
    tangent_dispatch={
        'current': None,
        'initial': '-initial',
        'initialThenCurrent': '-intialThenCurrent',  # Not a typo
        'secant': '-secant',
        'hall': '-hall',
    },
):
    """Newton-Raphson method for solving the nonlinear residual equation.

    Parameters
    ----------
    tangent : {'current', 'initial', 'initialThenCurrent', 'secant', 'hall'}
        Which stiffness to use for iterating. (default: 'current')
    """
    tangent: str = 'current'


@dataclasses.dataclass
class ModifiedNewton(
    Algorithm,
    tangent_dispatch={
        'current': None,
        'initial': '-initial',
        'secant': '-secant',
        'hall': '-hall',
    },
):
    """Modified Newton-Raphson method for solving the nonlinear residual
    equation.

    Parameters
    ----------
    tangent : {'current', 'initial', 'secant', 'hall'}
        Which stiffness to use for iterating. (default: 'current')
    """
    tangent: str = 'current'


#===================================================================================================
# Line search methods
#===================================================================================================
@dataclasses.dataclass
class NewtonLineSearch(Algorithm):
    """Newton-Raphson algorithm with line search, which increases the
    effectiveness when convergence is slow due to roughness of the residual.

    Parameters
    ----------
    type_search : {'Bisection', 'Secant', 'RegulaFalsi', 'InitialInterpolated'}
        Line search algorithm. (default: 'InitialInterpolated')
    tol : float, optional
        Tolerance for search. (default: 0.8)
    max_iters : int, optional
        Maximum number of iterations for search. (default: 10)
    min_eta : float, optional
        Minimum η value. (default: 0.1)
    max_eta : float, optional
        Maximum η value. (default: 10.0)

    Theory
    ------
    The rationale behind line search is that:

    - the direction ΔU found by the Newton-Raphson method is often a good
      direction, but the step size ||ΔU|| is not, and
    - it is cheaper to compute the residual for several points along ΔU rather
      than form and factor a new system Jacobian.

    In NewtonLineSearch, the regular Newton-Raphson method is used to compute
    ΔU, but the update is modified::

        U_n1 = U_n + η ΔU

    The different line search algorithms use different root finding algorithms
    to obtain η, a root to the function s(η) defined as::

        s(η) = ΔU R(U_n + η ΔU)
    """
    type_search: str = 'InitialInterpolated'
    tol: float = 0.8
    max_iters: int = 10
    min_eta: float = 0.1
    max_eta: float = 10.0

    _line_search_type_dispatch = ValueTypeDispatch(
        'line search',
        {
            'Bisection': 'Bisection',
            'Secant': 'Secant',
            'RegulaFalsi': 'RegulaFalsi',
            'InitialInterpolated': 'InitialInterpolated'
        },
    )

    def tcl_args(self, formats=None) -> t.List[str]:
        args = [
            'NewtonLineSearch',
            '-typeSearch',
            self._line_search_type_dispatch[self.type_search],
            '-tol',
            self.tol,
            '-maxIter',
            self.max_iters,
            '-minEta',
            self.min_eta,
            '-maxEta',
            self.max_eta,
        ]
        return self.format_objects(args, formats)


#===================================================================================================
# Accelerated Newton methods
#===================================================================================================
@dataclasses.dataclass
class _AcceleratedNewton(
    Algorithm,
    tangent_dispatch={
        'current': 'current',
        'initial': 'initial',
        'noTangent': 'noTangent',
    },
):
    """Modified Newton method with accelerator.

    Parameters
    ----------
    iterate : {'current', 'initial', 'noTangent'}, optional
        Tangent to iterate on. (default: 'current')
    increment : {'current', 'initial', 'noTangent'}, optional
        Tangent to increment on. (default: 'current')
    max_dim: int, optional
        Maximum number of iterations until the tangent is reformed and the
        acceleration restarts. (default: 3)
    """
    iterate: str = 'current'
    increment: str = 'current'
    max_dim: int = 3

    def tcl_args(self, formats=None) -> t.List[str]:
        args = [self.__class__.__name__]
        tangent_iter = self._tangent_flag_dispatch[self.iterate]
        tangent_incr = self._tangent_flag_dispatch[self.increment]

        args.extend(['-iterate', tangent_iter])
        args.extend(['-increment', tangent_incr])
        args.extend(['-maxDim', *self.format_objects([self.max_dim], formats)])

        return args


@dataclasses.dataclass
class KrylovNewton(_AcceleratedNewton):
    """Modified Newton method with Krylov subspace accelerator.

    Parameters
    ----------
    iterate : {'current', 'initial', 'noTangent'}, optional
        Tangent to iterate on. (default: 'current')
    increment : {'current', 'initial', 'noTangent'}, optional
        Tangent to increment on. (default: 'current')
    max_dim: int, optional
        Maximum number of iterations until the tangent is reformed and the
        acceleration restarts. (default: 3)
    """


@dataclasses.dataclass
class SecantNewton(_AcceleratedNewton):
    """Modified Newton method with two-term update to accelerate convergence.

    Parameters
    ----------
    iterate : {'current', 'initial', 'noTangent'}, optional
        Tangent to iterate on. (default: 'current')
    increment : {'current', 'initial', 'noTangent'}, optional
        Tangent to increment on. (default: 'current')
    max_dim: int, optional
        Maximum number of iterations until the tangent is reformed and the
        acceleration restarts. (default: 3)
    """


# TODO: These are undocumented, but present in OpenSeesCommands.cpp
#
# @dataclasses.dataclass
# class RaphsonNewton(_AcceleratedNewton):
#     pass
#
#
# @dataclasses.dataclass
# class MillerNewton(_AcceleratedNewton):
#     pass
#
#
# @dataclasses.dataclass
# class PeriodicNewton(_AcceleratedNewton):
#     pass


#===================================================================================================
# Broyden-type algorithms
#===================================================================================================
@dataclasses.dataclass
class _Broyden(
    Algorithm,
    tangent_dispatch={
        'current': None,
        'initial': '-initial',
        'secant': '-secant',
    },
):
    tangent: str = 'current'
    count: int = 10

    def tcl_args(self, formats=None) -> t.List[str]:
        args = super().tcl_args(formats)
        args.extend(self.format_objects(['-count', self.count], formats))
        return args


@dataclasses.dataclass
class Broyden(_Broyden):
    """Broyden algorithm for general unsymmetric systems.

    Parameters
    ----------
    tangent : {'current', 'initial', 'secant'}
        Which stiffness to use for iterating. (default: 'current')
    count : int, optional
        Number of iterations within a time step until a new tangent is formed.
        (default: 10)
    """


@dataclasses.dataclass
class BFGS(_Broyden):
    """Broyden-Fletcher-Goldfarb-Shanno (BFGS) algorithm.

    Parameters
    ----------
    tangent : {'current', 'initial', 'secant'}
        Which stiffness to use for iterating. (default: 'current')
    count : int, optional
        Number of iterations within a time step until a new tangent is formed.
        (default: 10)
    """
