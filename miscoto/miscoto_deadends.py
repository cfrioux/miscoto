#!/usr/bin/env python
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


def run_deadends(lp_instance_file=None, bacteria_dir=None, host_file=None, output_json=None):
    """Computes community scopes
        lp_instance_file ([str], optional): Defaults to None. [ASP facts instance of the problem]
        bacteria_dir ([str], optional): Defaults to None. [directory of bacterial metabolic networks]
        host_file ([str], optional): Defaults to None. [host metabolic network]
        output_json ([str], optional): Defaults to None. [json file for output]

    Returns:
        [dic]: [all information related to scope computation]
    """

    start_time = time.time()
    results = {}
    # case 1: instance is provided, just read targets and seeds if given
    input_instance = False
    if lp_instance_file:
        if not os.path.isfile(lp_instance_file) :
            logger.info('Instance file not found')
            sys.exit(1)

        input_instance = True
        delete_lp_instance = False
        logger.info(
            "Instance provided, only seeds and targets will be added if given")

    # case 2: read inputs from SBML files
    elif bacteria_dir:
        if not os.path.isdir(bacteria_dir):
            logger.info("Symbiont directory not found")
            sys.exit(1)

        delete_lp_instance = True

        if host_file:
            logger.info('Reading host network from ' + host_file)
            try:
                draftnet = sbml.readSBMLnetwork_symbionts_clyngor(host_file, 'host_metab_mod')
            except FileNotFoundError:
                logger.critical('Host file not found')
                sys.exit(1)
            except ParseError:
                logger.critical("Invalid syntax in SBML file: " + host_file)
                sys.exit(1)
            draftnet.add(Atom('draft', ["\"" + 'host_metab_mod' + "\""]))
        else:
            logger.warning('No host provided.')
            draftnet = TermSet()

        lp_instance = TermSet(draftnet)

        if not os.path.isdir(bacteria_dir):
            logger.critical("Symbiont directory not found")
            sys.exit(1)

        lp_instance_file = utils.to_file(lp_instance)

        logger.info('Reading bacterial networks from ' + bacteria_dir + '...')
        bactfacts = TermSet()
        onlyfiles = [f for f in listdir(bacteria_dir) if isfile(join(bacteria_dir, f))]

        if len(onlyfiles) == 0:
            logger.critical('No bacterial networks in ' + bacteria_dir)
            sys.exit(1)

        for bacteria_file in onlyfiles:
            name = os.path.splitext(bacteria_file)[0]
            bacteria_path = os.path.join(bacteria_dir, bacteria_file)
            try:
                one_bact_model = sbml.readSBMLnetwork_symbionts_clyngor(bacteria_path, name)
                one_bact_model.add(Atom('bacteria', ["\"" + name + "\""]))
                utils.to_file(one_bact_model, lp_instance_file)
                logger.info('Done for ' + name)
            except:
                logger.info('Could not read file ' + name + ', will ignore it')

    else:
        logger.critical("ERROR missing input")
        quit()

    logger.info("Computing deadends...")

    model = query.get_deadends(lp_instance_file, commons.ASP_SRC_DEADENDS)

    deadend_np = []
    deadend_nc = []
    for pred in model:
        if pred == 'deadend_np':
            for a in model[pred, 1]:
                deadend_np.append(a[0])
        elif pred == 'deadend_nc':
            for a in model[pred, 1]:
                deadend_nc.append(a[0])

    logger.info('{0} orphan metabolites (metabolites consumed but not produced) in community.'.format(len(deadend_np)))
    logger.info('{0} deadend metabolites (metabolites produced but not consumed) in community.'.format(len(deadend_nc)))

    if delete_lp_instance == True:
        os.unlink(lp_instance_file)

    results['deadend_np'] = deadend_np
    results['deadend_nc'] = deadend_nc

    if output_json:
        utils.to_json(results, output_json)

    logger.info("--- %s seconds ---" % (time.time() - start_time))
    utils.clean_up()

    return results
