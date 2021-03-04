"""Wrappers for Tcl OpenSees analyses."""
import importlib.resources

from . import analysis
from . import base
from . import element
from . import formatting
from . import integration
from . import material
from . import output
from . import section
from .base import *
from .formatting import *
from .model import *

__version__ = importlib.resources.read_text(__name__, '__version__')
