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
from miscoto import query, sbml, commons, utils
import time
###############################################################################
#
message = """
Compute the scope and target produciblity of a host (optional) and the added-value
of a microbiome regarding scope and target producibility. The microbiome result part
gives the targets and compounds that are producible providing cooperation occurs
within the community of host + all symbionts and that were not producible with
the host alone.
Computation from SBML models or an instance pre-created with miscoto_instance.py
"""

requires = """
requires PyASP package: "pip install PyASP"
"""

pusage="""
**1** from SBML files \n
python miscoto_scopes.py -m host.sbml -b symbiont_directory -s seeds.sbml -t targets.sbml
\n
**2** from a pre-computed instance with possibly (additional) seeds or targets \n
python miscoto_scopes.py -a instance.lp [-s seeds.sbml] [-t targets.sbml]
"""
#
###############################################################################

if __name__ == '__main__':

    start_time = time.time()
    parser = argparse.ArgumentParser(description=message, usage=pusage, epilog=requires)
    #parser.add_argument("-h", "--help",
    #                    help="display this message and exit", required=False)
    parser.add_argument("-a", "--asp",
                        help="instance if already created with miscoto_instance", required=False)
    parser.add_argument("-m", "--modelhost",
                        help="host model in SBML format, ignored if -a instance is provided",
                        required=False)
    parser.add_argument("-b", "--bactsymbionts",
                        help="directory of symbionts models, all in sbml format, ignored if -a instance is provided",
                        required=False)
    parser.add_argument("-s", "--seeds",
                        help="seeds in SBML format",
                        required=False)
    parser.add_argument("-t", "--targets",
                        help="targets in SBML format",
                        required=False)



    args = parser.parse_args()

    # case 1: instance is provided, just read targets and seeds if given
    if args.asp:
        delete_lp_instance = False
        lp_instance_file = args.asp
        print("Instance provided, only seeds and targets will be added if given")
        if args.targets:
            targets_sbml = args.targets
            print('Reading targets from '+ targets_sbml)
            targetsfacts = sbml.readSBMLspecies(targets_sbml, 'target')
        if args.seeds:
            seeds_sbml = args.seeds
            print('Reading targets from '+ seeds_sbml)
            seedsfacts = sbml.readSBMLspecies(seeds_sbml, 'seed')

            with open(lp_instance_file, "a") as f:
                for elem in targetsfacts:
                    f.write(str(elem) + '.\n')
                for elem in seedsfacts:
                    f.write(str(elem) + '.\n')

    # case 2: read inputs from SBML files
    elif args.bactsymbionts and args.seeds:
        delete_lp_instance = True

        bacterium_met =  args.bactsymbionts
        if args.modelhost:
            draft_sbml = args.modelhost
            print('Reading host network from ' + draft_sbml)
            draftnet = sbml.readSBMLnetwork_symbionts(draft_sbml, 'host_metab_mod')
            draftnet.add(Term('draft', ["\"" + 'host_metab_mod' + "\""]))
        else:
            print('No host provided.')
            draftnet = TermSet()
            # draftnet.add(Term('draft', ["\"" + 'host_metab_mod' + "\""]))

        seeds_sbml = args.seeds
        print('Reading seeds from '+ seeds_sbml)
        seeds = sbml.readSBMLspecies(seeds_sbml, 'seed')
        lp_instance = TermSet(draftnet.union(seeds))

        if args.targets:
            targets_sbml =  args.targets
            print('Reading targets from '+ targets_sbml)
            targets = sbml.readSBMLspecies(targets_sbml, 'target')
            lp_instance = TermSet(lp_instance.union(targets))
        else:
            print("No targets provided.")

        print('Reading bacterial networks from ' + bacterium_met + '...')
        bactfacts = TermSet()
        onlyfiles = [f for f in listdir(bacterium_met) if isfile(join(bacterium_met, f))]
        for bacteria_file in onlyfiles:
            name = os.path.splitext(bacteria_file)[0]
            try:
                one_bact_model = sbml.readSBMLnetwork_symbionts(bacterium_met+'/'+bacteria_file, name)
                bactfacts = TermSet(bactfacts.union(one_bact_model))
                bactfacts.add(Term('bacteria', ["\"" + name + "\""]))
                print('Done for ' + name)
            except:
                print('Could not read file ' + name + ' will ignore it')

        lp_instance = TermSet(lp_instance.union(bactfacts))
        lp_instance_file = lp_instance.to_file()

    else:
        print("ERROR missing input")
        print("\n")
        parser.print_help()
        quit()

    print("Computing scopes...")
    print("\n")
    model = query.get_scopes(lp_instance_file, commons.ASP_SRC_SCOPES)
    host_scope = []
    host_prodtargets = []
    host_unprodtargets = []
    com_scope = []
    comhost_scope = []
    com_prodtargets = []
    com_unprodtargets = []
    for a in model:
        if a.pred() == 'dscope':
            host_scope.append(a.arg(0))
        elif a.pred() == 'dproducible':
            host_prodtargets.append(a.arg(0))
        elif a.pred() == 'dunproducible':
            host_unprodtargets.append(a.arg(0))
        elif a.pred() == 'newscope_microbiome':
            com_scope.append(a.arg(0))
        elif a.pred() == 'newscope_with_host':
            comhost_scope.append(a.arg(0))
        elif a.pred() == 'newlyproducible':
            com_prodtargets.append(a.arg(0))
        elif a.pred() == 'aunproducible':
            com_unprodtargets.append(a.arg(0))

    if args.modelhost or args.asp:
        print('*** HOST model producibility check ***')

        print('Host producible targets => ' + str(len(host_prodtargets)))
        print("\n".join(host_prodtargets))
        print('\n')

        print('Host unproducible targets => ' + str(len(host_unprodtargets)))
        print("\n".join(host_unprodtargets))
        print('\n')

        print('Host scope => ' + str(len(host_scope)))
        print("\n".join(host_scope))
        print('\n')

    print('*** MICROBIOME added-value ***')
    print('Microbiome only producible targets => ' + str(len(com_prodtargets)))
    print("\n".join(com_prodtargets))
    print('\n')

    print('Microbiome unproducible targets => ' + str(len(com_unprodtargets)))
    print("\n".join(com_unprodtargets))
    print('\n')

    if args.modelhost or args.asp:
        print('Microbiome only (host + symbionts) scope (host metabolites only producible with the microbiome) => ' + str(len(com_scope)))
        print("\n".join(comhost_scope))
        print('\n')
    if args.asp or not args.modelhost:
        print('Microbiome only (symbionts) scope (metabolites only producible with the microbiome) => ' + str(len(com_scope)))
        print("\n".join(com_scope))
        print('\n')

    if delete_lp_instance == True:
        os.unlink(lp_instance_file)

    print("--- %s seconds ---" % (time.time() - start_time))
    utils.clean_up()
    quit()
