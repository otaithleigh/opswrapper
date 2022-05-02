import dataclasses
import typing as t
from enum import IntEnum

from .base import OpenSeesObject

# Most of the test commands share the same signature. Document parameters here
# to reduce repetition.
_standard_test_parameters = """Parameters
    ----------
    tolerance : float
        The tolerance criteria used to check for convergence.
    max_iters : int
        The maximum number of iterations to check before returning failure
        condition.
    print_flag : int, optional
        Print flag (default: 0). Valid options:
        - 0: print nothing
        - 1: print information on norms each time `test()` is invoked
        - 2: print information on norms and number of iterations at end of
             successful test
        - 4: print norms at each step and also the ΔU and R(U) vectors.
        - 5: if test fails to converge after `max_iters`, print an error message
             BUT RETURN A SUCCESSFUL TEST.
    norm_type : int, optional
        Type of norm. 0 = max-norm, 1 = 1-norm, 2 = 2-norm, etc. (default: 2)"""


class PrintFlag(IntEnum):
    """Print flag for convergence tests.
    
    Options
    -------
    - 0: print nothing
    - 1: print information on norms each time `test()` is invoked
    - 2: print information on norms and number of iterations at end of
         successful test
    - 4: print norms at each step and also the ΔU and R(U) vectors.
    - 5: if test fails to converge after `max_iters`, print an error message
         BUT RETURN A SUCCESSFUL TEST.
    """
    NOTHING = 0
    NORMS = 1
    NORMS_AND_ITERS = 2
    NORMS_AND_VECS = 4
    IGNORE_ERROR = 5


@dataclasses.dataclass
class Test(OpenSeesObject):
    tolerance: float
    max_iters: int
    print_flag: int = PrintFlag.NOTHING
    norm_type: int = 2

    def tcl_code(self, formats=None) -> str:
        return ' '.join(['test', *self.tcl_args(formats=formats)])

    def tcl_args(self, formats=None) -> t.List[str]:
        method = self.__class__.__name__
        print_flag = PrintFlag(self.print_flag)
        args = [method, self.tolerance, self.max_iters, print_flag, self.norm_type]
        return self.format_objects(args, formats)


@dataclasses.dataclass
class NormUnbalance(Test):
    """Convergence test which uses the norm of the right-hand side of the matrix
    equation to determine if convergence has been reached.

    What the right-hand side of the matrix equation is depends on the chosen
    integrator and constraint handler. Usually, though not always, it is equal
    to the unbalanced forces in the system.

    %(parameters)s

    Notes
    -----
    When using the Penalty method additional large forces to enforce the penalty
    functions exist on the right hand side, making convergence using this test
    usually impossible (even though solution might have converged).

    Theory
    ------
    If the system of equations formed by the integrator is::

        K ΔUi = R(Ui)

    This integrator is testing::

        ||R(Ui)|| < tol
    """


@dataclasses.dataclass
class NormDispIncr(Test):
    """Convergence test which uses the norm of the left-hand side solution
    vector of the matrix equation to determine if convergence has been reached.

    What the solution vector of the matrix equation is depends on the chosen
    integrator and constraint handler. Usually, though not always, it is equal
    to the displacement increments that are to be applied to the model.

    %(parameters)s

    Notes
    -----
    When using the Lagrange method to enforce the constraints, the Lagrange
    multipliers appear in the solution vector.

    Theory
    ------
    If the system of equations formed by the integrator is::

        K ΔUi = R(Ui)

    This integrator is testing::

        ||ΔUi|| < tol
    """


@dataclasses.dataclass
class EnergyIncr(Test):
    """Convergence test which uses the dot product of the solution vector and
    norm of the right hand side of the matrix equation to determine if
    convergence has been reached.

    The physical meaning of this quantity depends on the chosen integrator and
    constraint handler. Usually, though not always, it is equal to the energy
    unbalance in the system.

    %(parameters)s

    Notes
    -----
    1. When using the Penalty method additional large forces to enforce the
       penalty functions exist on the right hand side, making convergence using
       this test usually impossible (even though solution might have converged).
    2. When Lagrange multipliers are used, the solution vector contains the
       Lagrange multipliers.

    Theory
    ------
    If the system of equations formed by the integrator is::

        K ΔUi = R(Ui)

    This integrator is testing::

        ΔUi * R(Ui) < tol
    """


@dataclasses.dataclass
class RelativeNormUnbalance(Test):
    """Convergence test which uses the relative norm of the right-hand side of
    the matrix equation to determine if convergence has been reached.

    What the right-hand side of the matrix equation is depends on the chosen
    integrator and constraint handler. Usually, though not always, it is equal
    to the unbalanced forces in the system.

    %(parameters)s

    Notes
    -----
    1. When using the Penalty method additional large forces to enforce the
       penalty functions exist on the right hand side, making convergence using
       this test usually impossible (even though solution might have converged).
    2. ||R(U0)|| is the initial unbalance seen by the system when
       ``solveCurrentStep()`` is invoked on the algorithm.
    3. Sometimes there may be problems converging if ||R(U0)|| is very small to
       begin with.

    Theory
    ------
    If the system of equations formed by the integrator is::

        K ΔUi = R(Ui)

    This integrator is testing::

        ||R(Ui)|| / ||R(U0)|| < tol
    """


@dataclasses.dataclass
class RelativeNormDispIncr(Test):
    """Convergence test which uses the relative norm of the left-hand side
    solution vector of the matrix equation to determine if convergence has been
    reached.

    What the solution vector of the matrix equation is depends on the chosen
    integrator and constraint handler. Usually, though not always, it is equal
    to the displacement increments that are to be applied to the model.

    %(parameters)s

    Notes
    -----
    1. When using the Lagrange method to enforce the constraints, the Lagrange
       multipliers appear in the solution vector, making convergence using this
       test usually impossible (even though solution might have converged).
    2. ||ΔU0|| is the initial solution when ``solveCurrentStep()`` is invoked on
       the algorithm.
    3. Sometimes there may be problems converging if ||ΔU0|| is very small to
       begin with.

    Theory
    ------
    If the system of equations formed by the integrator is::

        K ΔUi = R(Ui)

    This integrator is testing::

        ||ΔUi|| / ||ΔU0|| < tol
    """


@dataclasses.dataclass
class TotalRelativeNormDispIncr(Test):
    """Convergence test which uses the ratio of the current norm to the total
    norm (the sum of all the norms since last convergence) of the solution
    vector of the matrix equation to determine if convergence has been reached.

    What the solution vector of the matrix equation is depends on the chosen
    integrator and constraint handler. Usually, though not always, it is equal
    to the displacement increments that are to be applied to the model.

    %(parameters)s

    Notes
    -----
    1. When using the Lagrange method to enforce the constraints, the Lagrange
       multipliers appear in the solution vector, making convergence using this
       test usually impossible (even though solution might have converged).

    Theory
    ------
    If the system of equations formed by the integrator is::

        K ΔUi = R(Ui)

    This integrator is testing::

        ||ΔUi|| / ||ΔU0 + ΔU1 + ΔU2 + ... + ΔUi|| < tol
    """


@dataclasses.dataclass
class RelativeEnergyIncr(Test):
    """Convergence test which uses the dot product of the solution vector and
    norm of the right hand side of the matrix equation to determine if
    convergence has been reached.

    The physical meaning of this quantity depends on the chosen integrator and
    constraint handler. Usually, though not always, it is equal to the energy
    unbalance in the system.

    %(parameters)s

    Notes
    -----
    1. When using the Penalty method additional large forces to enforce the
       penalty functions exist on the right hand side, making convergence using
       this test usually impossible (even though solution might have converged).
    2. When Lagrange multipliers are used, the solution vector contains the
       Lagrange multipliers.

    Theory
    ------
    If the system of equations formed by the integrator is::

        K ΔUi = R(Ui)

    This integrator is testing::

        [ΔUi * R(Ui)] / [ΔU0 * R(U0)] < tol
    """


for subclass in Test.__subclasses__():
    subclass.__doc__ %= {'parameters': _standard_test_parameters}
