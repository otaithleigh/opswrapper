import numpy as np

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


def test_node_recorder_pass_array():
    recorder = NodeRecorder(
        file=R'C:\Scratch\displacement.dat',
        nodes=np.array([1, 2, 3, 4, 5]),
        dofs=np.array([1, 2, 3, 4, 5, 6]),
        response='disp',
    )
    generated = recorder.tcl_code()
    expected = (
        'recorder Node -file {C:/Scratch/displacement.dat} '
        '-node 1 2 3 4 5 -dof 1 2 3 4 5 6 disp'
    )
    assert generated == expected


def test_node_recorder_windows_path():
    recorder = NodeRecorder(
        file=R'C:\Scratch\displacement.dat',
        nodes=[1, 2, 3, 4, 5],
        dofs=[1, 2, 3, 4, 5, 6],
        response='disp',
    )
    generated = recorder.tcl_code()
    expected = (
        'recorder Node -file {C:/Scratch/displacement.dat} '
        '-node 1 2 3 4 5 -dof 1 2 3 4 5 6 disp'
    )
    assert generated == expected


def test_node_recorder_delayed_file():
    recorder = NodeRecorder(nodes=1, dofs=1, response='accel')
    generated = recorder.tcl_code()
    expected = 'recorder Node -file {{{file}}} -node 1 -dof 1 accel'
    assert generated == expected


def test_node_recorder_delayed_file_then_format():
    recorder = NodeRecorder(nodes=1, dofs=1, response='accel')
    generated = recorder.tcl_code().format(file='/path/to/file')
    expected = 'recorder Node -file {/path/to/file} -node 1 -dof 1 accel'
    assert generated == expected


def test_node_recorder_region():
    recorder = NodeRecorder(file='/path/to/file', region=1, response='vel')
    generated = recorder.tcl_code()
    expected = 'recorder Node -file {/path/to/file} -region 1 vel'
    assert generated == expected


def test_node_recorder_all_nodes():
    recorder = NodeRecorder(
        file='/path/to/file',
        nodes='all',
        dofs=[1, 2, 3],
        response='vel',
    )
    generated = recorder.tcl_code()
    expected = 'recorder Node -file {/path/to/file} -node {*}[getNodeTags] -dof 1 2 3 vel'
    assert generated == expected


def test_node_recorder_all_nodes_delayed_file():
    recorder = NodeRecorder(nodes='all', dofs=1, response='accel')
    generated = recorder.tcl_code()
    expected = 'recorder Node -file {{{file}}} -node {{*}}[getNodeTags] -dof 1 accel'
    assert generated == expected


def test_node_recorder_all_nodes_delayed_file_then_format():
    recorder = NodeRecorder(nodes='all', dofs=1, response='accel')
    generated = recorder.tcl_code().format(file='/path/to/file')
    expected = 'recorder Node -file {/path/to/file} -node {*}[getNodeTags] -dof 1 accel'
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


def test_element_recorder_pass_array():
    recorder = ElementRecorder(
        file=R'C:\Scratch\forces.dat',
        elements=np.array([1, 2, 3, 4, 5]),
        dofs=np.array([1, 2, 3, 4, 5, 6]),
        response='force',
    )
    generated = recorder.tcl_code()
    expected = (
        'recorder Element -file {C:/Scratch/forces.dat} '
        '-ele 1 2 3 4 5 -dof 1 2 3 4 5 6 force'
    )
    assert generated == expected


def test_element_recorder_windows_path():
    recorder = ElementRecorder(
        file=R'C:\Scratch\forces.dat',
        elements=[1, 2, 3, 4, 5],
        dofs=[1, 2, 3, 4, 5, 6],
        response='force',
    )
    generated = recorder.tcl_code()
    expected = (
        'recorder Element -file {C:/Scratch/forces.dat} '
        '-ele 1 2 3 4 5 -dof 1 2 3 4 5 6 force'
    )
    assert generated == expected


def test_element_recorder_delayed_file():
    recorder = ElementRecorder(elements=1, dofs=1, response='force')
    generated = recorder.tcl_code()
    expected = 'recorder Element -file {{{file}}} -ele 1 -dof 1 force'
    assert generated == expected


def test_element_recorder_delayed_file_then_format():
    recorder = ElementRecorder(elements=1, dofs=1, response='force')
    generated = recorder.tcl_code().format(file='/path/to/file')
    expected = 'recorder Element -file {/path/to/file} -ele 1 -dof 1 force'
    assert generated == expected


def test_element_recorder_region():
    recorder = ElementRecorder(file='/path/to/file', region=1, response='axialForce')
    generated = recorder.tcl_code()
    expected = 'recorder Element -file {/path/to/file} -region 1 axialForce'
    assert generated == expected


def test_element_recorder_all_elements():
    recorder = ElementRecorder(
        file='/path/to/file',
        elements='all',
        dofs=[1, 2, 3],
        response='globalForce',
    )
    generated = recorder.tcl_code()
    expected = 'recorder Element -file {/path/to/file} -ele {*}[getEleTags] -dof 1 2 3 globalForce'
    assert generated == expected


def test_element_recorder_all_elements_delayed_file():
    recorder = ElementRecorder(elements='all', dofs=1, response='force')
    generated = recorder.tcl_code()
    expected = 'recorder Element -file {{{file}}} -ele {{*}}[getEleTags] -dof 1 force'
    assert generated == expected


def test_element_recorder_all_elements_delayed_file_then_format():
    recorder = ElementRecorder(elements='all', dofs=1, response='force')
    generated = recorder.tcl_code().format(file='/path/to/file')
    expected = 'recorder Element -file {/path/to/file} -ele {*}[getEleTags] -dof 1 force'
    assert generated == expected
