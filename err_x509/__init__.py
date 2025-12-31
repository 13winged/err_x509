"""
err_x509 - Fix Clash x509 SSL certificate errors
"""

__version__ = "1.0.0"
__author__ = "13winged"
__email__ = ""
__url__ = "https://github.com/13winged/err_x509"
__license__ = "MIT"

from .core import X509Fixer
from .cli import main
from . import config

__all__ = ['X509Fixer', 'main', 'config', '__version__']