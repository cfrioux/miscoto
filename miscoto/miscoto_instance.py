#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2018-2023 Clémence Frioux & Arnaud Belcour - Inria Dyliss - Pleiade
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

import sys
import os
import time
import logging
from miscoto import utils, sbml
from os import listdir
from os.path import isfile, join
from xml.etree.ElementTree import ParseError
from clyngor.as_pyasp import TermSet, Atom
from multiprocessing import Pool

logger = logging.getLogger(__name__)


def extract_symbiont_data(bacteria_file, bacteria_dir):
    """Create ASP model from SBML file
        bacteria_file (str): Name of the SBML file
        bacteria_dir (str): Defaults to None. [directory of bacterial metabolic networks]

    Returns:
        [TermSet]: Clyngor TermSet containing ASP formatting of SBMl model
    """
    name = os.path.splitext(bacteria_file)[0]
    bacteria_path = os.path.join(bacteria_dir, bacteria_file)

    if utils.is_valid_file(bacteria_path) is True:
        one_bact_model = sbml.readSBMLnetwork_symbionts_clyngor(bacteria_path, name)
        one_bact_model.add(Atom('bacteria', ["\"" + name + "\""]))
        logger.info('Done for ' + name)
        return one_bact_model
    else:
        logger.info('Could not read file ' + name + ' will ignore it')


def run_instance(bacteria_dir=None, seeds_file=None, host_file=None, targets_file=None, output=None, cpu_number=1):
    """Creates ASP facts instance to give as input to mincom, scopes or deadends.
    For mincom, the instance file must contain data from: bacteria_dir, seeds_file and targets_file. Optionally: host_file.
    For scopes, the instance file must contain data from: bacteria_dir and seeds_file. Optionally: host_file.
    For deadends, the instance file must contain data from: bacteria_dir.
        bacteria_dir ([str], optional): Defaults to None. [directory of bacterial metabolic networks]
        seeds_file ([str], optional): Defaults to None. [seeds file]
        host_file ([str], optional): Defaults to None. [host metabolic network]
        targets_file ([str], optional): Defaults to None. [targets file]
        output ([str], optional): Defaults to None. [output file]
        cpu_number (int): Number of CPU for multiprocessing (1 by default)

    Returns:
        [str]: [output file]
    """
    start_time = time.time()

    lp_instance = set()

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
        lp_instance = lp_instance.union(draftnet)
    else:
        logger.warning('No host provided')

    if seeds_file:
        logger.info('Reading seeds from ' + seeds_file)
        try:
            seeds = sbml.readSBMLspecies_clyngor(seeds_file, 'seed')
        except FileNotFoundError:
            logger.critical('Seeds file not found')
            sys.exit(1)
        except ParseError:
            logger.critical("Invalid syntax in SBML file: "+seeds_file)
            sys.exit(1)
        lp_instance = lp_instance.union(set(seeds))

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
        lp_instance = lp_instance.union(set(targets))

    if not os.path.isdir(bacteria_dir):
        logger.critical("Symbiont directory not found")
        sys.exit(1)

    lp_instance = TermSet(lp_instance)
    if output:
        #clear the file
        open(output, 'w').close()
        #add the content of seeds and/or targets
        output = utils.to_file(lp_instance, output)
    else:
        output = utils.to_file(lp_instance)

    logger.info('Reading bacterial networks from ' + bacteria_dir + '...')

    onlyfiles = [(f, bacteria_dir) for f in listdir(bacteria_dir) if isfile(join(bacteria_dir, f))]

    if len(onlyfiles) == 0:
        logger.critical('No bacterial networks in ' + bacteria_dir)
        sys.exit(1)

    # Extract data from SBML models using multiprocessing.
    miscoto_pool = Pool(cpu_number)
    bact_models = miscoto_pool.starmap(extract_symbiont_data, onlyfiles)

    miscoto_pool.close()
    miscoto_pool.join()

    for one_bact_model in bact_models:
        utils.to_file(one_bact_model, output)

    logger.info("Instance created: " + os.path.abspath(output))

    logger.info("--- %s seconds ---" % (time.time() - start_time))
    utils.clean_up()

    return output
