from pytest import raises

from opswrapper import test


def test_standard():
    generated = test.NormUnbalance(1e-8, 50).tcl_code()
    expected = 'test NormUnbalance 1e-08 50 0 2'
    assert generated == expected


def test_with_flags():
    generated = test.NormUnbalance(1e-8, 50, 2, 2).tcl_code()
    expected = 'test NormUnbalance 1e-08 50 2 2'
    assert generated == expected


def test_with_str_field():
    generated = test.NormDispIncr('$tol', 50, 2, 2).tcl_code()
    expected = 'test NormDispIncr $tol 50 2 2'
    assert generated == expected


def test_alternate_format():
    generated = test.NormUnbalance(1e-8, 50, 2, 2).tcl_code({float: '.2e'})
    expected = 'test NormUnbalance 1.00e-08 50 2 2'
    assert generated == expected


def test_bad_print_flag():
    the_test = test.EnergyIncr(1e-4, 50, 8)
    with raises(ValueError):
        the_test.tcl_code()
