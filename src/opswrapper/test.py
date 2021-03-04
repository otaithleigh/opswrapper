import dataclasses

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


@dataclasses.dataclass
class Test(OpenSeesObject):
    tolerance: float
    max_iters: int
    print_flag: int = 0
    norm_type: int = 2

    def tcl_code(self, **format_spec) -> str:
        fmt = self.get_format_spec(**format_spec)
        i, f = fmt.int, fmt.float

        method = self.__class__.__name__
        return (
            f'test {method} {self.tolerance:{f}} {self.max_iters:{i}} '
            f'{self.print_flag:{i}} {self.norm_type:{i}}'
        )


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
    """


for subclass in Test.__subclasses__():
    subclass.__doc__ %= {'parameters': _standard_test_parameters}
