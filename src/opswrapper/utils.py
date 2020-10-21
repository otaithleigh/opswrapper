import dataclasses
import pathlib
import types
from typing import List

import numpy as np

from .base import OpenSeesDef


class Namespace(types.SimpleNamespace):
    """Extension of the SimpleNamespace class to allow iterating over name-value
    pairs (a la dict.items).
    
    Example
    -------
    >>> files = Namespace()
    >>> files.input = 'input.tcl'
    >>> files.output = 'output.dat'
    >>> for name, path in files:
    ...     print(name, ':', path)
    input : input.tcl
    output : output.dat
    """
    def __iter__(self):
        return iter(self.__dict__.items())


def path_for_tcl(path) -> str:
    return str(path).replace('\\', '/')


def print_model(model: List[OpenSeesDef], file=None):
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
        file = pathlib.Path(file)
        file_is_descriptor = False
    except TypeError:
        file_is_descriptor = True

    modeltext = '\n'.join([str(line) for line in model])
    if file_is_descriptor:
        print(modeltext, file=file)
    else:
        with open(file, 'w') as f:
            print(modeltext, file=f)


def list_dataclass_fields(name, object, pad='', end='\n', exclude=None) -> str:
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
    lenname = lambda f: len(getattr(f, 'name'))
    max_key_len = max(map(lenname, fields))
    l = []
    for field in fields:
        if exclude is not None and field.name in exclude:
            continue
        l.append(f'{pad}{name}.{field.name.ljust(max_key_len)} : {getattr(object, field.name)!r}')

    return end.join(l)


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
        numsteps = int(np.maximum(2, 1 + np.ceil(np.max(np.abs(diff/rate)))))
        numbers_to_add = np.linspace(peaks[i, :], peaks[i + 1, :], numsteps)
        numbers.append(numbers_to_add[1:, :])

    numbers = np.vstack(numbers)
    if 1 in numbers.shape:
        numbers = numbers.flatten()

    return numbers
