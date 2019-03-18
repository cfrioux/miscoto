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
import logging
from miscoto import query, sbml, commons, utils
from os import listdir
from os.path import isfile, join
from pyasp.asp import *
from xml.etree.ElementTree import ParseError

logger = logging.getLogger(__name__)

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
    """run directly miscoto_mincom from the shell
    """
    parser = argparse.ArgumentParser(description=message, usage=pusage, epilog=requires)
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
    if args.intersection:
        intersection_arg = True
    else:
        intersection_arg = False
    if args.enumeration:
        enumeration_arg = True
    else:
        enumeration_arg = False
    if args.union:
        union_arg = True
    else:
        union_arg = False
    if args.optsol:
        optsol = True
    else:
        optsol = False

    run_mincom(option, bacterium_met, lp_instance_file, targets_sbml, seeds_sbml, draft_sbml,
                intersection_arg, enumeration_arg, union_arg, optsol)

def run_mincom(option=None, bacteria_dir=None, lp_instance_file=None, targets_file=None, seeds_file=None, host_file=None,
                intersection=False, enumeration=False, union=False, optsol=False):
    """Computes community selections in microbiota
        option (str, optional): Defaults to None. Modeling type: 'soup' for uncompartmentalized, 'minexch' for compartmentalized
        bacteria_dir (str, optional): Defaults to None. directory with symbionts metabolic networks
        lp_instance_file (str, optional): Defaults to None. ASP instance file
        targets_file (str, optional): Defaults to None. targets file
        seeds_file (str, optional): Defaults to None. seeds file
        host_file (str, optional): Defaults to None. host metabolic network file
        intersection (bool, optional): Defaults to False. compute intersection of solutions
        enumeration (bool, optional): Defaults to False. compute enumeration of solutions
        union (bool, optional): Defaults to False. compute union of solutions
        optsol (bool, optional): Defaults to False. compute one optimal solution
    """
    start_time = time.time()
    results = {}
    # checking option
    if option == "soup":
        encoding = commons.ASP_SRC_TOPO_SOUP
    elif option == "minexch":
        encoding = commons.ASP_SRC_TOPO_RXN_MIN_EXCH
    else:
        logger.critical("invalid option choice")
        logger.info(pusage)
        quit()

    # case 1: instance is provided, just read targets and seeds if given
    if lp_instance_file:
        if not os.path.isfile(lp_instance_file) :
            logger.critical('Instance file not found')
            sys.exit(1)

        delete_lp_instance = False

        logger.info(
            "Instance provided, only seeds and targets will be added if given")
        if targets_file:
            logger.info('Reading targets from ' + targets_file)
            try:
                targetsfacts = sbml.readSBMLspecies(targets_file, 'target')
            except FileNotFoundError:
                logger.critical('Targets file not found')
                sys.exit(1)
            except ParseError:
                logger.critical("Invalid syntax in SBML file: "+targets_file)
                sys.exit(1)
        else:
            targetsfacts = TermSet()

        if seeds_file:
            logger.info('Reading targets from ' + seeds_file)
            try:
                seedsfacts = sbml.readSBMLspecies(seeds_file, 'seed')
            except FileNotFoundError:
                logger.critical('Seeds file not found')
                sys.exit(1)
            except ParseError:
                logger.critical("Invalid syntax in SBML file: "+seeds_file)
                sys.exit(1)
        else:
            seedsfacts = TermSet()

        with open(lp_instance_file, "a") as f:
            for elem in targetsfacts:
                f.write(str(elem) + '.\n')
            for elem in seedsfacts:
                f.write(str(elem) + '.\n')

    # case 2: read inputs from SBML files
    elif bacteria_dir and seeds_file and targets_file:
        if not os.path.isdir(bacteria_dir):
            logger.critical("Symbiont directory not found")
            sys.exit(1)

        delete_lp_instance = True

        if host_file:
            logger.info('Reading host network from ' + host_file)
            try:
                draftnet = sbml.readSBMLnetwork_symbionts(host_file, 'host_metab_mod')
            except FileNotFoundError:
                logger.critical('Host file not found')
                sys.exit(1)
            except ParseError:
                logger.critical("Invalid syntax in SBML file: "+host_file)
                sys.exit(1)
            draftnet.add(Term('draft', ["\"" + 'host_metab_mod' + "\""]))
        else:
            logger.warning('No host provided')
            draftnet = TermSet()
            draftnet.add(Term('draft', ["\"" + 'host_metab_mod' + "\""]))

        logger.info('Reading seeds from ' + seeds_file)
        try:
            seeds = sbml.readSBMLspecies(seeds_file, 'seed')
        except FileNotFoundError:
            logger.critical('Targets file not found')
            sys.exit(1)
        except ParseError:
            logger.critical("Invalid syntax in SBML file: "+seeds_file)
            sys.exit(1)
        lp_instance = TermSet(draftnet.union(seeds))

        logger.info('Reading targets from '+ targets_file)
        try:
            targets = sbml.readSBMLspecies(targets_file, 'target')
        except FileNotFoundError:
            logger.critical('Targets file not found')
            sys.exit(1)
        except ParseError:
            logger.critical("Invalid syntax in SBML file: "+targets_file)
            sys.exit(1)
        lp_instance = TermSet(lp_instance.union(targets))

        lp_instance_file = utils.to_file(lp_instance)

        logger.info('Reading bacterial networks from ' + bacteria_dir + '...')
        bactfacts = TermSet()
        onlyfiles = [f for f in listdir(bacteria_dir) if isfile(join(bacteria_dir, f))]
        for bacteria_file in onlyfiles:
            name = os.path.splitext(bacteria_file)[0]
            try:
                one_bact_model = sbml.readSBMLnetwork_symbionts(bacteria_dir+'/'+bacteria_file, name)
                one_bact_model.add(Term('bacteria', ["\"" + name + "\""]))
                utils.to_file(one_bact_model, lp_instance_file)
                logger.info('Done for ' + name)
            except:
                logger.info('Could not read file ' + name + ' will ignore it')

    else:
        logger.info(
            "ERROR missing input: missing instance or symbionts/targets/seeds")
        logger.info(pusage)
        quit()

    if not optsol and not union and not enumeration and not intersection:
        logger.info(
            "No choice of solution provided. Will compute one optimal solution by default"
        )
        optsol = True

    logger.info('\nFinding optimal communities for target production...')
    #ground the instance
    try:
        grounded_instance = query.get_grounded_communities_from_file(lp_instance_file, encoding)
    except OSError:
        logger.critical(
            "Error. Possible reason: solvers are not properly installed. Please install them again by running 'pip uninstall pyasp' and 'pip install pyasp --no-cache-dir'"
        )
        sys.exit(1)


# one solution
    if optsol:
        logger.info('\n*** ONE MINIMAL SOLUTION ***')
        one_model = query.get_communities_from_g(grounded_instance)
        optimum = ','.join(map(str, one_model.score))
        still_unprod = []
        bacteria = []
        newly_prod = []
        exchanged = {}
        for a in one_model:
            if a.pred() == 'unproducible_target':
                still_unprod.append(a.arg(0).rstrip('"').lstrip('"'))
            elif a.pred() == 'newly_producible_target':
                newly_prod.append(a.arg(0).rstrip('"').lstrip('"'))
            elif a.pred() == 'chosen_bacteria':
                bacteria.append(a.arg(0).rstrip('"').lstrip('"'))
            elif a.pred() == 'exchanged':
                if (
                        a.arg(2).rstrip('"').lstrip('"'),
                        a.arg(3).rstrip('"').lstrip('"')
                ) in exchanged:  #exchanged[(from,to)]=[(what,compartto);(what,compartto)]
                    exchanged[(a.arg(2).rstrip('"').lstrip('"'),
                               a.arg(3))].append(
                                   a.arg(0).rstrip('"').lstrip('"'))
                else:
                    exchanged[(a.arg(2).rstrip('"').lstrip('"'),
                               a.arg(3)).rstrip('"').lstrip('"')] = []
                    exchanged[(a.arg(2).rstrip('"').lstrip('"'),
                               a.arg(3)).rstrip('"').lstrip('"')].append(
                                   a.arg(0).rstrip('"').lstrip('"'))
        logger.info(str(len(newly_prod)) + ' newly producible target(s):')
        logger.info("\n".join(newly_prod))
        logger.info('Still ' + str(len(still_unprod)) + ' unproducible target(s):')
        logger.info("\n".join(still_unprod))
        logger.info('Minimal set of bacteria of size ' + str(len(bacteria)))
        logger.info("\n".join(bacteria))
        if len(exchanged) >= 1:
            logger.info('Minimal set of exchanges of size => ' +
                        str(sum(len(v) for v in exchanged.values())))
            for fromto in exchanged:
                logger.info("\texchange(s) from " + fromto[0] + ' to ' +
                            fromto[1] + " = " + ','.join(exchanged[fromto]))
        results['one_model'] = one_model
        results['exchanged'] = exchanged
        results['bacteria'] = bacteria
        results['still_unprod'] = still_unprod
        results['newly_prod'] = newly_prod

# union of solutions
    if union:
        logger.info('\n*** UNION OF MINIMAL SOLUTION ***')
        try:
            if optsol:
                union_m = query.get_union_communities_from_g(grounded_instance, optimum)
            else:
                union_m = query.get_union_communities_from_g_noopti(grounded_instance)
        except IndexError:
            logger.error(
                "No stable model was found. Possible troubleshooting: no harmony between names for identical metabolites among host and microbes"
            )
            quit()
        optimum_union = ','.join(map(str, union_m.score))
        union_bacteria = []
        union_exchanged = {}
        for a in union_m :
            if a.pred() == 'chosen_bacteria':
                union_bacteria.append(a.arg(0).rstrip('"').lstrip('"'))
            elif a.pred() == 'exchanged':
                if (
                        a.arg(2).rstrip('"').lstrip('"'),
                        a.arg(3).rstrip('"').lstrip('"')
                ) in union_exchanged:  #union_exchanged[(from,to)]=[(what,compartto);(what,compartto)]
                    union_exchanged[(a.arg(2).rstrip('"').lstrip('"'),
                                     a.arg(3).rstrip('"').lstrip('"'))].append(
                                         a.arg(0).rstrip('"').lstrip('"'))
                else:
                    union_exchanged[(a.arg(2).rstrip('"').lstrip('"'),
                                     a.arg(3).rstrip('"').lstrip('"'))] = []
                    union_exchanged[(a.arg(2).rstrip('"').lstrip('"'),
                                     a.arg(3).rstrip('"').lstrip('"'))].append(
                                         a.arg(0).rstrip('"').lstrip('"'))
        logger.info('Union of minimal sets of bacteria, with optimum = ' +
                    optimum_union + ' comprises ' + str(len(union_bacteria)) +
                    ' bacteria')
        logger.info("\n".join(union_bacteria))
        if len(union_exchanged) >= 1:
            logger.info('\nExchanges in union => ' +
                        str(sum(len(v) for v in union_exchanged.values())))
            for fromto in union_exchanged:
                logger.info('\texchange(s) from ' + fromto[0] + ' to ' +
                            fromto[1] + " = " +
                            ','.join(union_exchanged[fromto]))
        results['union_exchanged'] = union_exchanged
        results['union_bacteria'] = union_bacteria
        results['optimum_union'] = optimum_union

# intersection of solutions
    if intersection:
        logger.info('\n*** INTERSECTION OF MINIMAL SOLUTION ***')
        if optsol:
            intersection_m = query.get_intersection_communities_from_g(grounded_instance, optimum)
        else:
            intersection_m = query.get_intersection_communities_from_g_noopti(grounded_instance)
        optimum_inter = ','.join(map(str, intersection_m.score))
        inter_bacteria = []
        inter_exchanged = {}
        for a in intersection_m :
            if a.pred() == 'chosen_bacteria':
                inter_bacteria.append(a.arg(0).rstrip('"').lstrip('"'))
            elif a.pred() == 'exchanged':
                if (
                        a.arg(2).rstrip('"').lstrip('"'), a.arg(3).rstrip('"').lstrip('"')
                ) in inter_exchanged:  #inter_exchanged[(from,to)]=[(what,compartto);(what,compartto)]
                    inter_exchanged[(a.arg(2).rstrip('"').lstrip('"'),
                                     a.arg(3).rstrip('"').lstrip('"'))].append(
                                         a.arg(0).rstrip('"').lstrip('"'))
                else:
                    inter_exchanged[(a.arg(2).rstrip('"').lstrip('"'),
                                     a.arg(3).rstrip('"').lstrip('"'))] = []
                    inter_exchanged[(a.arg(2).rstrip('"').lstrip('"'),
                                     a.arg(3).rstrip('"').lstrip('"'))].append(
                                         a.arg(0).rstrip('"').lstrip('"'))
        logger.info('Intersection of minimal sets of bacteria, with optimum = '
                    + optimum_inter + ' comprises ' +
                    str(len(inter_bacteria)) + ' bacteria')
        logger.info("\n".join(inter_bacteria))
        if len(inter_exchanged) >= 1:
            logger.info('\nExchanges in intersection => ' +
                        str(sum(len(v) for v in inter_exchanged.values())))
            for fromto in inter_exchanged:
                logger.info('\texchange(s) from ' + fromto[0] + ' to ' +
                            fromto[1] + " = " +
                            ','.join(inter_exchanged[fromto]))
        results['inter_exchanged'] = inter_exchanged
        results['inter_bacteria'] = inter_bacteria
        results['optimum_inter'] = optimum_inter

# enumeration of all solutions
    if enumeration:
        logger.info('\n*** ENUMERATION OF MINIMAL SOLUTION ***')
        if optsol:
            all_models = query.get_all_communities_from_g(grounded_instance, optimum)
        else:
            all_models = query.get_all_communities_from_g_noopti(grounded_instance)
        count = 1
        for model in all_models:
            enum_bacteria = []
            enum_exchanged = {}
            logger.info('\nSolution ' + str(count))
            for a in model :
                if a.pred() == 'chosen_bacteria':
                    enum_bacteria.append(a.arg(0).rstrip('"').lstrip('"'))
                elif a.pred() == 'exchanged':
                    if (
                            a.arg(2).rstrip('"').lstrip('"'),
                            a.arg(3).rstrip('"').lstrip('"')
                    ) in enum_exchanged:  #enum_exchanged[(from,to)]=[(what,compartto);(what,compartto)]
                        enum_exchanged[(
                            a.arg(2).rstrip('"').lstrip('"'),
                            a.arg(3).rstrip('"').lstrip('"').rstrip('"').lstrip('"'))].append(
                                a.arg(0).rstrip('"').lstrip('"'))
                    else:
                        enum_exchanged[(
                            a.arg(2).rstrip('"').lstrip('"'),
                            a.arg(3).rstrip('"').lstrip('"'))] = []
                        enum_exchanged[(
                            a.arg(2).rstrip('"').lstrip('"'),
                            a.arg(3).rstrip('"').lstrip('"'))].append(
                                a.arg(0).rstrip('"').lstrip('"'))
            logger.info("\t" + str(len(enum_bacteria)) +
                        " bacterium(ia) in solution " + str(count))
            for elem in enum_bacteria:
                logger.info("\t" + elem)
            if len(enum_exchanged) >= 1:
                logger.info("\t" +
                            str(sum(len(v) for v in enum_exchanged.values())) +
                            " exchange(s) in solution " + str(count))
                for fromto in enum_exchanged:
                    logger.info('\texchange(s) from ' + fromto[0] + ' to ' +
                                fromto[1] + " = " +
                                ','.join(enum_exchanged[fromto]))
            count+=1
        results['all_models'] = all_models
        results['enum_exchanged'] = enum_exchanged
        results['enum_bacteria'] = enum_bacteria

    if delete_lp_instance == True:
        os.unlink(lp_instance_file)

    logger.info("--- %s seconds ---" % (time.time() - start_time))
    utils.clean_up()

    return results

if __name__ == '__main__':
    cmd_mincom()