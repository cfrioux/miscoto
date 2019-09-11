#!python
# -*- coding: utf-8 -*-
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

def results_to_json(result_generators, output_json):
    for input_dictionary in result_generators:
        output_dictionary = {}

        for data in input_dictionary:
            if data == 'one_model':
                output_dictionary['one_model'] = {}
                one_model_data = input_dictionary[data]
                for input_key in one_model_data:
                    if not isinstance(input_key, tuple):
                        if isinstance(one_model_data[input_key], frozenset):
                            new_value = list(one_model_data[input_key])
                            output_dictionary['one_model'][input_key] = new_value
            elif data == 'all_models':
                output_dictionary['all_models'] = []
                for sub_dict in input_dictionary[data]:
                    if isinstance(sub_dict, dict):
                        for sub_key in sub_dict:
                            sub_dict_out = {}
                            if not isinstance(sub_key, tuple):
                                sub_dict_out[sub_key] = list(sub_dict[sub_key])
                                output_dictionary['all_models'].append(sub_dict_out)
                output_dictionary['all_models'] = tuple(output_dictionary['all_models'])
            if data not in ['one_model', 'all_models']:
                output_dictionary[data] = input_dictionary[data]

    with open(output_json, 'w') as outfile:
        outfile.write(json.dumps(output_dictionary))