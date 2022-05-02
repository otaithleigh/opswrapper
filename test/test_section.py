from opswrapper import section


def test_Elastic2D():
    generated = section.Elastic2D(1, 29000, 10, 144).tcl_code()
    expected = 'section Elastic 1 29000 10 144'
    assert generated == expected


def test_Elastic2D_special_format():
    generated = section.Elastic2D(1, 29000, 10, 144).tcl_code({float: '#.3g'})
    expected = 'section Elastic 1 2.90e+04 10.0 144.'
    assert generated == expected


def test_Elastic2D_shear():
    generated = section.Elastic2D(1, 29000, 10, 144, 11000, 1.0).tcl_code()
    expected = 'section Elastic 1 29000 10 144 11000 1'
    assert generated == expected


def test_Elastic3D():
    generated = section.Elastic3D(1, 29000, 10, 144, 14.1, 11000, 0.402).tcl_code()
    expected = 'section Elastic 1 29000 10 144 14.1 11000 0.402'
    assert generated == expected


def test_Elastic3D_shear():
    generated = section.Elastic3D(1, 29000, 10, 144, 14.1, 11000, 0.402, 1.0, 1.0).tcl_code()
    expected = 'section Elastic 1 29000 10 144 14.1 11000 0.402 1 1'
    assert generated == expected


def test_Fiber_section():
    generated = section.Fiber(1).fiber(0, -1, 1.0, 2).fiber(0, 1, 1.0, 2).tcl_code()
    expected = 'section Fiber 1 {\n    fiber 0 -1 1 2\n    fiber 0 1 1 2\n}'
    assert generated == expected
