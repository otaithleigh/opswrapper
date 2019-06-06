from opswrapper import material


def test_elastic():
    assert material.Elastic(1, 29000).tcl_code() == 'uniaxialMaterial Elastic 1 29000'


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
