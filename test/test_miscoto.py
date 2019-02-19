#!/usr/bin/python
#-*- coding: utf-8 -*-

import subprocess

from miscoto import run_instance, run_mincom, run_scopes
from pyasp.asp import *


def test_instance():
    expected_lp_instance = set([Term('product',['"e"','"R_R4"','"orgB2"']), Term('product',['"c"','"R_R1"','"host_metab_mod"']), Term('species',['"d"','"d"','"c"','"orgB3"']), Term('species',['"b"','"b"','"c"','"orgB1"']), Term('target',['"f"']), Term('reaction',['"R_R4"','"orgB2"']), Term('product',['"e"','"R_R4"','"orgB3"']), Term('species',['"e"','"e"','"c"','"orgB3"']), Term('species',['"a"','"a"','"c"','"host_metab_mod"']), Term('reactant',['"a"','"R_R1"','"orgB2"']), Term('species',['"e"','"e"','"c"','"orgB2"']), Term('reaction',['"R_R4"','"orgB1"']), Term('reaction',['"R_R1"','"orgB2"']), Term('product',['"c"','"R_R1"','"orgB2"']), Term('reactant',['"d"','"R_R4"','"orgB2"']), Term('species',['"c"','"c"','"c"','"orgB3"']), Term('product',['"f"','"R_R3"','"host_metab_mod"']), Term('reaction',['"R_R3"','"host_metab_mod"']), Term('product',['"c"','"R_R1"','"orgB3"']), Term('reaction',['"R_R2"','"orgB3"']), Term('species',['"d"','"d"','"c"','"orgB1"']), Term('reactant',['"b"','"R_R2"','"orgB3"']), Term('reaction',['"R_R1"','"host_metab_mod"']), Term('reactant',['"b"','"R_R2"','"host_metab_mod"']), Term('species',['"a"','"a"','"c"','"orgB2"']), Term('reactant',['"c"','"R_R4"','"orgB1"']), Term('species',['"e"','"e"','"c"','"host_metab_mod"']), Term('seed',['"b"']), Term('reaction',['"R_R4"','"orgB3"']), Term('species',['"c"','"c"','"c"','"orgB1"']), Term('reactant',['"a"','"R_R1"','"orgB3"']), Term('reactant',['"d"','"R_R4"','"orgB3"']), Term('product',['"d"','"R_R2"','"host_metab_mod"']), Term('species',['"c"','"c"','"c"','"host_metab_mod"']), Term('bacteria',['"orgB3"']), Term('reactant',['"c"','"R_R4"','"orgB2"']), Term('species',['"a"','"a"','"c"','"orgB3"']), Term('species',['"b"','"b"','"c"','"host_metab_mod"']), Term('reactant',['"d"','"R_R4"','"orgB1"']), Term('reactant',['"a"','"R_R1"','"host_metab_mod"']), Term('species',['"d"','"d"','"c"','"host_metab_mod"']), Term('species',['"f"','"f"','"c"','"host_metab_mod"']), Term('reactant',['"e"','"R_R3"','"host_metab_mod"']), Term('product',['"e"','"R_R4"','"orgB1"']), Term('species',['"b"','"b"','"c"','"orgB2"']), Term('product',['"d"','"R_R2"','"orgB3"']), Term('species',['"c"','"c"','"c"','"orgB2"']), Term('species',['"e"','"e"','"c"','"orgB1"']), Term('reaction',['"R_R1"','"orgB3"']), Term('species',['"a"','"a"','"c"','"orgB1"']), Term('reaction',['"R_R2"','"host_metab_mod"']), Term('bacteria',['"orgB1"']), Term('species',['"b"','"b"','"c"','"orgB3"']), Term('draft',['"host_metab_mod"']), Term('species',['"d"','"d"','"c"','"orgB2"']), Term('reactant',['"c"','"R_R4"','"orgB3"']), Term('seed',['"a"']), Term('bacteria',['"orgB2"'])])

    lp_instance = run_instance(host_file='../toy/orgA.xml', bacteria_dir='../toy/symbionts/', seeds_file='../toy/seeds.xml', targets_file='../toy/targets_A.xml')
    lp_instance = [atom for atom in lp_instance]

    assert set(lp_instance) == expected_lp_instance


def test_mincom():
    expected_newly_productible = set(['"f"'])
    expected_bacteria = set(['"orgB3"'])
    expected_exchande = {('"orgB3"', '"host_metab_mod"'): ['"e"']}

    results = run_mincom(host_file='../toy/orgA.xml', bacteria_dir='../toy/symbionts/', seeds_file='../toy/seeds.xml', targets_file='../toy/targets_A.xml', option='minexch')

    assert set(results['newly_prod']) == expected_newly_productible
    assert set(results['bacteria']) == expected_bacteria
    assert results['exchanged'] == expected_exchande


def test_scopes():
    producible_targets = set()
    unproducible_targets = set(['"f"'])
    host_scope = set(['"d"', '"a"', '"c"', '"b"'])
    microbiome_producible_targets = set(['"f"'])
    microbiome_unproducible_targets = set()
    microbiome_only = set(['"f"', '"e"'])

    results = run_scopes(host_file='../toy/orgA.xml', bacteria_dir='../toy/symbionts/', seeds_file='../toy/seeds.xml', targets_file='../toy/targets_A.xml')

    assert set(results['host_prodtargets']) == producible_targets
    assert set(results['host_unprodtargets']) == unproducible_targets
    assert set(results['host_scope']) == host_scope
    assert set(results['com_prodtargets']) == microbiome_producible_targets
    assert set(results['com_unprodtargets']) == microbiome_unproducible_targets
    assert set(results['comhost_scope']) == microbiome_only

if __name__ == "__main__":
    print("** testing scope **")
    test_scopes()
    print("** testing mincom **")
    test_mincom()
    print("** testing instance creation")
    test_instance()
