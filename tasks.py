import subprocess as sub
import sys
from pathlib import Path
from shutil import rmtree

from invoke import task

try:
    import colorama
    from colorama import Fore, Style
    _COLOR = True
    colorama.init()
except ImportError:
    _COLOR = False

#===============================================================================
# Configuration
#===============================================================================
# The name used by PyPi and Conda
NAME = 'opswrapper'

# The actual importable package name
PACKAGE = 'opswrapper'

# Conda options
CONDABUILD = 'mambabuild'
CHANNELS = ['conda-forge', 'defaults']

# Whether to echo commands
ECHO = True

#===============================================================================
# Auto-generated variables
#===============================================================================
with Path('src', PACKAGE, '__version__').open() as f:
    VERSION = f.read()

PYPI_NAME = NAME.replace('-', '_')
BUILD_DIR = Path('build')
DIST_DIR = Path('dist')
PYPI_DIST_DIR = DIST_DIR / 'pypi' / VERSION

#===============================================================================
# Tasks
#===============================================================================
@task
def clean(c):
    squawk('Removing', DIST_DIR)
    rmtree(DIST_DIR, ignore_errors=True)
    squawk('Removing', BUILD_DIR)
    rmtree(BUILD_DIR, ignore_errors=True)


#---------------------------------------
# Build
#---------------------------------------
@task
def build_pypi(c):
    """Build the PyPi package."""
    pypi_build_dir = BUILD_DIR / f'{PYPI_NAME}-{VERSION}-pypi'
    squawk('Removing', pypi_build_dir)
    rmtree(pypi_build_dir, ignore_errors=True)

    run(['git', 'clone', '.', pypi_build_dir])
    run(['python', 'setup.py', 'sdist', 'bdist_wheel'], cwd=pypi_build_dir)

    squawk('Moving build artifacts to', PYPI_DIST_DIR)
    PYPI_DIST_DIR.mkdir(parents=True, exist_ok=True)
    for file in (pypi_build_dir / 'dist').glob('*'):
        new_path = PYPI_DIST_DIR / file.name
        print(file, '->', new_path)
        file.rename(new_path)


@task
def build_conda(c):
    """Build the conda package."""
    channels = ['-c'] * len(CHANNELS) * 2
    channels[1::2] = CHANNELS

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    run(['conda', CONDABUILD, *channels, '--output-folder', DIST_DIR, 'pkg'])


@task(pre=[build_pypi, build_conda])
def build(c):
    """Build all distribution packages."""


#---------------------------------------
# Upload
#---------------------------------------
@task
def upload_pypi(c):
    """Upload PyPi package."""
    files = PYPI_DIST_DIR.glob('*')
    run(['twine', 'upload', *files])


@task
def upload_conda(c):
    """Upload conda package."""
    file = DIST_DIR / 'noarch' / f'{NAME}-{VERSION}-py_0.tar.bz2'
    run(['anaconda', 'upload', file])


@task(pre=[upload_pypi, upload_conda])
def upload(c):
    """Upload packages to PyPi and anaconda.org."""


#===============================================================================
# Utilities
#===============================================================================
def squawk(*args, sep=None, end=None, file=None):
    if file is None:
        file = sys.stderr

    if _COLOR:
        print(Fore.BLUE + str(args[0]),
              *args[1:],
              Style.RESET_ALL,
              sep=sep,
              end=end,
              file=file)
    else:
        print(*args, sep=sep, end=end, file=file)


def run(args, check=True, cwd=None, echo=ECHO):
    args = list(map(str, args))
    if echo:
        squawk('Running', args)
    return sub.run(args, check=check, cwd=cwd)
