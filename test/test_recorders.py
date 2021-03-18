from opswrapper.output import NodeRecorder, ElementRecorder


def test_node_recorder():
    recorder = NodeRecorder(
        file='/path/to/file',
        nodes=1,
        dofs=[1, 2],
        response='disp',
    )
    generated = recorder.tcl_code()
    expected = 'recorder Node -file {/path/to/file} -node 1 -dof 1 2 disp'
    assert generated == expected


def test_element_recorder():
    recorder = ElementRecorder(
        file='/path/to/file',
        elements=1,
        dofs=[1, 2],
        response='localForce',
    )
    generated = recorder.tcl_code()
    expected = 'recorder Element -file {/path/to/file} -ele 1 -dof 1 2 localForce'
    assert generated == expected
