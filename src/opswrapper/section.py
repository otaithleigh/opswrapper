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

    def tcl_code(self, **format_spec) -> str:
        fmt = self.get_format_spec(**format_spec)
        i, f = fmt.int, fmt.float
        code = f'section Elastic {self.tag:{i}} {self.E:{f}} {self.A:{f}} {self.Iz:{f}}'
        if self.G is not None and self.alphaY is not None:
            code += f' {self.G:{f}} {self.alphaY:{f}}'
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

    def tcl_code(self, **format_spec) -> str:
        fmt = self.get_format_spec(**format_spec)
        i, f = fmt.int, fmt.float
        code = (
            f'section Elastic {self.tag:{i}} {self.E:{f}} {self.A:{f}}'
            f' {self.Iz:{f}} {self.Iy:{f}} {self.G:{f}} {self.J:{f}}'
        )
        if self.alphaY is not None and self.alphaZ is not None:
            code += f' {self.alphaY:{f}} {self.alphaZ:{f}}'
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

    Example
    -------
    >>> ops.section.Fiber(1).fiber(0, 1, 1.0, 2).fiber(0, -1, 1.0, 2)
    Fiber(tag=1, GJ=None, commands=[Fiber._Fiber(y=0, z=1, A=1.0, mat=2), Fiber._Fiber(y=0, z=-1, A=1.0, mat=2)])
    """
    tag: int
    GJ: float = None
    commands: list = dataclasses.field(default_factory=list)

    @dataclasses.dataclass
    class _Fiber():
        y: float
        z: float
        A: float
        mat: int
        _parent: 'Fiber' = dataclasses.field(repr=False, hash=False)

        def tcl_code(self, **format_spec) -> str:
            fmt = self._parent.get_format_spec(format_spec)
            i, f = fmt.int, fmt.float
            return f'fiber {self.y:{f}} {self.z:{f}} {self.A:{f}} {self.mat:{i}}'

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
        self.commands.append(self._Fiber(y, z, A, mat, self))
        return self

    @dataclasses.dataclass
    class _PatchQuad():
        mat: int
        nfIJ: int
        nfJK: int
        yI: float
        zI: float
        yJ: float
        zJ: float
        yK: float
        zK: float
        yL: float
        zL: float
        _parent: 'Fiber' = dataclasses.field(repr=False, hash=False)

        def tcl_code(self, **format_spec) -> str:
            fmt = self._parent.get_format_spec(format_spec)
            i, f = fmt.int, fmt.float
            return (
                f'patch quad {self.mat:{i}} {self.nfIJ:{i}} {self.nfJK:{i}}'
                f' {self.yI:{f}} {self.zI:{f}} {self.yJ:{f}} {self.zJ:{f}}'
                f' {self.yK:{f}} {self.zK:{f}} {self.yL:{f}} {self.zL:{f}}'
            )

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

        self.commands.append(self._PatchQuad(mat, nfIJ, nfJK, yI, zI, yJ, zJ, yK, zK, yL, zL, self))
        return self

    @dataclasses.dataclass
    class _PatchRect():
        mat: int
        nfY: int
        nfZ: int
        yI: float
        zI: float
        yJ: float
        zJ: float
        _parent: 'Fiber' = dataclasses.field(repr=False, hash=False)

        def tcl_code(self, **format_spec) -> str:
            fmt = self._parent.get_format_spec(format_spec)
            i, f = fmt.int, fmt.float
            return (
                f'patch rect {self.mat:{i}} {self.nfY:{i}} {self.nfZ:{i}}'
                f' {self.yI:{f}} {self.zI:{f}} {self.yJ:{f}} {self.zJ:{f}}'
            )

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

        self.commands.append(self._PatchRect(mat, nfY, nfZ, yI, zI, yJ, zJ, self))
        return self

    def tcl_code(self, **format_spec) -> str:
        fmt = self.get_format_spec(**format_spec)
        i, f = fmt.int, fmt.float
        code = [f'section Fiber {self.tag:{i}}']
        if self.GJ is not None:
            code[0] += f' -GJ {self.GJ:{f}}'
        code[0] += ' {'
        code.extend([f'    {cmd.tcl_code(**format_spec)}' for cmd in self.commands])
        code.append('}')
        return '\n'.join(code)
