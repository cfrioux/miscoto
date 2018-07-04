#!/usr/bin/env python
# Copyright (c) 2018, Clemence Frioux <clemence.frioux@inria.fr>
#
# This file is part of miscoto.
#
# meneco is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# meneco is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with meneco.  If not, see <http://www.gnu.org/licenses/>.
# -*- coding: utf-8 -*-

import argparse
import sys
import os
from pyasp.asp import *
from os import listdir
from os.path import isfile, join
from miscoto import utils, sbml
import time
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


if __name__ == '__main__':

    start_time = time.time()
    parser = argparse.ArgumentParser(description=message, epilog=requires)
    #parser.add_argument("-h", "--help",
    #                    help="display this message and exit", required=False)
    parser.add_argument("-m", "--modelhost",
                        help="host metabolic network in SBML format", required=False)
    parser.add_argument("-s", "--seeds",
                        help="seeds in SBML format", required=True)
    parser.add_argument("-t", "--targets",
                        help="targets in SBML format", required=False)
    parser.add_argument("-b", "--bactsymbionts",
                        help="directory of symbionts models, all in sbml format", required=True)
    parser.add_argument("-o", "--output",
                        help="output file for instance", required=False)



    args = parser.parse_args()

    bacterium_met =  args.bactsymbionts

    if args.modelhost:
        draft_sbml = args.modelhost
        print('Reading host network from ' + draft_sbml)
        draftnet = sbml.readSBMLnetwork_symbionts(draft_sbml, 'host_metab_mod')
        draftnet.add(Term('draft', ["\"" + 'host_metab_mod' + "\""]))
    else:
        print('No host provided')
        draftnet = TermSet()
        draftnet.add(Term('draft', ["\"" + 'host_metab_mod' + "\""]))

    seeds_sbml = args.seeds
    print('Reading seeds from '+ seeds_sbml)
    seeds = sbml.readSBMLspecies(seeds_sbml, 'seed')
    lp_instance = TermSet(draftnet.union(seeds))

    if args.targets:
        targets_sbml =  args.targets
        print('Reading targets from '+ targets_sbml)
        targets = sbml.readSBMLspecies(targets_sbml, 'target')
        lp_instance = TermSet(lp_instance.union(targets))

    print('Reading bacterial networks from ' + bacterium_met + '...')
    bactfacts = TermSet()
    onlyfiles = [f for f in listdir(bacterium_met) if isfile(join(bacterium_met, f))]
    for bacteria_file in onlyfiles:
        name = os.path.splitext(bacteria_file)[0]
        try:
            one_bact_model = sbml.readSBMLnetwork_symbionts(bacterium_met+'/'+bacteria_file, name)
            # print(one_bact_model)
            bactfacts = TermSet(bactfacts.union(one_bact_model))
            bactfacts.add(Term('bacteria', ["\"" + name + "\""]))
            print('Done for ' + name)
        except:
            print('Could not read file ' + name + ' will ignore it')
    # print(bactfacts)

    lp_instance = TermSet(lp_instance.union(bactfacts))
    if args.output:
        all_networks_file = lp_instance.to_file(args.output)
    else:
        all_networks_file = lp_instance.to_file()
    print(os.path.abspath(all_networks_file))

    print("--- %s seconds ---" % (time.time() - start_time))
    utils.clean_up()
    quit()
