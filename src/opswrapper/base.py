import abc
import dataclasses


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


DEFAULT_FORMAT_SPEC = MultiFormatSpec()
_global_format_spec = DEFAULT_FORMAT_SPEC.copy()


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
    old_spec = _global_format_spec.copy()
    _global_format_spec.update(format_spec)
    return old_spec


class OpenSeesObject(abc.ABC):
    """Base class for wrapping OpenSees Tcl objects/commands.

    Formatting
    ----------
    `OpenSeesObject`s can be formatted via multiple ways. The simplest is to convert
    them to str::

        >>> str(Elastic(1, 29000))
        'uniaxialMaterial 1 29000'

    A float format specifier may be specified when used with the built-in format
    commands::

        >>> format(Elastic(1, 29000), 'e')
        'uniaxialMaterial 1 2.900000e+4'
        >>> f'{Elastic(1, 29000):.2e}'
        'uniaxialMaterial 1 2.90e+04'

    Specifiers for other numeric types may be passed using the `tcl_code` method::

        >>> Elastic(1, 29000).tcl_code(int='4d')
        'uniaxialMaterial Elastic    1 29000'

    Defaults can be set on a global basis using `base.set_global_format_spec`, on a
    per-class basis using `cls.set_class_format_spec`, or on a per-object basis
    using `self.set_format_spec`::

        >>> set_global_format_spec(float='#.3g')
        >>> section.Elastic2D.set_class_format_spec(float='#.3g')
        >>> s = section.Elastic2D(...)
        >>> s.set_format_spec(float='#.3g')

    Each of these methods return the previously-set modifiers if you wish to restore
    them later.
    """
    _format_spec: MultiFormatSpec = DEFAULT_FORMAT_SPEC

    def get_format_spec(self, **formats):
        """Return a copy of the format specifiers for this object.

        Parameters
        ----------
        **formats
            Format specifiers to use instead of the stored ones.

        Returns
        -------
        format_spec : MultiFormatSpec
            Format specifiers, updated if necessary.
        """
        if formats is None:
            format_spec = self._format_spec.copy()
        else:
            format_spec = self._format_spec.copy().update(formats)
        return format_spec

    def set_format_spec(self, **formats):
        """Set the default format specifiers for this object.

        Parameters
        ----------
        **formats
            Keyword-based format identifiers.

        Returns
        -------
        old_spec : MultiFormatSpec
            The previous formatters.
        """
        old_spec = self._format_spec
        self._format_spec = old_spec.copy().update(formats)
        return old_spec

    @classmethod
    def set_class_format_spec(cls, **formats):
        """Set the default format specifiers for this class.

        Parameters
        ----------
        **formats
            Keyword-based format identifiers.

        Returns
        -------
        old_spec : MultiFormatSpec
            The previous formatters.
        """
        old_spec = cls._format_spec
        cls._format_spec = old_spec.copy().update(formats)
        return old_spec

    @abc.abstractmethod
    def tcl_code(self, **format_spec) -> str:
        """Return the corresponding Tcl code to create this object.

        Parameters
        ----------
        **format_spec
            Format specifiers by class. See `MultiFormatSpec` for supported classes.

        Example
        -------
        >>> import opswrapper as ops
        >>> ops.material.Elastic(1, 29000.0).tcl_code(float='e')
        'uniaxialMaterial Elastic 1 2.900000e+04'
        """
        pass

    def __str__(self):
        return self.tcl_code()

    def __format__(self, float_spec=None):
        return self.tcl_code(float=float_spec)

    def use_default_format(self):
        self._format_spec = DEFAULT_FORMAT_SPEC

    def dump(self, fid, **format_spec):
        """Write the Tcl code for this object to the given file descriptor.

        Parameters
        ----------
        fid
            File-like object to write to.
        **format_spec
            Format specifiers to use instead of the defaults.
        """
        print(self.tcl_code(**format_spec), file=fid)
