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

from miscoto import query, sbml, commons, utils
from os import listdir
from os.path import isfile, join
from pyasp.asp import *

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
**1** from SBML2 files \n
python miscoto_scopes.py -m host.sbml -b symbiont_directory -s seeds.sbml -t targets.sbml
\n
**2** from SBML2 files \n
python miscoto_scopes.py -b symbiont_directory -s seeds.sbml -t targets.sbml
\n
**3** from a pre-computed instance with possibly (additional) seeds or targets \n
python miscoto_scopes.py -a instance.lp [-s seeds.sbml] [-t targets.sbml]
"""
#
###############################################################################


def cmd_scopes():
    """runs directly miscoto_scopes from the shell
    """
    parser = argparse.ArgumentParser(description=message, usage=pusage, epilog=requires)
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
    lp_instance_file_arg = args.asp
    targets_sbml = args.targets
    seeds_sbml = args.seeds
    bacterium_met =  args.bactsymbionts
    draft_sbml = args.modelhost
    run_scopes(lp_instance_file_arg, targets_sbml, seeds_sbml, bacterium_met, draft_sbml)

def run_scopes(lp_instance_file=None, targets_file=None, seeds_file=None, bacteria_dir=None, host_file=None):
    """[summary]
        lp_instance_file ([str], optional): Defaults to None. [ASP facts instance of the problem]
        targets_file ([str], optional): Defaults to None. [targets file]
        seeds_file ([str], optional): Defaults to None. [seeds file]
        bacteria_dir ([str], optional): Defaults to None. [directory of bacterial metabolic networks]
        host_file ([str], optional): Defaults to None. [host metabolic network]
    
    Returns:
        [dic]: [all information related to scope computation]
    """

    start_time = time.time()
    results = {}
    # case 1: instance is provided, just read targets and seeds if given
    input_instance = False
    if lp_instance_file:
        input_instance = True
        delete_lp_instance = False
        print("Instance provided, only seeds and targets will be added if given")
        if targets_file:
            print('Reading targets from '+ targets_file)
            targetsfacts = sbml.readSBMLspecies(targets_file, 'target')
        if seeds_file:
            print('Reading targets from '+ seeds_file)
            seedsfacts = sbml.readSBMLspecies(seeds_file, 'seed')

            with open(lp_instance_file, "a") as f:
                for elem in targetsfacts:
                    f.write(str(elem) + '.\n')
                for elem in seedsfacts:
                    f.write(str(elem) + '.\n')

    # case 2: read inputs from SBML files
    elif bacteria_dir and seeds_file:
        delete_lp_instance = True

        if host_file:
            print('Reading host network from ' + host_file)
            draftnet = sbml.readSBMLnetwork_symbionts(host_file, 'host_metab_mod')
            draftnet.add(Term('draft', ["\"" + 'host_metab_mod' + "\""]))
        else:
            print('No host provided.')
            draftnet = TermSet()

        print('Reading seeds from '+ seeds_file)
        seeds = sbml.readSBMLspecies(seeds_file, 'seed')
        lp_instance = TermSet(draftnet.union(seeds))

        if targets_file:
            print('Reading targets from '+ targets_file)
            targets = sbml.readSBMLspecies(targets_file, 'target')
            lp_instance = TermSet(lp_instance.union(targets))
        else:
            print("No targets provided.")

        print('Reading bacterial networks from ' + bacteria_dir + '...')
        bactfacts = TermSet()
        onlyfiles = [f for f in listdir(bacteria_dir) if isfile(join(bacteria_dir, f))]
        for bacteria_file in onlyfiles:
            name = os.path.splitext(bacteria_file)[0]
            try:
                one_bact_model = sbml.readSBMLnetwork_symbionts(bacteria_dir+'/'+bacteria_file, name)
                bactfacts = TermSet(bactfacts.union(one_bact_model))
                bactfacts.add(Term('bacteria', ["\"" + name + "\""]))
                print('Done for ' + name)
            except:
                print('Could not read file ' + name + ', will ignore it')

        lp_instance = TermSet(lp_instance.union(bactfacts))
        lp_instance_file = lp_instance.to_file()

    else:
        print("ERROR missing input")
        print("\n")
        print(pusage)
        quit()

    print("Computing scopes...")
    try:
        model = query.get_scopes(lp_instance_file, commons.ASP_SRC_SCOPES)
    except OSError:
        print("Error. Solvers are not properly installed. Please install them again by running 'pip uninstall pyasp' and 'pip install pyasp no-cache-dir'")
        sys.exit(1)
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

    if host_file or input_instance:
        print('*** HOST model producibility check ***')

        print('Host producible targets => ' + str(len(host_prodtargets)))
        print("\n".join(host_prodtargets))
        results['host_prodtargets'] = host_prodtargets

        print('Host unproducible targets => ' + str(len(host_unprodtargets)))
        print("\n".join(host_unprodtargets))
        results['host_unprodtargets'] = host_unprodtargets

        print('Host scope => ' + str(len(host_scope)))
        print("\n".join(host_scope))
        results['host_scope'] = host_scope

    print('*** MICROBIOME added-value ***')
    print('Microbiome only producible targets => ' + str(len(com_prodtargets)))
    print("\n".join(com_prodtargets))
    results['com_prodtargets'] = com_prodtargets

    print('Microbiome unproducible targets => ' + str(len(com_unprodtargets)))
    print("\n".join(com_unprodtargets))
    results['com_unprodtargets'] = com_unprodtargets

    if host_file or input_instance:
        print('Microbiome only (host + symbionts) scope (host metabolites only producible with the microbiome) => ' + str(len(com_scope)))
        print("\n".join(comhost_scope))
        #print('\n')
        results['comhost_scope'] = comhost_scope
    if input_instance or not host_file:
        print('Microbiome only (symbionts) scope (metabolites only producible with the microbiome) => ' + str(len(com_scope)))
        print("\n".join(com_scope))
        #print('\n')
        results['com_scope'] = com_scope

    if delete_lp_instance == True:
        os.unlink(lp_instance_file)

    print("--- %s seconds ---" % (time.time() - start_time))
    utils.clean_up()
    return results

if __name__ == '__main__':
    cmd_scopes()