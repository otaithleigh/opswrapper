from opswrapper import material


def test_elastic():
    assert material.Elastic(1, 29000).tcl_code() == 'uniaxialMaterial Elastic 1 29000'


def test_elastic_special_format():
    assert material.Elastic(1, 29000).tcl_code({float: '.2e'}) == 'uniaxialMaterial Elastic 1 2.90e+04'


def test_elastic_Eneg_but_no_eta():
    generated_code = material.Elastic(1, 29000, Eneg=10000).tcl_code()
    expected_code = 'uniaxialMaterial Elastic 1 29000 0 10000'
    assert generated_code == expected_code


def test_elastic_Eneg_and_eta():
    generated_code = material.Elastic(1, 29000, 12.0, 10000).tcl_code()
    expected_code = 'uniaxialMaterial Elastic 1 29000 12 10000'
    assert generated_code == expected_code


def test_elastic_pp():
    generated_code = material.ElasticPP(1, 29000, 0.00207).tcl_code()
    expected_code = 'uniaxialMaterial ElasticPP 1 29000 0.00207'
    assert generated_code == expected_code


def test_elastic_pp_eps0_but_no_eps_yN():
    generated_code = material.ElasticPP(1, 29000, 0.00207, eps0=0.001).tcl_code()
    expected_code = 'uniaxialMaterial ElasticPP 1 29000 0.00207 0.00207 0.001'
    assert generated_code == expected_code


def test_Steel01():
    generated_code = material.Steel01(1, 50, 29000, 0.003).tcl_code()
    expected_code = 'uniaxialMaterial Steel01 1 50 29000 0.003'
    assert generated_code == expected_code


def test_Steel01_special_format():
    generated_code = material.Steel01(1, 50, 29000, 0.003).tcl_code({float: '.2e'})
    expected_code = 'uniaxialMaterial Steel01 1 5.00e+01 2.90e+04 3.00e-03'
    assert generated_code == expected_code


def test_Steel01_iso_hardening():
    generated_code = material.Steel01(1, 50, 29000, 0.003, 0.01, 0.02, 0.03, 0.04).tcl_code()
    expected_code = 'uniaxialMaterial Steel01 1 50 29000 0.003 0.01 0.02 0.03 0.04'
    assert generated_code == expected_code


def test_Steel02():
    generated_code = material.Steel02(1, 50, 29000, 0.003).tcl_code()
    expected_code = 'uniaxialMaterial Steel02 1 50 29000 0.003 20 0.925 0.15'
    assert generated_code == expected_code


def test_Steel02_special_format():
    generated_code = material.Steel02(1, 50, 29000, 0.003).tcl_code({int: '4d'})
    expected_code = 'uniaxialMaterial Steel02    1 50 29000 0.003 20 0.925 0.15'
    assert generated_code == expected_code


def test_Steel02_non_default_R():
    generated_code = material.Steel02(1, 50, 29000, 0.003, R0=15, cR1=0.9, cR2=0.20).tcl_code()
    expected_code = 'uniaxialMaterial Steel02 1 50 29000 0.003 15 0.9 0.2'
    assert generated_code == expected_code


def test_Steel02_iso_hardening():
    generated_code = material.Steel02(1, 50, 29000, 0.003, a1=0.5, a2=1.0, a3=0.5, a4=1.0).tcl_code()
    expected_code = 'uniaxialMaterial Steel02 1 50 29000 0.003 20 0.925 0.15 0.5 1 0.5 1'
    assert generated_code == expected_code


def test_Steel02_initial_stress():
    generated_code = material.Steel02(1, 50, 29000, 0.003, sigma_i=15).tcl_code()
    expected_code = 'uniaxialMaterial Steel02 1 50 29000 0.003 20 0.925 0.15 0 1 0 1 15'
    assert generated_code == expected_code
