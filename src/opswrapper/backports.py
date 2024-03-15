"""Backport of the Python 3.12 TemporaryDirectory, which has a
`delete` option to prevent it always cleaning up after itself.

Modified slightly to work on Python 3.9+.

Includes patches from December 2023 (Python 3.13 series).

Original source: https://github.com/python/cpython/blob/29f7eb4859bfc27a4c93f36449ca7d810e13288b/Lib/tempfile.py
"""
import os
import shutil
import types
import warnings
import weakref
from tempfile import mkdtemp


def _dont_follow_symlinks(func, path, *args):
    # Pass follow_symlinks=False, unless not supported on this platform.
    if func in os.supports_follow_symlinks:
        func(path, *args, follow_symlinks=False)
    elif not os.path.islink(path):
        func(path, *args)


def _resetperms(path):
    try:
        chflags = os.chflags
    except AttributeError:
        pass
    else:
        _dont_follow_symlinks(chflags, path, 0)
    _dont_follow_symlinks(os.chmod, path, 0o700)


class TemporaryDirectory:
    """Create and return a temporary directory.  This has the same
    behavior as mkdtemp but can be used as a context manager.  For
    example:

        with TemporaryDirectory() as tmpdir:
            ...

    Upon exiting the context, the directory and everything contained
    in it are removed (unless delete=False is passed or an exception
    is raised during cleanup and ignore_cleanup_errors is not True).

    Optional Arguments:
        suffix - A str suffix for the directory name.  (see mkdtemp)
        prefix - A str prefix for the directory name.  (see mkdtemp)
        dir - A directory to create this temp dir in.  (see mkdtemp)
        ignore_cleanup_errors - False; ignore exceptions during cleanup?
        delete - True; whether the directory is automatically deleted.
    """

    def __init__(
        self,
        suffix=None,
        prefix=None,
        dir=None,
        ignore_cleanup_errors=False,
        *,
        delete=True,
    ):
        # PCT: 3.12 modifies mkdtemp to always return an absolute path,
        # not sure if anything in here relies on that behavior. Replicate
        # for consistency.
        self.name = os.path.abspath(mkdtemp(suffix, prefix, dir))
        self._ignore_cleanup_errors = ignore_cleanup_errors
        self._delete = delete
        self._finalizer = weakref.finalize(
            self,
            self._cleanup,
            self.name,
            warn_message="Implicitly cleaning up {!r}".format(self),
            ignore_errors=self._ignore_cleanup_errors,
            delete=self._delete,
        )

    @classmethod
    def _rmtree(cls, name, ignore_errors=False, repeated=False):
        def onerror(func, path, exc_info):
            exc = exc_info[0]
            if isinstance(exc, PermissionError):
                if repeated and path == name:
                    if ignore_errors:
                        return
                    raise

                try:
                    if path != name:
                        _resetperms(os.path.dirname(path))
                    _resetperms(path)

                    try:
                        os.unlink(path)
                    except IsADirectoryError:
                        cls._rmtree(path, ignore_errors=ignore_errors)
                    except PermissionError:
                        # The PermissionError handler was originally added for
                        # FreeBSD in directories, but it seems that it is raised
                        # on Windows too.
                        # bpo-43153: Calling _rmtree again may
                        # raise NotADirectoryError and mask the PermissionError.
                        # So we must re-raise the current PermissionError if
                        # path is not a directory.
                        if not os.path.isdir(path) or os.path.isjunction(path):
                            if ignore_errors:
                                return
                            raise
                        cls._rmtree(
                            path, ignore_errors=ignore_errors, repeated=(path == name)
                        )
                except FileNotFoundError:
                    pass
            elif isinstance(exc, FileNotFoundError):
                pass
            elif not ignore_errors:
                raise

        shutil.rmtree(name, onerror=onerror)

    @classmethod
    def _cleanup(cls, name, warn_message, ignore_errors=False, delete=True):
        if delete:
            cls._rmtree(name, ignore_errors=ignore_errors)
            warnings.warn(warn_message, ResourceWarning)  # noqa: B028

    def __repr__(self):
        return "<{} {!r}>".format(self.__class__.__name__, self.name)

    def __enter__(self):
        return self.name

    def __exit__(self, exc, value, tb):
        if self._delete:
            self.cleanup()

    def cleanup(self):
        if self._finalizer.detach() or os.path.exists(self.name):
            self._rmtree(self.name, ignore_errors=self._ignore_cleanup_errors)

    __class_getitem__ = classmethod(types.GenericAlias)
