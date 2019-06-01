#!/usr/bin/python
#-*- coding: utf-8 -*-

import subprocess

from miscoto import run_instance, run_mincom, run_scopes
from pyasp.asp import *


def test_instance():
    with open('../toy/instance_toy.lp', 'r') as expected_file:
        expected_lp_instances = expected_file.read().splitlines()
    lp_instance = run_instance(host_file='../toy/orgA.xml', bacteria_dir='../toy/symbionts/', seeds_file='../toy/seeds.xml', targets_file='../toy/targets_A.xml')

    with open(lp_instance, 'r') as found_file:
        lp_instances = found_file.read().splitlines()
        assert sorted(lp_instances) == sorted(expected_lp_instances)


def test_mincom_minexch():
    expected_newly_productible = set(['f'])
    expected_bacteria = set(['orgB3'])
    expected_exchande = {('orgB3', 'host_metab_mod'): ['e']}

    results = run_mincom(host_file='../toy/orgA.xml', bacteria_dir='../toy/symbionts/', seeds_file='../toy/seeds.xml', targets_file='../toy/targets_A.xml', option='minexch')

    assert set(results['newly_prod']) == expected_newly_productible
    assert set(results['bacteria']) == expected_bacteria
    assert results['exchanged'] == expected_exchande


def test_mincom_minexch_optsol():
    expected_newly_productible = set(['f'])
    expected_bacteria = set(['orgB3'])
    expected_exchande = {('orgB3', 'host_metab_mod'): ['e']}

    results = run_mincom(host_file='../toy/orgA.xml', bacteria_dir='../toy/symbionts/', seeds_file='../toy/seeds.xml', targets_file='../toy/targets_A.xml', option='minexch', optsol=True)

    assert set(results['newly_prod']) == expected_newly_productible
    assert set(results['bacteria']) == expected_bacteria
    assert results['exchanged'] == expected_exchande


def test_mincom_minexch_intersection():
    inter_bacteria = set(['orgB3'])
    inter_exchanged = {('orgB3', 'host_metab_mod'): ['e']}

    results = run_mincom(host_file='../toy/orgA.xml', bacteria_dir='../toy/symbionts/', seeds_file='../toy/seeds.xml', targets_file='../toy/targets_A.xml', option='minexch', intersection=True)

    assert set(results['inter_bacteria']) == inter_bacteria
    assert results['inter_exchanged'] == inter_exchanged


def test_mincom_minexch_enumeration():
    enum_bacteria = {1: ['orgB3']}
    enum_exchanged = {1:{('orgB3', 'host_metab_mod'): ['e']}}

    results = run_mincom(host_file='../toy/orgA.xml', bacteria_dir='../toy/symbionts/', seeds_file='../toy/seeds.xml', targets_file='../toy/targets_A.xml', option='minexch', enumeration=True)

    assert results['enum_bacteria'] == enum_bacteria
    assert results['enum_exchanged'] == enum_exchanged


def test_mincom_minexch_enumeration_optsol():
    enum_bacteria = {1: ['orgB3']}
    enum_exchanged = {1:{('orgB3', 'host_metab_mod'): ['e']}}

    results = run_mincom(host_file='../toy/orgA.xml', bacteria_dir='../toy/symbionts/', seeds_file='../toy/seeds.xml', targets_file='../toy/targets_A.xml', option='minexch', enumeration=True, optsol=True)

    assert results['enum_bacteria'] == enum_bacteria
    assert results['enum_exchanged'] == enum_exchanged


def test_mincom_soup():
    expected_newly_productible = set(['f'])
    expected_bacteria = set(['orgB1','orgB2','orgB3']) #solution is one org among the 3

    results = run_mincom(host_file='../toy/orgA.xml', bacteria_dir='../toy/symbionts/', seeds_file='../toy/seeds.xml', targets_file='../toy/targets_A.xml', option='soup')

    assert set(results['newly_prod']) == expected_newly_productible
    assert set(results['bacteria']).issubset(expected_bacteria) and len(set(results['bacteria'])) ==1

def test_mincom_soup_optsol():
    expected_newly_productible = set(['f'])
    expected_bacteria = set(['orgB1','orgB2','orgB3']) #solution is one org among the 3

    results = run_mincom(host_file='../toy/orgA.xml', bacteria_dir='../toy/symbionts/', seeds_file='../toy/seeds.xml', targets_file='../toy/targets_A.xml', option='soup', optsol=True)

    assert set(results['newly_prod']) == expected_newly_productible
    assert set(results['bacteria']).issubset(expected_bacteria) and len(set(results['bacteria'])) ==1


def test_mincom_soup_enumeration():
    enum_bacteria = {1: ['orgB3'], 2: ['orgB1'], 3: ['orgB2']}

    results = run_mincom(host_file='../toy/orgA.xml', bacteria_dir='../toy/symbionts/', seeds_file='../toy/seeds.xml', targets_file='../toy/targets_A.xml', option='soup', enumeration=True)

    assert sorted(enum_bacteria.values()) == sorted(results['enum_bacteria'].values())
    assert sorted(enum_bacteria.keys()) == sorted(results['enum_bacteria'].keys())


def test_mincom_soup_enumeration_optsol():
    enum_bacteria = {1: ['orgB3'], 2: ['orgB1'], 3: ['orgB2']}

    results = run_mincom(host_file='../toy/orgA.xml', bacteria_dir='../toy/symbionts/', seeds_file='../toy/seeds.xml', targets_file='../toy/targets_A.xml', option='soup', enumeration=True, optsol=True)

    assert sorted(enum_bacteria.values()) == sorted(results['enum_bacteria'].values())
    assert sorted(enum_bacteria.keys()) == sorted(results['enum_bacteria'].keys())


def test_scopes():
    producible_targets = set()
    unproducible_targets = set(['f'])
    host_scope = set(['d', 'a', 'c', 'b'])
    microbiome_producible_targets = set(['f'])
    microbiome_unproducible_targets = set()
    microbiome_only = set(['f', 'e'])

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
