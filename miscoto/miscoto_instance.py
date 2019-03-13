#!/usr/bin/env python
# Copyright (c) 2018, Clemence Frioux <clemence.frioux@inria.fr>
#
# This file is part of miscoto.
#
# miscoto is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# miscoto is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with miscoto.  If not, see <http://www.gnu.org/licenses/>.
# -*- coding: utf-8 -*-

import argparse
import sys
import os
import time

from miscoto import utils, sbml
from os import listdir
from os.path import isfile, join
from pyasp.asp import *

###############################################################################
#
message = """
Prepares instance for miscoto. Useful in a benchmark context: pre-calculating
the instance ensures that SBML files do not have to be read again.
Instances are text files that can be modified between runs through multiple
ways, including the use of bash tools
"""

requires = """
requires PyASP package: "pip install PyASP"
"""
#
###############################################################################



def cmd_instance():
    """run miscoto_instance from the shell
    """
    parser = argparse.ArgumentParser(description=message, epilog=requires)
    #parser.add_argument("-h", "--help",
    #                    help="display this message and exit", required=False)
    parser.add_argument("-b", "--bactsymbionts",
                        help="directory of symbionts models, all in sbml format", required=True)
    parser.add_argument("-s", "--seeds",
                        help="seeds in SBML format", required=True)
    parser.add_argument("-m", "--modelhost",
                        help="host metabolic network in SBML format", required=False)
    parser.add_argument("-t", "--targets",
                        help="targets in SBML format", required=False)
    parser.add_argument("-o", "--output",
                        help="output file for instance", required=False)

    args = parser.parse_args()
    bacterium_met =  args.bactsymbionts
    seeds_sbml = args.seeds
    model_host = args.modelhost
    targets_sbml = args.targets
    output = args.output

    run_instance(bacterium_met, seeds_sbml, model_host, targets_sbml, output)

def run_instance(bacteria_dir=None, seeds_file=None, host_file=None, targets_file=None, output=None):
    start_time = time.time()
    if not bacteria_dir or not seeds_file:
        print("Symbionts and seeds are required minimal inputs")
        sys.exit(1)
    if host_file:
        print('Reading host network from ' + host_file)
        try:
            draftnet = sbml.readSBMLnetwork_symbionts(host_file, 'host_metab_mod')
        except FileNotFoundError:
            print('Host file not found')
            sys.exit(1)
        draftnet.add(Term('draft', ["\"" + 'host_metab_mod' + "\""]))
    else:
        print('No host provided')
        draftnet = TermSet()
        draftnet.add(Term('draft', ["\"" + 'host_metab_mod' + "\""]))

    print('Reading seeds from '+ seeds_file)
    try:
        seeds = sbml.readSBMLspecies(seeds_file, 'seed')
    except FileNotFoundError:
        print('Seeds file not found')
        sys.exit(1)
    lp_instance = TermSet(draftnet.union(seeds))

    if targets_file:
        print('Reading targets from '+ targets_file)
        try:
            targets = sbml.readSBMLspecies(targets_file, 'target')
        except FileNotFoundError:
            print('Targets file not found')
            sys.exit(1)
        lp_instance = TermSet(lp_instance.union(targets))

    if not os.path.isdir(bacteria_dir):
        print("Symbiont directory not found")
        sys.exit(1)

    if output:
        #clear the file
        open(output, 'w').close()
        #add the content of seeds and/or targets
        all_networks_file = utils.to_file(lp_instance,output)
    else:
        all_networks_file = utils.to_file(lp_instance)

    print('Reading bacterial networks from ' + bacteria_dir + '...')
    bactfacts = TermSet()
    onlyfiles = [f for f in listdir(bacteria_dir) if isfile(join(bacteria_dir, f))]
    for bacteria_file in onlyfiles:
        name = os.path.splitext(bacteria_file)[0]
        try:
            one_bact_model = sbml.readSBMLnetwork_symbionts(bacteria_dir+'/'+bacteria_file, name)
            one_bact_model.add(Term('bacteria', ["\"" + name + "\""]))
            utils.to_file(one_bact_model, all_networks_file)
            print('Done for ' + name)
        except:
            print('Could not read file ' + name + ' will ignore it')

    print("Instance created: " + os.path.abspath(all_networks_file))

    print("--- %s seconds ---" % (time.time() - start_time))
    utils.clean_up()

    return lp_instance

if __name__ == '__main__':
    cmd_instance()