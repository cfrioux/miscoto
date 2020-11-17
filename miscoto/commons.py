# -*- coding: utf-8 -*-
"""
Definition of numerous constants, for paths, names, arguments for ASP solvers.
"""

import sys
import os

# Root
ROOT = os.path.dirname(__file__)

# Constants
ASP_FILE_EXTENSION = '.lp'

# Directories (starting from here)
DIR_SOURCES     = ''  # sources are inside the package
DIR_ASP_SOURCES = 'encodings'
DIR_DATA     = os.path.join(*[ROOT , '..', 'data'])  # sources are inside the package

# ASP SOURCES
def __asp_file(name):
    "path to given asp source file name"
    return os.path.join(*[ROOT, DIR_ASP_SOURCES, name + ASP_FILE_EXTENSION])

# Routine
ASP_SRC_SCOPES = __asp_file('scopes')
# Topological subcommunities
ASP_SRC_TOPO_SOUP   = __asp_file('community_soup')
ASP_SRC_TOPO_RXN_MIN_EXCH = __asp_file('community_minexch')
ASP_SRC_TOPO_RXN_MIN_EXCH_NOHOST = __asp_file('community_minexch_nohost')
# Topological exchanges
# ASP_SRC_TRANSP   = __asp_file('transported_metabolites')


def basename(filepath):
    """Return the basename of given filepath.
    >>> basename('~/an/interesting/file.lp')
    'file'
    """
    return os.path.splitext(os.path.basename(filepath))[0]

def extension(filepath):
    """Return the extension of given filepath.
    >>> extension('~/an/interesting/file.lp')
    'lp'
    >>> extension('nothing')
    ''
    >>> extension('nothing.important')
    'important'
    """
    return os.path.splitext(os.path.basename(filepath))[1][1:]

def is_valid_path(filepath):
    """True if given filepath is a valid one (a file exists, or could exists)"""
    if filepath and not os.access(filepath, os.W_OK):
        try:
            open(filepath, 'w').close()
            os.unlink(filepath)
            return True
        except OSError:
            return False
    else:  # path is accessible
        return True
