#!/usr/bin/python
#-*- coding: utf-8 -*-

import json
import os
import subprocess

from miscoto import run_instance, run_mincom, run_scopes


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
    expected_exchanges = {('orgB3', 'host_metab_mod'): ['e']}

    results = run_mincom(host_file='../toy/orgA.xml', bacteria_dir='../toy/symbionts/', seeds_file='../toy/seeds.xml', targets_file='../toy/targets_A.xml', option='minexch', optsol=True)

    assert set(results['newly_prod']) == expected_newly_productible
    assert set(results['bacteria']) == expected_bacteria
    assert results['exchanged'] == expected_exchanges


def test_mincom_minexch_optsol_nohost():
    expected_newly_productible = set(['f'])
    expected_bacteria = set(['orgB3','orgA'])
    expected_exchanges = {('orgB3', 'orgA'): ['e']}

    results = run_mincom(bacteria_dir='../toy/symbionts_nohost/', seeds_file='../toy/seeds.xml', targets_file='../toy/targets_A.xml', option='minexch', optsol=True)

    assert set(results['newly_prod']) == expected_newly_productible
    assert set(results['bacteria']) == expected_bacteria
    assert results['exchanged'] == expected_exchanges


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

def test_mincom_soup_optsol_no_host():
    expected_newly_productible = set(['f'])
    expected_bacteria = set(['orgB1','orgB2','orgB3','orgA']) #solution is one org among the 3

    results = run_mincom(bacteria_dir='../toy/symbionts_nohost/', seeds_file='../toy/seeds.xml', targets_file='../toy/targets_A.xml', option='soup', optsol=True)

    assert set(results['newly_prod']) == expected_newly_productible
    assert set(results['bacteria']).issubset(expected_bacteria) and len(set(results['bacteria'])) ==2

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

def test_create_json_scopes():
    results = run_scopes(host_file='../toy/orgA.xml', bacteria_dir='../toy/symbionts/', seeds_file='../toy/seeds.xml', targets_file='../toy/targets_A.xml', output_json='test.json')
    dict_results = json.loads(open('test.json', 'r').read())
    expected_results = {'host_prodtargets': [],
                        'host_unprodtargets': ['f'],
                        'host_scope': ['d', 'a', 'c', 'b'],
                        'com_prodtargets': ['f'],
                        'com_unprodtargets': [],
                        'comhost_scope': ['f', 'e']}

    for result_key in expected_results:
        assert sorted(dict_results[result_key]) == sorted(expected_results[result_key])
    os.remove('test.json')

def test_create_json_mincom_minexch():
    results = run_mincom(host_file='../toy/orgA.xml', bacteria_dir='../toy/symbionts/',
                        seeds_file='../toy/seeds.xml', targets_file='../toy/targets_A.xml',
                        option='minexch', intersection=True, enumeration=True, union=True, 
                        optsol=True, output_json='test.json')
    dict_results = json.loads(open('test.json', 'r').read())
    expected_results = {"bacteria": ["orgB3"],
                        "still_unprod": [],
                        "newly_prod": ["f"],
                        "union_bacteria": ["orgB3"],
                        "score_optimum_union": "0,1,1",
                        "inter_bacteria": ["orgB3"],
                        "score_optimum_inter": "0,1,1",
                        "enum_bacteria": {"1": ["orgB3"]},
                        "enum_exchanged": {"1": [{"what": ["e"],"from_to": ["orgB3","host_metab_mod"]}]},
                        "union_exchanged": [{"what": ["e"],"from_to": ["orgB3","host_metab_mod"]}],
                        "inter_exchanged": [{"what": ["e"],"from_to": ["orgB3","host_metab_mod"]}],
                        "exchanged": [{"what": ["e"],"from_to": ["orgB3","host_metab_mod"]}]
                    }
    assert dict_results['bacteria'] == expected_results['bacteria']
    assert dict_results['still_unprod'] == expected_results['still_unprod']
    assert dict_results['newly_prod'] == expected_results['newly_prod']
    assert dict_results['union_bacteria'] == expected_results['union_bacteria']
    assert dict_results['score_optimum_union'] == expected_results['score_optimum_union']
    assert dict_results['inter_bacteria'] == expected_results['inter_bacteria']
    assert dict_results['score_optimum_inter'] == expected_results['score_optimum_inter']
    assert dict_results['enum_bacteria'] == expected_results['enum_bacteria']
    assert dict_results['enum_exchanged'] == expected_results['enum_exchanged']
    assert dict_results['union_exchanged'] == expected_results['union_exchanged']
    assert dict_results['inter_exchanged'] == expected_results['inter_exchanged']
    assert dict_results['exchanged'] == expected_results['exchanged']
    os.remove('test.json')

def test_create_json_mincom_soup():
    run_mincom(host_file='../toy/orgA.xml', bacteria_dir='../toy/symbionts/',
                        seeds_file='../toy/seeds.xml', targets_file='../toy/targets_A.xml',
                        option='soup', enumeration=True, optsol=True, output_json='test.json')
    dict_results = json.loads(open('test.json', 'r').read())
    expected_results = {'exchanged': [],
                        'bacteria': ['orgB3'],
                        'still_unprod': [],
                        'newly_prod': ['f'],
                        'enum_exchanged': {'1': {}, '2': {}, '3': {}},
                        'enum_bacteria': {'1': ['orgB3'], '2': ['orgB1'], '3': ['orgB2']}}
    bacts = {'orgB1', 'orgB2', 'orgB3'}

    assert dict_results['one_model']['newly_producible_target'] == ['f']
    assert set(dict_results['one_model']['chosen_bacteria']).issubset(bacts)
    assert dict_results['exchanged'] == expected_results['exchanged']
    assert set(dict_results['bacteria']).issubset(bacts)
    assert dict_results['still_unprod'] == expected_results['still_unprod']
    assert dict_results['newly_prod'] == expected_results['newly_prod']
    assert bacts == set([y for x in list(dict_results['enum_bacteria'].values()) for y in x])
    assert len(dict_results['enum_exchanged']) == len(expected_results['enum_exchanged'])
    os.remove('test.json')