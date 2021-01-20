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
from xml.etree.ElementTree import ParseError
from clyngor.as_pyasp import TermSet, Atom

logger = logging.getLogger(__name__)


def run_focus(seeds_file:str, bacteria_dir:str, focus_bact:list, output_json:str=None):
    """Computes community scopes
        seeds_file [str]: seeds file
        bacteria_dir [str]: directory of bacterial metabolic networks
        focus_bact [list]: basename of microbe of interest
        output_json ([str], optional): Defaults to None. [json file for output]
    
    Returns:
        [dic]: [all information related to focus computation]
    """
    start_time = time.time()
    results = {}
    # case 1: instance is provided, just read targets and seeds if given
    input_instance = False

    # read seeds
    logger.info('Reading seeds from ' + seeds_file)
    try:
        seedsfacts = sbml.readSBMLspecies_clyngor(seeds_file, 'seed')
    except FileNotFoundError:
        logger.critical('Seeds file not found')
        sys.exit(1)
    except ParseError:
        logger.critical("Invalid syntax in SBML file: " + seeds_file)
        sys.exit(1)
        
    lp_instance_file = utils.to_file(seedsfacts)

    # add the name of microbe of interest in the instance file
    with open(lp_instance_file, "a") as f:
        for ts in focus_bact:
            f.write(f'target_species("{ts}").\n')

    # read bacterial metabolic networks from SBML files
    if not os.path.isdir(bacteria_dir):
        logger.info("Symbiont directory not found")
        sys.exit(1)

    logger.info('Reading bacterial networks from ' + bacteria_dir + '...')
    onlyfiles = [f for f in listdir(bacteria_dir) if isfile(join(bacteria_dir, f))]

    if len(onlyfiles) == 0:
        logger.critical('No bacterial networks in ' + bacteria_dir)
        sys.exit(1)

    # keep the names of all bacteria that are in the symbiont directory
    all_bacteria_names = []

    for bacteria_file in onlyfiles:
        name = os.path.splitext(bacteria_file)[0]
        all_bacteria_names.append(name)
        bacteria_path = os.path.join(bacteria_dir, bacteria_file)
        try:
            one_bact_model = sbml.readSBMLnetwork_symbionts_clyngor(bacteria_path, name)
            one_bact_model.add(Atom('bacteria', ["\"" + name + "\""]))
            utils.to_file(one_bact_model, lp_instance_file)
            logger.info('Done for ' + name)
        except:
            logger.info('Could not read file ' + name + ', will ignore it')

    focus_bact2 = focus_bact
    for ts in focus_bact:
        if not ts in all_bacteria_names:
            logger.warning(f"{ts} is not the basename of a symbiont from {bacteria_dir}. If the file of your network of interest is named `ecoli.xml`, its basename would be `ecoli`. {ts} will be ignored.")
            focus_bact2.remove(ts)
    if len(focus_bact2) == 0:
        logger.critical(f"No element from {focus_bact} could be found in {bacteria_dir}. Please check the input having in mind that if the file of your network of interest is named `ecoli.xml`, its basename would be `ecoli`.")
        sys.exit(1)
        
    # logger.info(os.path.abspath(lp_instance_file))


    logger.info(f"Computing producible metabolites for {focus_bact}...")

    model = query.get_scopes(lp_instance_file, commons.ASP_SRC_FOCUS)

    indiv_produced = {}
    produced_in_com = {}
    newly_prod = {}
    for pred in model:
        if pred == 'iproduced':
            for a in model[pred, 2]:
                if not a[1] in indiv_produced:
                    indiv_produced[a[1]] = [a[0]]
                else:
                    indiv_produced[a[1]].append(a[0])
        elif pred == 'cproduced':
            for a in model[pred, 2]:
                if not a[1] in produced_in_com:
                    produced_in_com[a[1]] = [a[0]]
                else:
                    produced_in_com[a[1]].append(a[0])

    for ts in focus_bact:
        logger.info(f"\n############ {ts}")
        results[ts] = {}
        
        if ts in indiv_produced:
            logger.info(f"* {len(indiv_produced[ts])} metabolites producible by {ts} when alone:")
            logger.info("\n".join(indiv_produced[ts]))
        else:
            logger.info(f"\n* No metabolite producible by {ts} when alone:")
            indiv_produced[ts] = []

        if ts in produced_in_com:
            newly_prod[ts] = list(set(produced_in_com[ts]) - set(indiv_produced[ts]))
            logger.info(f"\n* {len(produced_in_com[ts])} metabolites producible by {ts} in the community: the {len(indiv_produced[ts])} metabolites above + the following {len(newly_prod[ts])} metabolites:")
            logger.info("\n".join(newly_prod[ts]))
        else:
            logger.info(f"\n* No metabolite producible by {ts} in the community")
            produced_in_com[ts] = []
            newly_prod[ts] = []

        results[ts]["produced_alone"] = indiv_produced[ts]
        results[ts]["produced_in_community"] = produced_in_com[ts]
        results[ts]["community_metabolic_gain"] = newly_prod[ts]

    delete_lp_instance = True
    if delete_lp_instance == True:
        os.unlink(lp_instance_file)

    if output_json:
        utils.to_json(results, output_json)

    logger.info("--- %s seconds ---" % (time.time() - start_time))
    utils.clean_up()

    return results
