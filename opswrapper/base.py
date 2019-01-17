from __future__ import annotations

import abc

class OpenSeesObject(abc.ABC):
    """Base class for wrapping OpenSees Tcl objects/commands."""

    @abc.abstractmethod
    def tcl_code(self) -> str:
        """Return the corresponding Tcl code to create this object."""
        pass

    def dump(self, fid):
        """Write the Tcl code for this object to the given file descriptor.
        
        Parameters
        ----------
        fid
            File-like object to write to.
        """
        print(self.tcl_code(), file=fid)
