opswrapper
++++++++++

Python wrappers and helpers for (Tcl) OpenSees analyses.


Installation
============

Conda::

    conda install -c otaithleigh opswrapper


Usage
=====

The objects provided in this package largely line up with their OpenSees Tcl
counterparts. The general workflow is to create a list of objects, and then call
``str`` on them while printing to a file. Each entry in the list will become a
line in the Tcl script, allowing for mixing of raw Tcl code and opswrapper
objects.


Simple Example
==============

.. code:: python

    import opswrapper as ops
    model = []
    model.append(ops.Model(ndm=2, ndf=3))
    model.append(ops.Node(1, 0, 0))
    model.append(ops.Node(2, 0, 10))
    model.append(ops.material.Elastic(1, 29000))
    model.append(ops.element.Truss(1, 1, 2, mat=1, A=10))
    print(*model, sep='\n')

Output::

    model basic -ndm 2 -ndf 3
    node 1 0 0
    node 2 0 10
    uniaxialMaterial Elastic 1 29000
    element truss 1 1 2 10 1


Formatting
==========

Objects can be formatted via multiple ways. The simplest is to convert them to
``str``:

.. code:: python

    >>> str(Elastic(1, 29000.))
    'uniaxialMaterial 1 29000'

A float format specifier may be specified when used with the built-in format
commands:

.. code:: python

    >>> format(Elastic(1, 29000.), 'e')
    'uniaxialMaterial 1 2.900000e+4'
    >>> f'{Elastic(1, 29000.):.2e}'
    'uniaxialMaterial 1 2.90e+04'

Specifiers for other types may be passed using the ``tcl_code`` method:

.. code:: python

    >>> Elastic(1, 29000.).tcl_code({int: '4d'})
    'uniaxialMaterial Elastic    1 29000'

Defaults can be set on a global basis using ``base.set_global_format_spec``, on a
per-class basis using ``cls.set_class_format_spec``, or on a per-object basis
using ``self.set_format_spec``:

.. code:: python

    >>> set_global_format_spec({float: '#.3g'})
    >>> section.Elastic2D.set_class_format_spec({float: '#.3g'})
    >>> s = section.Elastic2D(...)
    >>> s.set_format_spec({float: '#.3g'})

Each of these methods return the previously-set modifiers if you wish to restore
them later.
