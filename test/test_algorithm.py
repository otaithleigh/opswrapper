from pytest import raises

from opswrapper import algorithm


def test_Linear():
    generated = algorithm.Linear().tcl_code()
    assert generated == 'algorithm Linear'


def test_Linear_with_tangent():
    generated = algorithm.Linear('secant').tcl_code()
    assert generated == 'algorithm Linear -secant'


def test_Linear_factor_once():
    generated = algorithm.Linear(factor_once=True).tcl_code()
    assert generated == 'algorithm Linear -factorOnce'


def test_Linear_bad_tangent():
    with raises(TypeError):
        algorithm.Linear('not_a_valid_tangent').tcl_code()


def test_Newton():
    generated = algorithm.Newton().tcl_code()
    assert generated == 'algorithm Newton'


def test_Newton_tangent():
    generated = algorithm.Newton('hall').tcl_code()
    assert generated == 'algorithm Newton -hall'


def test_Newton_weird_tangent():
    generated = algorithm.Newton('initialThenCurrent').tcl_code()
    # No, this is not a typo.
    assert generated == 'algorithm Newton -intialThenCurrent'


def test_KrylovNewton_default():
    generated = algorithm.KrylovNewton().tcl_code()
    assert generated == 'algorithm KrylovNewton -iterate current -increment current -maxDim 3'


def test_Broyden_default():
    generated = algorithm.Broyden().tcl_code()
    assert generated == 'algorithm Broyden -count 10'


def test_Broyden_tangent():
    generated = algorithm.Broyden('secant').tcl_code()
    assert generated == 'algorithm Broyden -secant -count 10'
