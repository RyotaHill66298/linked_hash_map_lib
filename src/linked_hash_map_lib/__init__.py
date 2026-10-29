"""linked_hash_map_lib: a small, dependency-free ordered hash map.

This package exposes a single class, :class:`LinkedHashMap`, from
:mod:`linked_hash_map_lib.core`. Importing the package name directly
returns the class to keep the import ergonomic::

    from linked_hash_map_lib import LinkedHashMap

Rationale for re-exporting here instead of requiring users to type the
full ``linked_hash_map_lib.core.LinkedHashMap`` path: the package has
exactly one public type, so an extra submodule hop buys nothing but
keystrokes.
"""

from .core import LinkedHashMap

__all__ = ["LinkedHashMap"]
