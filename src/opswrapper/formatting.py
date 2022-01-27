from __future__ import annotations

import dataclasses
from typing import Dict, Union

__all__ = [
    'MultiFormatSpec',
    'set_global_format_spec',
]


@dataclasses.dataclass
class MultiFormatSpec():
    """Specifiers for formatting of different types."""
    _spec: SpecDict = dataclasses.field(default_factory=dict)

    # Properties for temporary backwards compatibility
    @property
    def int(self):
        return self.get_format(1)

    @property
    def float(self):
        return self.get_format(1.0)

    def __repr__(self) -> str:
        clsname = self.__class__.__name__
        specs = ', '.join([f'{cls.__name__}={fmt!r}' for cls, fmt in self._spec.items()])
        return f'{clsname}({specs})'

    def copy(self):
        """Return a copy of the object."""
        the_copy = self.__class__()
        the_copy.update(self)
        return the_copy

    def __or__(self, other: SpecLike):
        new = self.copy()
        new.update(other)
        return new

    def __ior__(self, other: SpecLike):
        self.update(other)
        return self

    def update(self, other: SpecLike):
        """Update the object. Accepts a dict or MultiFormatSpec.

        Unlike the dict method, returns self.
        """
        if isinstance(other, self.__class__):
            self._spec.update(other._spec)
        else:
            self._spec.update(other)
        return self

    def get_format(self, obj: object):
        """Find a format specifier for the given object.

        - If the object's type is listed specifically, return that.
        - Failing that, try to find a registered type that is a superclass of
          the object. If multiple superclasses are registered, the earliest
          registered one is returned.
        - If no superclass is registered, return ''.

        Parameters
        ----------
        obj : object
            The object to get a format for.

        Returns
        -------
        fmt : str
            The format string to use for `obj`.
        """
        try:
            fmt = self._spec[obj.__class__]
        except KeyError:
            for type, fmt in self._spec.items():
                if isinstance(obj, type):
                    break
            else:
                fmt = ''
        return fmt

    def register_format(self, cls: type, fmt: str):
        """Register a format string for a given type.

        Parameters
        ----------
        cls : Type
            The type to register.
        fmt : str
            The format string to register.
        """
        if not isinstance(cls, type):
            raise TypeError(f'cls must be a type, not a {cls.__class__!r}')

        self._spec[cls] = fmt


SpecDict = Dict[type, str]
SpecLike = Union[SpecDict, MultiFormatSpec]

_GLOBAL_FORMAT_SPEC = MultiFormatSpec()
_GLOBAL_FORMAT_SPEC.register_format(bool, 'd')
_GLOBAL_FORMAT_SPEC.register_format(int, 'd')
_GLOBAL_FORMAT_SPEC.register_format(float, 'g')
_GLOBAL_FORMAT_SPEC.register_format(str, '')


def set_global_format_spec(formats: SpecDict):
    """Set the global default format specifiers.

    Parameters
    ----------
    formats: dict[type, str]
        Class-based format identifiers.

    Returns
    -------
    old_spec : MultiFormatSpec
        The previous globally-set formatters.

    Example
    -------
    >>> s = section.Elastic2D(1, 29000, 10, 144)
    >>> print(s)
    section Elastic 1 29000 10 144
    >>> set_global_format_spec({float: '#.3g'})
    MultiFormatSpec(int='d', float='g')
    >>> print(s)
    section Elastic 1 2.90e+04 10.0 144.
    """
    old_spec = _GLOBAL_FORMAT_SPEC.copy()
    _GLOBAL_FORMAT_SPEC.update(formats)
    return old_spec


def get_global_format_spec():
    """Return the global format specifier."""
    return _GLOBAL_FORMAT_SPEC


def get_format(o):
    """Get the globally-set format specifier for an object."""
    return _GLOBAL_FORMAT_SPEC.get_format(o)
