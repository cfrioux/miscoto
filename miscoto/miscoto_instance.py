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
from miscoto import utils, sbml
from os import listdir
from os.path import isfile, join
from xml.etree.ElementTree import ParseError
from clyngor.as_pyasp import TermSet, Atom

logger = logging.getLogger(__name__)


def run_instance(bacteria_dir=None, seeds_file=None, host_file=None, targets_file=None, output=None):
    """Creates ASP facts instance to give as input to mincom or scopes
        bacteria_dir ([str], optional): Defaults to None. [directory of bacterial metabolic networks]
        seeds_file ([str], optional): Defaults to None. [seeds file]
        host_file ([str], optional): Defaults to None. [host metabolic network]
        targets_file ([str], optional): Defaults to None. [targets file]
        output ([str], optional): Defaults to None. [output file]

    Returns:
        [str]: [output file]
    """
    start_time = time.time()
    if not bacteria_dir or not seeds_file:
        logger.critical("Symbionts and seeds are required minimal inputs")
        sys.exit(1)
    if host_file:
        logger.info('Reading host network from ' + host_file)
        try:
            draftnet = sbml.readSBMLnetwork_symbionts_clyngor(host_file, 'host_metab_mod')
        except FileNotFoundError:
            logger.critical('Host file not found')
            sys.exit(1)
        except ParseError:
            logger.critical("Invalid syntax in SBML file: "+host_file)
            sys.exit(1)
        draftnet.add(Atom('draft', ["\"" + 'host_metab_mod' + "\""]))
    else:
        logger.warning('No host provided')
        draftnet = TermSet()
    logger.info('Reading seeds from ' + seeds_file)
    try:
        seeds = sbml.readSBMLspecies_clyngor(seeds_file, 'seed')
    except FileNotFoundError:
        logger.critical('Seeds file not found')
        sys.exit(1)
    except ParseError:
        logger.critical("Invalid syntax in SBML file: "+seeds_file)
        sys.exit(1)
    lp_instance = TermSet(draftnet.union(seeds))

    if targets_file:
        logger.info('Reading targets from ' + targets_file)
        try:
            targets = sbml.readSBMLspecies_clyngor(targets_file, 'target')
        except FileNotFoundError:
            logger.critical('Targets file not found')
            sys.exit(1)
        except ParseError:
            logger.critical("Invalid syntax in SBML file: "+targets_file)
            sys.exit(1)
        lp_instance = TermSet(lp_instance.union(targets))

    if not os.path.isdir(bacteria_dir):
        logger.critical("Symbiont directory not found")
        sys.exit(1)

    if output:
        #clear the file
        open(output, 'w').close()
        #add the content of seeds and/or targets
        all_networks_file = utils.to_file(lp_instance,output)
    else:
        all_networks_file = utils.to_file(lp_instance)

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
            utils.to_file(one_bact_model, all_networks_file)
            logger.info('Done for ' + name)
        except:
            logger.info('Could not read file ' + name + ' will ignore it')

    logger.info("Instance created: " + os.path.abspath(all_networks_file))

    logger.info("--- %s seconds ---" % (time.time() - start_time))
    utils.clean_up()

    return all_networks_file
