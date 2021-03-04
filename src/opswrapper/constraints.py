import dataclasses

from .base import OpenSeesObject


@dataclasses.dataclass
class Plain(OpenSeesObject):
    """Plain constraint handler.

    Only supports constraints applied using the 'fix' and 'equalDOF' commands.
    """
    def tcl_code(self, **format_spec) -> str:
        return 'constraints Plain'


@dataclasses.dataclass
class Transformation(OpenSeesObject):
    """Constraints enforcement by the transformation method.

    Notes
    -----
    The single-point constraints when using the transformation method are done
    directly. The matrix equation is not manipulated to enforce them, rather the
    trial displacements are set directly at the nodes at the start of each
    analysis step.

    Great care must be taken when multiple constraints are being enforced as the
    transformation method does not follow constraints:

    1. If a node is fixed, constrain it with the 'fix' command and 'equalDOF' or
       other type of constraint.
    2. If multiple nodes are constrained, make sure that the retained node is
       not constrained in any other constraint.
    """
    def tcl_code(self, **format_spec) -> str:
        return 'constraints Transformation'


@dataclasses.dataclass
class Lagrange(OpenSeesObject):
    """Constraints enforcement using Lagrange multipliers.

    Parameters
    ----------
    alpha_s : float
        Multiplier for single-point constraints.
    alpha_m : float
        Multiplier for multi-point constraints.

    Notes
    -----
    The Lagrange multiplier method introduces new unknowns to the system of
    equations. The diagonal part of the system corresponding to these new
    unknowns is 0.0. This ensures that the system IS NOT symmetric positive
    definite.
    """
    alpha_s: float
    alpha_m: float

    def tcl_code(self, **format_spec) -> str:
        f = self.get_format_spec(**format_spec).float
        return f'constraints Lagrange {self.alpha_s:{f}} {self.alpha_m:{f}}'


@dataclasses.dataclass
class Penalty(OpenSeesObject):
    """Constraints enforcement using the penalty method.

    Parameters
    ----------
    alpha_s : float
        Penalty for single-point constraints.
    alpha_m : float
        Penalty for multi-point constraints.

    Notes
    -----
    The degree to which the constraints are enforced is dependent on the penalty
    values chosen. Problems can arise if these values are too small (constraint
    not enforced strongly enough) or too large (problems associated with
    conditioning of the system of equations).
    """
    alpha_s: float
    alpha_m: float

    def tcl_code(self, **format_spec) -> str:
        f = self.get_format_spec(**format_spec).float
        return f'constraints Penalty {self.alpha_s:{f}} {self.alpha_m:{f}}'
