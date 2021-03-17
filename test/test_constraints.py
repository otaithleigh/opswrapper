from opswrapper import constraints


def test_Plain():
    generated = constraints.Plain().tcl_code()
    assert generated == 'constraints Plain'


def test_Transformation():
    generated = constraints.Transformation().tcl_code()
    assert generated == 'constraints Transformation'


def test_Lagrange():
    generated = constraints.Lagrange(1e6, 1e6).tcl_code()
    assert generated == 'constraints Lagrange 1e+06 1e+06'


def test_Lagrange_other_format():
    generated = constraints.Lagrange(1e6, 1e6).tcl_code({float: '.0f'})
    assert generated == 'constraints Lagrange 1000000 1000000'


def test_Penalty():
    generated = constraints.Penalty(1e12, 1e12).tcl_code()
    assert generated == 'constraints Penalty 1e+12 1e+12'


def test_Penalty_other_format():
    generated = constraints.Penalty(1e12, 1e12).tcl_code({float: '+.1e'})
    assert generated == 'constraints Penalty +1.0e+12 +1.0e+12'
