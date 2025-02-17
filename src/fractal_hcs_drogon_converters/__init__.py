"""
Package description.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("fractal-hcs-drogon-converters")
except PackageNotFoundError:
    __version__ = "uninstalled"
