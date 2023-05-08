from opswrapper import integration


def test_HingeRadau():
    generated = integration.HingeRadau(1, 0.01, 2, 0.02, 3).tcl_code()
    assert generated == '"HingeRadau 1 0.01 2 0.02 3"'


def test_HingeRadauTwo():
    generated = integration.HingeRadauTwo(1, 0.01, 2, 0.02, 3).tcl_code()
    assert generated == '"HingeRadauTwo 1 0.01 2 0.02 3"'


def test_HingeMidpoint():
    generated = integration.HingeMidpoint(1, 0.01, 2, 0.02, 3).tcl_code()
    assert generated == '"HingeMidpoint 1 0.01 2 0.02 3"'
