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


def run_scopes(lp_instance_file=None, targets_file=None, seeds_file=None, bacteria_dir=None, host_file=None, output_json=None):
    """Computes community scopes
        lp_instance_file ([str], optional): Defaults to None. [ASP facts instance of the problem]
        targets_file ([str], optional): Defaults to None. [targets file]
        seeds_file ([str], optional): Defaults to None. [seeds file]
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

        if targets_file:
            logger.info('Reading targets from ' + targets_file)
            try:
                targetsfacts = sbml.readSBMLspecies_clyngor(targets_file, 'target')
            except FileNotFoundError:
                logger.critical('Targets file not found')
                sys.exit(1)
            except ParseError:
                logger.critical("Invalid syntax in SBML file: "+targets_file)
                sys.exit(1)
        else:
            targetsfacts = TermSet()

        if seeds_file:
            logger.info('Reading seeds from ' + seeds_file)
            try:
                seedsfacts = sbml.readSBMLspecies_clyngor(seeds_file, 'seed')
            except FileNotFoundError:
                logger.critical('Seeds file not found')
                sys.exit(1)
            except ParseError:
                logger.critical("Invalid syntax in SBML file: " + seeds_file)
                sys.exit(1)
        else:
            seedsfacts = TermSet()

        with open(lp_instance_file, "a") as f:
            for elem in targetsfacts:
                f.write(str(elem) + '.\n')
            for elem in seedsfacts:
                f.write(str(elem) + '.\n')

    # case 2: read inputs from SBML files
    elif bacteria_dir and seeds_file:
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
                logger.critical("Invalid syntax in SBML file: " + targets_file)
                sys.exit(1)
            lp_instance = TermSet(lp_instance.union(targets))
        else:
            logger.info("No targets provided.")

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
        #logger.info(pusage)
        quit()

    logger.info("Computing scopes...")

    model = query.get_scopes(lp_instance_file, commons.ASP_SRC_SCOPES)

    host_scope = []
    host_prodtargets = []
    host_unprodtargets = []
    com_scope = []
    comhost_scope = []
    com_prodtargets = []
    com_unprodtargets = []
    target_producers = {}
    for pred in model:
        if pred == 'dscope':
            for a in model[pred, 1]:
                host_scope.append(a[0])
        elif pred == 'dproducible':
            for a in model[pred, 1]:
                host_prodtargets.append(a[0])
        elif pred == 'dunproducible':
            for a in model[pred, 1]:
                host_unprodtargets.append(a[0])
        elif pred == 'newscope_microbiome':
            for a in model[pred, 1]:
                com_scope.append(a[0])
        elif pred == 'newscope_with_host':
            for a in model[pred, 1]:
                comhost_scope.append(a[0])
        elif pred == 'newlyproducible':
            for a in model[pred, 1]:
                com_prodtargets.append(a[0])
        elif pred == 'aunproducible':
            for a in model[pred, 1]:
                com_unprodtargets.append(a[0])
        elif pred == 'target_producer_coop_initcom':
            for a in model[pred, 2]:
                if not a[1] in target_producers:
                    target_producers[a[1]] = [a[0]]
                else:
                    target_producers[a[1]].append(a[0])

    if host_file or input_instance:
        logger.info('*** HOST model producibility check ***')

        logger.info('Host producible targets => ' + str(len(host_prodtargets)))
        logger.info("\n".join(host_prodtargets))
        results['host_prodtargets'] = host_prodtargets

        logger.info('Host unproducible targets => ' +
                    str(len(host_unprodtargets)))
        logger.info("\n".join(host_unprodtargets))
        results['host_unprodtargets'] = host_unprodtargets

        logger.info('Host scope => ' + str(len(host_scope)))
        logger.info("\n".join(host_scope))
        results['host_scope'] = host_scope

    logger.info('*** MICROBIOME added-value ***')
    logger.info('Microbiome only producible targets => ' +
                str(len(com_prodtargets)))
    logger.info("\n".join(com_prodtargets))
    results['com_prodtargets'] = com_prodtargets

    logger.info('Microbiome unproducible targets => ' +
                str(len(com_unprodtargets)))
    logger.info("\n".join(com_unprodtargets))
    results['com_unprodtargets'] = com_unprodtargets

    if host_file or input_instance:
        logger.info(
            '\nHost metabolites becoming producible through cooperation with symbionts (excluding metabolites that were producible by the host alone) => '
            + str(len(comhost_scope)) + "\n")
        logger.info("\n".join(comhost_scope))
        results['comhost_scope'] = comhost_scope
    if input_instance or not host_file:
        logger.info(
            '\nMicrobiome (host and symbionts) metabolites that become producible through cooperation (excluding metabolites that were producible by the host alone) => '
            + str(len(com_scope)) + "\n")
        logger.info("\n".join(com_scope))
        results['com_scope'] = com_scope
    
    results["targets_producers"] = target_producers

    if delete_lp_instance == True:
        os.unlink(lp_instance_file)

    if output_json:
        utils.to_json(results, output_json)

    logger.info("--- %s seconds ---" % (time.time() - start_time))
    utils.clean_up()

    return results
