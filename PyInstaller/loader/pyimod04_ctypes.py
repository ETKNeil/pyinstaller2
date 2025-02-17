#-----------------------------------------------------------------------------
# Copyright (c) 2005-2022, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License with exception
# for distributing bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------
"""
Hooks to make ctypes.CDLL, .PyDLL, etc. look in sys._MEIPASS first.
"""

import sys


def install():
    """
    Install the hooks.

    This must be done from a function as opposed to at module-level, because when the module is imported/executed,
    the import machinery is not completely set up yet.
    """

    import os

    try:
        import ctypes
    except ImportError:
        # ctypes is not included in the frozen application
        return

    def _frozen_name(name):
        # If the given (file)name does not exist, fall back to searching for its basename in sys._MEIPASS, where
        # PyInstaller usually collects shared libraries.
        if name and not os.path.isfile(name):
            frozen_name = os.path.join(sys._MEIPASS, os.path.basename(name))
            if os.path.isfile(frozen_name):
                name = frozen_name
        return name

    class PyInstallerImportError(OSError):
        def __init__(self, name):
            self.msg = (
                "Failed to load dynlib/dll %r. Most likely this dynlib/dll was not found when the application "
                "was frozen." % name
            )
            self.args = (self.msg,)

    class PyInstallerCDLL(ctypes.CDLL):
        def __init__(self, name, *args, **kwargs):
            name = _frozen_name(name)
            try:
                super(PyInstallerCDLL,self).__init__(name, *args, **kwargs)
            except Exception as base_error:
                raise PyInstallerImportError(name) # #from base_error

    ctypes.CDLL = PyInstallerCDLL
    ctypes.cdll = ctypes.LibraryLoader(PyInstallerCDLL)

    class PyInstallerPyDLL(ctypes.PyDLL):
        def __init__(self, name, *args, **kwargs):
            name = _frozen_name(name)
            try:
                super(PyInstallerPyDLL,self).__init__(name, *args, **kwargs)
            except Exception as base_error:
                raise PyInstallerImportError(name) ##from base_error

    ctypes.PyDLL = PyInstallerPyDLL
    ctypes.pydll = ctypes.LibraryLoader(PyInstallerPyDLL)

    if sys.platform.startswith('win'):

        class PyInstallerWinDLL(ctypes.WinDLL):
            def __init__(self, name, *args, **kwargs):
                name = _frozen_name(name)
                try:
                    super(PyInstallerWinDLL,self).__init__(name, *args, **kwargs)
                except Exception as base_error:
                    raise PyInstallerImportError(name) ##from base_error

        ctypes.WinDLL = PyInstallerWinDLL
        ctypes.windll = ctypes.LibraryLoader(PyInstallerWinDLL)

        class PyInstallerOleDLL(ctypes.OleDLL):
            def __init__(self, name, *args, **kwargs):
                name = _frozen_name(name)
                try:
                    super(PyInstallerOleDLL,self).__init__(name, *args, **kwargs)
                except Exception as base_error:
                    raise PyInstallerImportError(name) #from base_error

        ctypes.OleDLL = PyInstallerOleDLL
        ctypes.oledll = ctypes.LibraryLoader(PyInstallerOleDLL)


# On Mac OS insert sys._MEIPASS in the first position of the list of paths that ctypes uses to search for libraries.
#
# Note: 'ctypes' module will NOT be bundled with every app because code in this module is not scanned for module
#       dependencies. It is safe to wrap 'ctypes' module into 'try/except ImportError' block.
if sys.platform.startswith('darwin'):
    try:
        from ctypes.macholib import dyld
        dyld.DEFAULT_LIBRARY_FALLBACK.insert(0, sys._MEIPASS)
    except ImportError:
        # Do nothing when module 'ctypes' is not available.
        pass
