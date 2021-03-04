from opswrapper import utils


def test_tcllist():
    assert utils.tcllist([1.0, 2, "sam's the best!"]) == "[list {1.0} {2} {sam's the best!}]"
