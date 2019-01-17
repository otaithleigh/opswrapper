"""Helpers for running OpenSees."""

from __future__ import annotations

import dataclasses
import logging
import os
import pathlib
import subprocess as sub
import tempfile

import numpy as np

log = logging.getLogger(__name__)


@dataclasses.dataclass
class AnalysisResults():
    """Results from an OpenSees analysis.
    
    Parameters
    ----------
    returncode
        The return code from OpenSees.
    stdout
        Captured console output from OpenSees.
    """
    returncode: int
    stdout: str


@dataclasses.dataclass
class OpenSeesAnalysis():
    """Wrapper for an OpenSees analysis.
    
    Parameters
    ----------
    echo_output : optional
        If True, echo OpenSees output to console. (default: False)
    delete_files : optional
        If True, delete temporary files after each run. (default: True)
    opensees : Path, optional
        OpenSees binary to use. (default: 'OpenSees')
    scratch_dir : optional
        Directory to store temporary files. (default: system temp directory)
    """
    echo_output: bool = False
    delete_files: bool = True
    opensees: pathlib.Path = None
    scratch_dir: pathlib.Path = None

    def __post_init__(self):
        if self.opensees is None:
            self.opensees = pathlib.Path('OpenSees')
        else:
            self.opensees = pathlib.Path(self.opensees)

        if self.scratch_dir is None:
            self.scratch_dir = pathlib.Path(tempfile.gettempdir())
        else:
            self.scratch_dir = pathlib.Path(self.scratch_dir)

        self.working_dir = tempfile.TemporaryDirectory(
            prefix="OpenSeesAnalysis_", dir=self.scratch_dir)

    def scratch_file(self, filename: str) -> pathlib.Path:
        """Return the path to `filename` in the scratch directory."""
        return pathlib.Path(self.working_dir.name)/filename

    def run_opensees(self, inputfile: str, echo: bool = None) -> AnalysisResults:
        """Run an OpenSees script.

        Parameters
        ----------
        inputfile
            Script to execute.
        echo : optional
            If `True`, echo output to console. If not provided, uses the 
            `self.echo_output` setting.
        """
        if echo is None:
            echo = self.echo_output

        cmd = [self.opensees, inputfile]
        stdout = []

        #pylint: disable=E1123
        # (bug in astroid.brain; text argument not recognized)
        log.debug("Calling OpenSees with cmd {}".format(cmd))
        with sub.Popen(cmd, bufsize=1, stdout=sub.PIPE, stderr=sub.STDOUT, text=True) as p:
            #pylint: enable=E1123
            if echo:
                for line in p.stdout:
                    print(line, end='')
                    stdout.append(line)
            else:
                for line in p.stdout:
                    stdout.append(line)

        stdout = ''.join(stdout)

        return AnalysisResults(p.returncode, stdout)
