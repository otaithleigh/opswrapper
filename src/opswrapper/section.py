import dataclasses

from . import base


@dataclasses.dataclass
class Elastic2D(base.OpenSeesObject):
    """Elastic section for 2D analysis.

    Shear deformations may be included by specifying `G` and `alphaY`.

    Parameters
    ----------
    tag : int
        Integer tag for the section.
    E : float
        Elastic modulus of the section.
    A : float
        Area of the section.
    Iz : float
        Moment of inertia of the section.
    G : float, optional
        Shear modulus of the section. Both `G` and `alphaY` must be set to
        create a section with shear deformations. (default: None)
    alphaY : float, optional
        Shear shape factor. Both `G` and `alphaY` must be set to create a
        section with shear deformations. (default: None)
    """
    tag: int
    E: float
    A: float
    Iz: float
    G: float = None
    alphaY: float = None

    def tcl_code(self):
        code = f'section Elastic {self.tag:d} {self.E:g} {self.A:g} {self.Iz:g}'
        if self.G is not None and self.alphaY is not None:
            code += f' {self.G:g} {self.alphaY:g}'
        return code


@dataclasses.dataclass
class Elastic3D(base.OpenSeesObject):
    """Elastic section for 3D analysis.

    Shear deformations may be included by specifying `alphaY` and `alphaZ`.

    Parameters
    ----------
    tag : int
        Integer tag for the section.
    E : float
        Elastic modulus of the section.
    A : float
        Area of the section.
    Iz : float
        Major-axis moment of inertia of the section.
    Iy : float
        Minor-axis moment of inertia of the section.
    G : float
        Shear modulus of the section.
    J : float
        Torsional moment of inertia of the section.
    alphaY : float, optional
        Shear shape factor along the local y-axis. Both `alphaY` and `alphaZ`
        must be set to create a section with shear deformations. (default: None)
    alphaZ : float, optional
        Shear shape factor along the local z-axis. Both `alphaY` and `alphaZ`
        must be set to create a section with shear deformations. (default: None)
    """
    tag: int
    E: float
    A: float
    Iz: float
    Iy: float
    G: float
    J: float
    alphaY: float = None
    alphaZ: float = None

    def tcl_code(self):
        code = (
            f'section Elastic {self.tag:d} {self.E:g} {self.A:g}',
            f' {self.Iz:g} {self.Iy:g} {self.G:g} {self.J:g}'
        )
        if self.alphaY is not None and self.alphaZ is not None:
            code += f' {self.alphaY:g} {self.alphaZ:g}'
        return code


@dataclasses.dataclass
class Fiber(base.OpenSeesObject):
    """Fiber-based section.

    Commands that define the fibers can be passed in at construction or created
    using the methods defined.

    Parameters
    ----------
    tag : int
        Integer tag of the section.
    GJ : float, optional
        Linear-elastic torsional stiffness for the section. (default: None)
    commands : list, optional
        List of commands that make up the section. (default: [])
    """
    tag: int
    GJ: float = None
    commands: list = dataclasses.field(default_factory=list)

    def fiber(self, y, z, A, mat):
        """Add a single fiber.

        Returns `self` to allow chained commands.

        Parameters
        ----------
        y : float
            Local y-coordinate of the fiber.
        z : float
            Local z-coordinate of the fiber.
        A : float
            Area of the fiber.
        mat : int
            Tag of the uniaxial material to use.
        """
        self.commands.append(f'fiber {y:g} {z:g} {A:g} {mat:d}')
        return self

    def patch_quad(self, mat, nfIJ, nfJK, *coords):
        """Add a quadrilateral shaped patch.

        The geometry of the patch is defined by four vertices: I, J, K, L. The
        coordinates of each of the four vertices is specified in counter-
        clockwise sequence.

        Returns `self` to allow chained commands.

        Parameters
        ----------
        mat : int
            Tag of the material used for each fiber.
        nfIJ : int
            Number of fibers in the IJ direction.
        nfJK : int
            Number of fibers in the JK direction.
        *coords : float, tuple
            Local y-z coordinates of the vertices. Specified either as four
            2-tuples or eight floats. Order is I, J, K, L.

        Ref: opensees.berkeley.edu/wiki/index.php/Patch_Command
        """
        if len(coords) == 4:
            yI, zI = coords[0]
            yJ, zJ = coords[1]
            yK, zK = coords[2]
            yL, zL = coords[3]
        elif len(coords) == 8:
            yI, zI, yJ, zJ, yK, zK, yL, zL = coords
        else:
            raise ValueError("patch_quad: coords must either be 4 2-tuples or 8 coordinates")

        self.commands.append(
            f'patch quad {mat:d} {nfIJ:d} {nfJK:d} '
            f'{yI:g} {zI:g} {yJ:g} {zJ:g} {yK:g} {zK:g} {yL:g} {zL:g}'
        )
        return self

    def patch_rect(self, mat, nfY, nfZ, *coords):
        """Add a rectangular patch of fibers.

        The patch is defined by the vertices I and J which define the lower left
        and upper right corners, respectively.

        Returns `self` to allow chained commands.

        Parameters
        ----------
        mat : int
            Tag of the uniaxial material used for each fiber.
        nfY : int
            Number of fibers in the y-direction.
        nfZ : int
            Number of fibers in the z-direction.
        *coords : float, tuple
            Local y-z coordinates of the vertices. Specified either as two
            2-tuples or four floats. Order is I, J.

        Ref: opensees.berkeley.edu/wiki/index.php/Patch_Command
        """
        if len(coords) == 2:
            yI, zI = coords[0]
            yJ, zJ = coords[1]
        elif len(coords) == 4:
            yI, zI, yJ, zJ = coords
        else:
            raise ValueError("patch_rect: coords must either be 2 2-tuples or 4 coordinates")
        
        self.commands.append(f'patch rect {mat:d} {nfY:d} {nfZ:d} {yI:g} {zI:g} {yJ:g} {zJ:g}')

    def tcl_code(self):
        code = [f'section Fiber {self.tag:d}']
        if self.GJ is not None:
            code[0] += f' -GJ {self.GJ:g}'
        code[0] += ' {'
        code.extend([f'    {cmd!s}' for cmd in self.commands])
        code.append('}')
        return '\n'.join(code)
