from opswrapper.output import NodeRecorder, ElementRecorder


def test_node_recorder():
    generated_code = NodeRecorder(
        file='/path/to/file', nodes=1, dofs=[1, 2], response='disp').tcl_code()
    expected_code = 'recorder Node -file {/path/to/file} -node 1 -dof 1 2 disp'
    assert generated_code == expected_code


def test_element_recorder():
    generated_code = ElementRecorder(
        file='/path/to/file', elements=1, dofs=[1, 2], response='localForce').tcl_code()
    expected_code = 'recorder Element -file {/path/to/file} -ele 1 -dof 1 2 localForce'
    assert generated_code == expected_code
