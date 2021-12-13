from opswrapper import integrator


def test_LoadControl_default():
    generated = integrator.LoadControl(0.1).tcl_code()
    assert generated == 'integrator LoadControl 0.1 1 0.1 0.1'


def test_DisplacementControl_default():
    generated = integrator.DisplacementControl(1, 1, 0.1).tcl_code()
    assert generated == 'integrator DisplacementControl 1 1 0.1 1 0.1 0.1'


def test_MinUnbalDispNorm_default():
    generated = integrator.MinUnbalDispNorm(0.1).tcl_code()
    assert generated == 'integrator MinUnbalDispNorm 0.1 1 0.1 0.1'


def test_ArcLength():
    generated = integrator.ArcLength(1.0, 0.1).tcl_code({float: '#g'})
    assert generated == 'integrator ArcLength 1.00000 0.100000'


def test_CentralDifference():
    generated = integrator.CentralDifference().tcl_code()
    assert generated == 'integrator CentralDifference'


def test_Newmark():
    generated = integrator.Newmark(0.5, 0.25).tcl_code()
    assert generated == 'integrator Newmark 0.5 0.25'


def test_HHT_default():
    generated = integrator.HHT(0.9).tcl_code()
    assert generated == 'integrator HHT 0.9'


def test_HHT_non_default():
    generated = integrator.HHT(0.9, 0.3025).tcl_code()
    assert generated == 'integrator HHT 0.9 0.3025 0.6'
