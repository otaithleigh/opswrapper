from opswrapper import element
from opswrapper import integration


def test_ElasticBeamColumn2D():
    generated = element.ElasticBeamColumn2D(1, 0, 1, 10.0, 29000.0, 144.0, 1).tcl_code()
    expected = 'element elasticBeamColumn 1 0 1 10 29000 144 1'
    assert generated == expected


def test_ElasticBeamColumn3D():
    generated = element.ElasticBeamColumn3D(1, 0, 1, 10.0, 29000.0, 11000.0, 0.402, 14.1, 144.0,
                                            1).tcl_code()
    expected = 'element elasticBeamColumn 1 0 1 10 29000 11000 0.402 14.1 144 1'
    assert generated == expected


def test_ForceBeamColumn():
    generated = element.ForceBeamColumn(2, 0, 1, 1, integration.Lobatto(1, 5)).tcl_code()
    expected = 'element forceBeamColumn 2 0 1 1 "Lobatto 1 5"'
    assert generated == expected
