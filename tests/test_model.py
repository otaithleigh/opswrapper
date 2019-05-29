from opswrapper.model import Model, Node


def test_model():
    assert Model(ndm=2, ndf=3).tcl_code() == "model basic -ndm 2 -ndf 3"


def test_node():
    assert Node(1, (0, 0), mass=(1, 2, 3)).tcl_code() == "node 1 0 0 -mass 1 2 3"
    assert Node(2, (2.2, 2.0)).tcl_code() == "node 2 2.2 2"


def test_node_unpack():
    assert Node(1, *(0, 0), mass=(1, 2, 3)).tcl_code() == "node 1 0 0 -mass 1 2 3"
    assert Node(2, *(2.2, 2.0)).tcl_code() == "node 2 2.2 2"


def test_node_ndm_1():
    assert Node(1, 0, mass=1).tcl_code() == "node 1 0 -mass 1"
    assert Node(2, 1.1).tcl_code() == "node 2 1.1"
