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
