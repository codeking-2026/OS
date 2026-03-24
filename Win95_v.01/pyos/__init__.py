"""
pyos package
=============

Educational operating system simulator for a single user.

Example usage:
    from pyos.services.kernel import Kernel
    from pyos.ui.shell import Shell

    kernel = Kernel()
    shell = Shell(kernel)
    shell.onecmd("ls")
"""

from .services.kernel import Kernel
from .ui.shell import Shell

__all__ = ["Kernel", "Shell"]
