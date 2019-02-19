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
Compute a community from a microbiome
Inputs: SBML models (symbionts and optionally host) + seeds + targets or an
instance pre-created with miscoto_instance.py,
option: soup = minimal size community in a mixed-bag
framework or minexch = minimal size and minimal exchange community.
Can compute one minimal solution and or union, intersection, enumeration of
all minimal solutions
"""

pusage = """
**1** from SBML files
python miscoto_mincom.py -m host.sbml -b symbiont_directory -s seeds.sbml -t targets.sbml -o option [--intersection] [--union] [--enumeration] [--optsol]
\n
**2** from a pre-computed instance with possibly (additional) seeds or targets
python miscoto_mincom.py -a instance.lp -o option [-s seeds.sbml] [-t targets.sbml] [--intersection] [--union] [--enumeration] [--optsol]
\n
Option -o is either 'soup' or 'minexch' depending on the wanted modeling method
\n
"""

requires = """
requires PyASP package: "pip install PyASP"
"""
#
###############################################################################


def cmd_mincom():
    parser = argparse.ArgumentParser(description=message, usage=pusage, epilog=requires)
    #parser.add_argument("-h", "--help",
    #                    help="display this message and exit", required=False)
    parser.add_argument("-o", "--option",
                        help="subcom option: soup, minexch", required=True)
    parser.add_argument("-a", "--asp",
                        help="instance if already created with miscoto_instance", required=False)
    parser.add_argument("--enumeration",
                        help="enumeration of optimal solutions", required=False, action="store_true")
    parser.add_argument("--intersection",
                        help="intersection of optimal solutions", required=False, action="store_true")
    parser.add_argument("--optsol",
                        help="one optimal solutions", required=False, action="store_true")
    parser.add_argument("--union",
                        help="union of optimal solutions", required=False, action="store_true")
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
    bacterium_met =  args.bactsymbionts
    option = args.option
    lp_instance_file = args.asp
    targets_sbml = args.targets
    seeds_sbml = args.seeds
    draft_sbml = args.modelhost
    intersection_arg = args.intersection
    enumeration = args.enumeration
    union_arg = args.union
    optsol = args.optsol

    run_mincom(bacterium_met, option, lp_instance_file, targets_sbml, seeds_sbml, draft_sbml,
                intersection_arg, enumeration, union_arg, optsol)

def run_mincom(bacterium_met, option, lp_instance_file=None, targets_sbml=None, seeds_sbml=None, draft_sbml=None,
                intersection_arg=None, enumeration=None, union_arg=None, optsol=None):
    start_time = time.time()
    results = {}
    # checking option
    if option == "soup":
        encoding = commons.ASP_SRC_TOPO_SOUP
    elif option == "minexch":
        encoding = commons.ASP_SRC_TOPO_RXN_MIN_EXCH
    else:
        print("invalid option choice")
        print(pusage)
        quit()

    # case 1: instance is provided, just read targets and seeds if given
    if lp_instance_file:
        delete_lp_instance = False
        
        print("Instance provided, only seeds and targets will be added if given")
        if targets_sbml:
            print('Reading targets from '+ targets_sbml)
            targetsfacts = sbml.readSBMLspecies(targets_sbml, 'target')
            # for elem in targetsfacts:
            #     print(str(elem))
        if seeds_sbml:
            print('Reading targets from '+ seeds_sbml)
            seedsfacts = sbml.readSBMLspecies(seeds_sbml, 'seed')
            # for elem in targetsfacts:
            #     print(str(elem))

            with open(lp_instance_file, "a") as f:
                for elem in targetsfacts:
                    f.write(str(elem) + '.\n')
                for elem in seedsfacts:
                    f.write(str(elem) + '.\n')

    # case 2: read inputs from SBML files
    elif bacterium_met and seeds_sbml and targets_sbml:
        delete_lp_instance = True
        
        if draft_sbml:
            print('Reading host network from ' + draft_sbml)
            draftnet = sbml.readSBMLnetwork_symbionts(draft_sbml, 'host_metab_mod')
            draftnet.add(Term('draft', ["\"" + 'host_metab_mod' + "\""]))
        else:
            print('No host provided')
            draftnet = TermSet()
            draftnet.add(Term('draft', ["\"" + 'host_metab_mod' + "\""]))

        
        print('Reading seeds from '+ seeds_sbml)
        seeds = sbml.readSBMLspecies(seeds_sbml, 'seed')
        lp_instance = TermSet(draftnet.union(seeds))

        
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
                bactfacts = TermSet(bactfacts.union(one_bact_model))
                bactfacts.add(Term('bacteria', ["\"" + name + "\""]))
                print('Done for ' + name)
            except:
                print('Could not read file ' + name + ' will ignore it')

        lp_instance = TermSet(lp_instance.union(bactfacts))
        lp_instance_file = lp_instance.to_file()

    else:
        print("ERROR missing input: missing instance or bactsymbionts+targets+seeds")
        print(pusage)
        quit()


    if not optsol and not union_arg and not enumeration and not intersection_arg:
        print("No choice of solution provided. Will compute one optimal solution by default")
        optsol = True

    print('\nFinding optimal communities for target production...')
    #ground the instance
    grounded_instance = query.get_grounded_communities_from_file(lp_instance_file, encoding)


# one solution
    if optsol:
        print('\n*** ONE MINIMAL SOLUTION ***')
        one_model = query.get_communities_from_g(grounded_instance)
        optimum = ','.join(map(str, one_model.score))
        # print(optimum)
        still_unprod = []
        bacteria = []
        newly_prod = []
        exchanged = {}
        for a in one_model:
            if a.pred() == 'unproducible_target':
                still_unprod.append(a.arg(0))
            elif a.pred() == 'newly_producible_target':
                newly_prod.append(a.arg(0))
            elif a.pred() == 'chosen_bacteria':
                bacteria.append(a.arg(0))
            elif a.pred() == 'exchanged':
                if (a.arg(2),a.arg(3)) in exchanged: #exchanged[(from,to)]=[(what,compartto);(what,compartto)]
                    exchanged[(a.arg(2),a.arg(3))].append(a.arg(0))
                else:
                    exchanged[(a.arg(2),a.arg(3))] = []
                    exchanged[(a.arg(2),a.arg(3))].append(a.arg(0))
        print(str(len(newly_prod)) + ' newly producible target(s):')
        print("\n".join(newly_prod))
        print('\n')
        print('Still ' + str(len(still_unprod)) + ' unproducible target(s):')
        print("\n".join(still_unprod))
        print('\nMinimal set of bacteria of size ' + str(len(bacteria)))
        print("\n".join(bacteria))
        if len(exchanged) >= 1:
            print('\nMinimal set of exchanges of size => ' + str(sum(len(v) for v in exchanged.values())))
            for fromto in exchanged:
                print("\texchange(s) from " + fromto[0] + ' to ' + fromto[1] + " = " + ','.join(exchanged[fromto]))
        results['one_model'] = one_model
        results['exchanged'] = exchanged
        results['bacteria'] = bacteria
        results['still_unprod'] = still_unprod
        results['newly_prod'] = newly_prod

# union of solutions
    if union_arg:
        print('\n*** UNION OF MINIMAL SOLUTION ***')
        try:
            if optsol:
                union = query.get_union_communities_from_g(grounded_instance, optimum)
            else:
                union = query.get_union_communities_from_g_noopti(grounded_instance)
        except IndexError:
            print("No stable model was found. Possible troubleshooting: no harmony between names for identical metabolites among host and microbes")
            quit()
        optimum_union = ','.join(map(str, union.score))
        union_bacteria = []
        union_exchanged = {}
        for a in union :
            if a.pred() == 'chosen_bacteria':
                union_bacteria.append(a.arg(0))
            elif a.pred() == 'exchanged':
                if (a.arg(2),a.arg(3)) in union_exchanged: #union_exchanged[(from,to)]=[(what,compartto);(what,compartto)]
                    union_exchanged[(a.arg(2),a.arg(3))].append(a.arg(0))
                else:
                    union_exchanged[(a.arg(2),a.arg(3))] = []
                    union_exchanged[(a.arg(2),a.arg(3))].append(a.arg(0))
        print('Union of minimal sets of bacteria, with optimum = ' + optimum_union + ' comprises ' + str(len(union_bacteria)) + ' bacteria')
        print("\n".join(union_bacteria))
        if len(union_exchanged) >= 1:
            print('\nExchanges in union => ' + str(sum(len(v) for v in union_exchanged.values())))
            for fromto in union_exchanged:
                print('\texchange(s) from ' + fromto[0] + ' to ' + fromto[1] + " = " + ','.join(union_exchanged[fromto]))
        results['union_exchanged'] = union_exchanged
        results['union_bacteria'] = union_bacteria
        results['optimum_union'] = optimum_union

# intersection of solutions
    if intersection_arg:
        print('\n*** INTERSECTION OF MINIMAL SOLUTION ***')
        if optsol:
            intersection = query.get_intersection_communities_from_g(grounded_instance, optimum)
        else:
            intersection = query.get_intersection_communities_from_g_noopti(grounded_instance)
        optimum_inter = ','.join(map(str, intersection.score))
        inter_bacteria = []
        inter_exchanged = {}
        for a in intersection :
            if a.pred() == 'chosen_bacteria':
                inter_bacteria.append(a.arg(0))
            elif a.pred() == 'exchanged':
                if (a.arg(2),a.arg(3)) in inter_exchanged: #inter_exchanged[(from,to)]=[(what,compartto);(what,compartto)]
                    inter_exchanged[(a.arg(2),a.arg(3))].append(a.arg(0))
                else:
                    inter_exchanged[(a.arg(2),a.arg(3))] = []
                    inter_exchanged[(a.arg(2),a.arg(3))].append(a.arg(0))
        print('Intersection of minimal sets of bacteria, with optimum = ' + optimum_inter + ' comprises ' + str(len(inter_bacteria)) + ' bacteria')
        print("\n".join(inter_bacteria))
        if len(inter_exchanged) >= 1:
            print('\nExchanges in intersection => ' + str(sum(len(v) for v in inter_exchanged.values())))
            for fromto in inter_exchanged:
                print('\texchange(s) from ' + fromto[0] + ' to ' + fromto[1] + " = " + ','.join(inter_exchanged[fromto]))
        results['inter_exchanged'] = inter_exchanged
        results['inter_bacteria'] = inter_bacteria
        results['optimum_inter'] = optimum_inter

# enumeration of all solutions
    if enumeration:
        print('\n*** ENUMERATION OF MINIMAL SOLUTION ***')
        if optsol:
            all_models = query.get_all_communities_from_g(grounded_instance, optimum)
        else:
            all_models = query.get_all_communities_from_g_noopti(grounded_instance)
        count = 1
        for model in all_models:
            enum_bacteria = []
            enum_exchanged = {}
            print('\nSolution '+ str(count))
            for a in model :
                if a.pred() == 'chosen_bacteria':
                    enum_bacteria.append(a.arg(0))
                elif a.pred() == 'exchanged':
                    if (a.arg(2),a.arg(3)) in enum_exchanged: #enum_exchanged[(from,to)]=[(what,compartto);(what,compartto)]
                        enum_exchanged[(a.arg(2),a.arg(3))].append(a.arg(0))
                    else:
                        enum_exchanged[(a.arg(2),a.arg(3))] = []
                        enum_exchanged[(a.arg(2),a.arg(3))].append(a.arg(0))
            print("\t" + str(len(enum_bacteria)) + " bacterium(ia) in solution " + str(count))
            for elem in enum_bacteria:
                print("\t" + elem)
            if len(enum_exchanged) >= 1:
                print("\t" + str(sum(len(v) for v in enum_exchanged.values())) + " exchange(s) in solution " + str(count))
                for fromto in enum_exchanged:
                    print('\texchange(s) from ' + fromto[0] + ' to ' + fromto[1] + " = " + ','.join(enum_exchanged[fromto]))
            count+=1
        print('\n')
        print("--- %s seconds ---" % (time.time() - start_time))
        utils.clean_up()
        results['all_models'] = all_models
        results['enum_exchanged'] = enum_exchanged
        results['enum_bacteria'] = enum_bacteria

    return results

    if delete_lp_instance == True:
        os.unlink(lp_instance_file)

    print("--- %s seconds ---" % (time.time() - start_time))
    utils.clean_up()
    quit()

if __name__ == '__main__':
    cmd_mincom()