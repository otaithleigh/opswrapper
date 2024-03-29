import dataclasses
import numbers
import types
from pathlib import Path
from typing import Callable, Generic, Iterable, Mapping, TypeVar

import numpy as np


def coerce_numeric(obj, to_type: type):
    """Gently attempt to coerce between numeric types."""
    # If to_type is a parameterized generic, issubclass() freaks out
    # in an unhelpful way. isinstance(to_type, type) returns True,
    # so I guess the only thing to do is check if to_type has
    # annotations.
    if hasattr(to_type, "__args__"):
        return obj

    # Only try to coerce *to* numbers
    if not issubclass(to_type, numbers.Number):
        return obj

    # Only try to coerce *from* numbers
    if not isinstance(obj, numbers.Number):
        return obj

    # If coercion doesn't work, just return the original object.
    try:
        coerced = to_type(obj)
    except Exception:
        return obj

    return coerced


class Namespace(types.SimpleNamespace):
    """Extension of the SimpleNamespace class to make it more dict-like.

    Examples
    --------
    Iterating over name-value pairs (a la dict.items):

    >>> files = Namespace()
    >>> files.input = 'input.tcl'
    >>> files.output = 'output.dat'
    >>> for name, path in files:
    ...     print(name, ':', path)
    input : input.tcl
    output : output.dat

    Programmatic get and set access:

    >>> files['input']
    'input.tcl'
    >>> files['output'] = 'output.csv'
    >>> files.output
    'output.csv'
    """

    def __iter__(self):
        return iter(self.__dict__.items())

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __delitem__(self, key):
        delattr(self, key)


def path_for_tcl(path) -> str:
    return Path(path).as_posix()


def print_model(model: Iterable[str], file=None):
    """Print a model definition to a file.

    Parameters
    ----------
    model : list
        List of strings and/or OpenSeesObjects that define a model and/or its
        analysis routine.
    file : file-like, optional
        Name of a file or an open file descriptor. If None, print to stdout.
        (default: None)
    """
    try:
        file = Path(file)
        file_is_descriptor = False
    except TypeError:
        file_is_descriptor = True

    modeltext = "\n".join(str(line) for line in model)
    if file_is_descriptor:
        print(modeltext, file=file)
    else:
        with open(file, "w") as f:
            print(modeltext, file=f)


def tclescape(text: str) -> str:
    """Escape a string for use as a literal in Tcl."""
    # Based on:
    # - https://stackoverflow.com/a/27086669 (fast Python algorithms for doing this)
    # - https://stackoverflow.com/a/70082148 (which characters actually need escaping?)
    chars = R'\[$"'
    for c in chars:
        if c in text:
            text = text.replace(c, "\\" + c)
    return f'"{text}"'


def tcllist(it: Iterable[object], stringify: Callable[[object], str] = str) -> str:
    R"""Generate code for a Tcl list.

    All elements in the list are escaped and will not support commands
    or variable substitution. Do that on the Python side.

    Parameters
    ----------
    it : iterable
        Iterable to convert to Tcl list.
    stringify : (object) -> str
        Function called to convert the objects to ``str`` before being escaped.
        (default: ``str``)

    Example
    -------
    >>> tcllist([1.0, 2, "sam's the best!", "[this_wont_run]", "$no_substitutes"])
    '[list "1.0" "2" "sam\'s the best!" "\\[this_wont_run]" "\\$no_substitutes"]'
    """
    return f"[list {' '.join(tclescape(stringify(i)) for i in it)}]"


def list_dataclass_fields(name, object, pad="", end="\n", exclude=None) -> str:
    """Represent the fields of a dataclass object.

    Parameters
    ----------
    name : str
        The name to use for the object in the representation.
    object : dataclass
        Object to describe.
    pad : str, optional
        String to pad the left side with. (default: '')
    end : str, optional
        String to end each entry with. (default: '\\n')
    exclude : list[str], optional
        Field names to exclude. (default: None)

    Example
    -------
    >>> print(list_dataclass_fields('gravity_columns', self.gravity_columns, pad=' '*8))
            gravity_columns.include          : True
            gravity_columns.num_points       : 4
            gravity_columns.material_model   : Steel01
            gravity_columns.strain_hardening : 0.01
    """
    fields = dataclasses.fields(object)
    max_key_len = max(len(f.name) for f in fields)
    return end.join(
        f"{pad}{name}.{field.name.ljust(max_key_len)} : {getattr(object, field.name)!r}"
        for field in fields
        if exclude is None or field.name not in exclude
    )


def fill_out_numbers(peaks, rate):
    """Fill in numbers between peaks.

    Parameters
    ----------
    peaks : array-like
        Peaks to fill between.
    rate : float
        Rate to use between peaks.

    Examples
    --------
    >>> fill_out_numbers([0, 1, -1], rate=0.25)
    array([ 0.  ,  0.25,  0.5 ,  0.75,  1.  ,  0.75,  0.5 ,  0.25,  0.  ,
           -0.25, -0.5 , -0.75, -1.  ])
    >>> fill_out_numbers([[0, 1, -1], [1, 2, -2]], rate=0.25)
    array([[ 0.  ,  1.  , -1.  ],
           [ 0.25,  1.25, -1.25],
           [ 0.5 ,  1.5 , -1.5 ],
           [ 0.75,  1.75, -1.75],
           [ 1.  ,  2.  , -2.  ]])

    Ported from the MATLAB function written by Mark Denavit.
    """
    peaks = np.array(peaks)

    if len(peaks.shape) == 1:
        peaks = peaks.reshape(peaks.size, 1)

    if peaks.shape[0] == 1:
        peaks = peaks.T

    numpeaks = peaks.shape[0]
    numbers = [peaks[0, :]]

    for i in range(numpeaks - 1):
        diff = peaks[i + 1, :] - peaks[i, :]
        numsteps = int(np.maximum(2, 1 + np.ceil(np.max(np.abs(diff / rate)))))
        numbers_to_add = np.linspace(peaks[i, :], peaks[i + 1, :], numsteps)
        numbers.append(numbers_to_add[1:, :])

    numbers = np.vstack(numbers)
    if 1 in numbers.shape:
        numbers = numbers.flatten()

    return numbers


KT = TypeVar("KT")
VT = TypeVar("VT")


@dataclasses.dataclass
class ValueTypeDispatch(Generic[KT, VT]):
    """Dispatch helper that raises TypeError.

    Parameters
    ----------
    name : str
        Name of the value type. Used in the error message.
    dispatch : mapping
        Mapping of dispatch keys to values.

    Example
    -------
    >>> tangent_dispatch = ValueTypeDispatch('tangent',
    ...                                      {'current': None,
    ...                                       'initial': '-initial'})
    >>> tangent_dispatch['initial']
    '-initial'
    >>> tangent_dispatch['not_a_tangent']
    <Traceback>
    TypeError: Invalid tangent 'not_a_tangent'; must be one of ['current', 'initial']
    """

    name: str
    dispatch: Mapping[KT, VT]

    def __getitem__(self, key: KT) -> VT:
        try:
            value = self.dispatch[key]
        except KeyError as exc:
            valid = list(self.dispatch)
            raise TypeError(
                f"Invalid {self.name} {key!r}; must be one of {valid!r}"
            ) from exc
        return value
