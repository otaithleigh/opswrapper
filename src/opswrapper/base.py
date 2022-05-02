import abc
import dataclasses
import typing

from .formatting import MultiFormatSpec, SpecLike, _GLOBAL_FORMAT_SPEC
from .utils import coerce_numeric

__all__ = [
    'OpenSeesObject',
]


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

        >>> format(Elastic(1, 29000.), 'e')
        'uniaxialMaterial 1 2.900000e+4'
        >>> f'{Elastic(1, 29000.):.2e}'
        'uniaxialMaterial 1 2.90e+04'

    Specifiers for other numeric types may be passed using the `tcl_code` method::

        >>> Elastic(1, 29000.).tcl_code({int: '4d'})
        'uniaxialMaterial Elastic    1 29000'

    Defaults can be set on a global basis using `base.set_global_format_spec`, on a
    per-class basis using `cls.set_class_format_spec`, or on a per-object basis
    using `self.set_format_spec`::

        >>> set_global_format_spec({float: '#.3g'})
        >>> section.Elastic2D.set_class_format_spec({float: '#.3g'})
        >>> s = section.Elastic2D(...)
        >>> s.set_format_spec({float: '#.3g'})

    Each of these methods return the previously-set modifiers if you wish to restore
    them later.
    """
    _format_spec: MultiFormatSpec = _GLOBAL_FORMAT_SPEC

    def __post_init__(self):
        # Gently attempt to coerce numeric types. Not guarding against TypeError
        # from dataclasses.fields since __post_init__ only gets called on
        # dataclasses.
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            # A field's "type" isn't always strictly a type -- sometimes it's an
            # annotation that doesn't resolve to a concrete type. For example,
            # Union[str, int] causes coerce_numeric to panic when checking for
            # numeric subclasses. I'm not sure if it makes more sense to check
            # that here or inside coerce_numeric.
            if isinstance(field.type, type):
                value = coerce_numeric(value, field.type)
            setattr(self, field.name, value)

    def get_object_formats(self, objects: list, formats: SpecLike = None):
        """Get type-specific formatters for a list of objects, using this
        object's current format spec.

        Parameters
        ----------
        objects : list
            The objects to get formatters for.
        formats : SpecLike, optional
            Override format specifiers.

        Returns
        -------
        specs : list[str]
            List of specifiers, in the same order as `objects`.
        """
        format_spec = self.get_format_spec(formats)
        return [format_spec.get_format(obj) for obj in objects]

    def format_objects(self, objects: list, formats: SpecLike = None) -> list[str]:
        """Format a list of objects according to their type.

        Parameters
        ----------
        objects : list
            The objects to format.
        formats : SpecLike, optional
            Override format specifiers.
        """
        format_spec = self.get_format_spec(formats)
        formatted = []
        for obj in objects:
            if isinstance(obj, OpenSeesObject):
                formatted.append(obj.tcl_code(formats))
            else:
                fmt = format_spec.get_format(obj)
                formatted.append(format(obj, fmt))

        return formatted

    def get_format_spec(self, formats: SpecLike = None):
        """Return a copy of the format specifiers for this object.

        Parameters
        ----------
        formats : SpecLike, optional
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

    def set_format_spec(self, formats: SpecLike):
        """Set the default format specifiers for this object.

        Parameters
        ----------
        formats : SpecLike
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
    def set_class_format_spec(cls, formats: SpecLike):
        """Set the default format specifiers for this class.

        Parameters
        ----------
        formats : SpecLike
            Class-based format identifiers.

        Returns
        -------
        old_spec : MultiFormatSpec
            The previous formatters.
        """
        old_spec = cls._format_spec
        cls._format_spec = old_spec.copy().update(formats)
        return old_spec

    @abc.abstractmethod
    def tcl_code(self, formats: SpecLike = None) -> str:
        """Return the corresponding Tcl code to create this object.

        Parameters
        ----------
        formats : SpecLike, optional
            Override format specifiers by class.

        Example
        -------
        >>> import opswrapper as ops
        >>> ops.material.Elastic(1, 29000.0).tcl_code({float: 'e'})
        'uniaxialMaterial Elastic 1 2.900000e+04'
        """
        pass

    def tcl_args(self, formats: SpecLike = None) -> typing.List[str]:
        """Return the formatted arguments to the Tcl command to create this
        object.

        Parameters
        ----------
        formats : SpecLike, optional
            Override format specifiers by class.

        Example
        -------
        >>> import opswrapper as ops
        >>> ops.material.Elastic(1, 29000.0).tcl_args({float: 'e'})
        ['Elastic', '1' , '2.900000e+04']
        """
        raise NotImplementedError()

    def __str__(self):
        return self.tcl_code()

    def __format__(self, float_spec=None):
        return self.tcl_code({float: float_spec})

    def use_global_format(self):
        self._format_spec = _GLOBAL_FORMAT_SPEC

    def dump(self, fid: typing.TextIO, formats: SpecLike = None):
        """Write the Tcl code for this object to the given file descriptor.

        Parameters
        ----------
        fid
            File-like object to write to.
        formats : SpecLike
            Format specifiers to use instead of the defaults.
        """
        print(self.tcl_code(formats), file=fid)


OpenSeesDef = typing.Union[str, OpenSeesObject]
