import dataclasses

__all__ = [
    'MultiFormatSpec',
    'set_global_format_spec',
]


@dataclasses.dataclass
class MultiFormatSpec():
    """Specifiers for formatting of different numeric types."""
    int: str = 'd'
    float: str = 'g'

    def copy(self):
        """Return a copy of the object."""
        return self.__class__(self.int, self.float)

    def update(self, other):
        """Update the object. Accepts a dict or MultiFormatSpec.

        Unlike the dict method, returns self.
        """
        if isinstance(other, self.__class__):
            get = lambda obj, v: getattr(obj, v, None)
        else:
            get = lambda obj, v: obj.get(v, None)
        for field in dataclasses.fields(self):
            new_value = get(other, field.name)
            if new_value is not None:
                setattr(self, field.name, new_value)
        return self


_GLOBAL_FORMAT_SPEC = MultiFormatSpec()


def set_global_format_spec(**format_spec):
    """Set the global default format specifiers.

    Parameters
    ----------
    **format_spec
        Keyword-based format identifiers.

    Returns
    -------
    old_spec : MultiFormatSpec
        The previous globally-set formatters.

    Example
    -------
    >>> s = section.Elastic2D(1, 29000, 10, 144)
    >>> print(s)
    section Elastic 1 29000 10 144
    >>> set_global_format_spec(float='#.3g')
    MultiFormatSpec(int='d', float='g')
    >>> print(s)
    section Elastic 1 2.90e+04 10.0 144.
    """
    old_spec = _GLOBAL_FORMAT_SPEC.copy()
    _GLOBAL_FORMAT_SPEC.update(format_spec)
    return old_spec
