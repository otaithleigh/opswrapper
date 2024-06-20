import dataclasses
import numbers
import os
from pathlib import Path
from typing import Callable, Generic, Iterable, Mapping, TypeVar, Union

import numpy as np

StrPath = Union[str, os.PathLike[str]]


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


def path_for_tcl(path: StrPath) -> str:
    return Path(path).as_posix()


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
