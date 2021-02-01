#!python
# -*- coding: utf-8 -*-

# Copyright (C) 2018-2021 Clémence Frioux & Arnaud Belcour - Inria Dyliss - Pleiade
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>

import json
import os
import tempfile

def clean_up() :
    if os.path.isfile("parser.out"): os.remove("parser.out")
    if os.path.isfile("parsetab.py"): os.remove("parsetab.py")
    if os.path.isfile("asp_py_lextab.py"): os.remove("asp_py_lextab.py")
    if os.path.isfile("asp_py_lextab.pyc"): os.remove("asp_py_lextab.pyc")
    if os.path.isfile("asp_py_parsetab.py"): os.remove("asp_py_parsetab.py")
    if os.path.isfile("asp_py_parsetab.pyc"): os.remove("asp_py_parsetab.pyc")


def to_file(termset, outputfile=None):
    """Append the content of the TermSet into a file
    
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


def to_json(input_dictionary, output_json):
    """write the content of miscoto results into a json.
    As results of opt_sol are already in the dictionary delete one_model.

    Args:
        input_dictionary (dict): MiSCoTo dictionary results
        outputfile (str): name of the output file
    """
    def remap_keys(k,v):
        return {'what':v, 'from_to': k}

    def alter_dict_optsol(input_dictionary, k):
        # save the keys/values
        temp = input_dictionary[k]
        # del the old dict
        del input_dictionary[k]
        # prepare new data structure:
        input_dictionary[k] = {}
        # remap the information
        for frozenset_key in temp:
            if isinstance(frozenset_key, str) and '/' not in frozenset_key:
                if frozenset_key == "target_producer_coop_selectedcom":
                    target_producers = {}
                    for element in temp[frozenset_key]:
                        if element[1] not in target_producers:
                            target_producers[element[1]] = [element[0]]
                        else:
                            target_producers[element[1]].append(element[0])
                    input_dictionary[k][frozenset_key] = target_producers
                else:
                    input_dictionary[k][frozenset_key] = []
                    for frozenset_elements in temp[frozenset_key]:
                        input_dictionary[k][frozenset_key].extend([frozenset_element for frozenset_element in frozenset_elements])

    def alter_dict_enum(input_dictionary, k):
        # save the keys/values
        temp = input_dictionary[k]
        # del the old dict
        del input_dictionary[k]
        # prepare new data structure:
        input_dictionary[k] = {}
        # remap the information
        for solnumber in temp:
            input_dictionary[k][solnumber] = []
            for elem in temp[solnumber]:
                input_dictionary[k][solnumber].append(remap_keys(elem, temp[solnumber][elem]))
    
    def alter_dict(input_dictionary, k):
        # save the keys/values
        temp = input_dictionary[k]
        # del the old dict
        del input_dictionary[k]
        # prepare new data structure:
        input_dictionary[k] = {}
        # remap the information
        input_dictionary[k] = []
        for elem in temp:
            input_dictionary[k].append(remap_keys(elem, temp[elem]))

    if 'one_model' in input_dictionary:
        alter_dict_optsol(input_dictionary, 'one_model')

    if 'enum_exchanged' in input_dictionary:
        alter_dict_enum(input_dictionary, 'enum_exchanged')

    if 'union_exchanged' in input_dictionary:
        alter_dict(input_dictionary, 'union_exchanged')
    
    if 'inter_exchanged' in input_dictionary:
        alter_dict(input_dictionary, 'inter_exchanged')
    
    if 'exchanged' in input_dictionary:
        alter_dict(input_dictionary, 'exchanged')

    if 'union_bacteria' in input_dictionary and 'inter_bacteria' in input_dictionary:
        input_dictionary['key_species'] = input_dictionary['union_bacteria']
        input_dictionary['essential_symbionts'] = input_dictionary['inter_bacteria']
        input_dictionary['alternative_symbionts'] = list(set(input_dictionary['union_bacteria']) - set(input_dictionary['inter_bacteria']))

    with open(output_json, 'w') as outfile:
        outfile.write(json.dumps(input_dictionary, indent=4, sort_keys=True))