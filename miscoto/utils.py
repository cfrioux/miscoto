#!python
# -*- coding: utf-8 -*-
import os
from pyasp.term import *

def clean_up() :
    if os.path.isfile("parser.out"): os.remove("parser.out")
    if os.path.isfile("parsetab.py"): os.remove("parsetab.py")
    if os.path.isfile("asp_py_lextab.py"): os.remove("asp_py_lextab.py")
    if os.path.isfile("asp_py_lextab.pyc"): os.remove("asp_py_lextab.pyc")
    if os.path.isfile("asp_py_parsetab.py"): os.remove("asp_py_parsetab.py")
    if os.path.isfile("asp_py_parsetab.pyc"): os.remove("asp_py_parsetab.pyc")

def to_file(termset, outputfile=None):
    """write the content of the TermSet into a file
    
    Args:
        termset (TermSet): ASP termset
        outputfile (str, optional): Defaults to None. name of the output file
    """
    if outputfile:
        f = open(outputfile, 'a')
    else:
        fd, outputfile = tempfile.mkstemp(suffix='.lp', prefix='miscoto_')
        f = os.fdopen(fd, 'a')
    for t in termset:
        f.write(str(t) + '.\n')
    f.close()
    return outputfile
