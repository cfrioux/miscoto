#!/usr/bin/python
#-*- coding: utf-8 -*-

import json
import os
import subprocess

from miscoto import run_instance, run_mincom, run_scopes, run_focus


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
    expected_exchange = {('orgB3', 'host_metab_mod'): ['e']}
    expected_producer = {"f": ["host_metab_mod"]}

    results = run_mincom(host_file='../toy/orgA.xml', bacteria_dir='../toy/symbionts/', seeds_file='../toy/seeds.xml', targets_file='../toy/targets_A.xml', option='minexch')

    assert set(results['newly_prod']) == expected_newly_productible
    assert set(results['bacteria']) == expected_bacteria
    assert results['exchanged'] == expected_exchange
    assert expected_producer == results['one_model_targetsproducers']


def test_mincom_minexch_optsol():
    expected_newly_productible = set(['f'])
    expected_bacteria = set(['orgB3'])
    expected_exchanges = {('orgB3', 'host_metab_mod'): ['e']}
    expected_producer = {"f": ["host_metab_mod"]}

    results = run_mincom(host_file='../toy/orgA.xml', bacteria_dir='../toy/symbionts/', seeds_file='../toy/seeds.xml', targets_file='../toy/targets_A.xml', option='minexch', optsol=True)

    assert set(results['newly_prod']) == expected_newly_productible
    assert set(results['bacteria']) == expected_bacteria
    assert results['exchanged'] == expected_exchanges


def test_mincom_minexch_optsol_nohost():
    expected_newly_productible = set(['f'])
    expected_bacteria = set(['orgB3','orgA'])
    expected_exchanges = {('orgB3', 'orgA'): ['e']}
    expected_producer = {"f": ["orgA"]}

    results = run_mincom(bacteria_dir='../toy/symbionts_nohost/', seeds_file='../toy/seeds.xml', targets_file='../toy/targets_A.xml', option='minexch', optsol=True)

    assert set(results['newly_prod']) == expected_newly_productible
    assert set(results['bacteria']) == expected_bacteria
    assert results['exchanged'] == expected_exchanges
    assert expected_producer == results['one_model_targetsproducers']


def test_mincom_minexch_intersection():
    inter_bacteria = set(['orgB3'])
    inter_exchanged = {('orgB3', 'host_metab_mod'): ['e']}
    inter_producer = {"f": ["host_metab_mod"]}

    results = run_mincom(host_file='../toy/orgA.xml', bacteria_dir='../toy/symbionts/', seeds_file='../toy/seeds.xml', targets_file='../toy/targets_A.xml', option='minexch', intersection=True)

    assert set(results['inter_bacteria']) == inter_bacteria
    assert results['inter_exchanged'] == inter_exchanged
    assert inter_producer == results['inter_targetsproducers']


def test_mincom_minexch_enumeration():
    enum_bacteria = {1: ['orgB3']}
    enum_exchanged = {1:{('orgB3', 'host_metab_mod'): ['e']}}
    enum_producer = {1:{"f": ["host_metab_mod"]}}

    results = run_mincom(host_file='../toy/orgA.xml', bacteria_dir='../toy/symbionts/', seeds_file='../toy/seeds.xml', targets_file='../toy/targets_A.xml', option='minexch', enumeration=True)

    assert results['enum_bacteria'] == enum_bacteria
    assert results['enum_exchanged'] == enum_exchanged
    assert results['enum_targetsproducers'] == enum_producer


def test_mincom_minexch_enumeration_optsol():
    enum_bacteria = {1: ['orgB3']}
    enum_exchanged = {1:{('orgB3', 'host_metab_mod'): ['e']}}
    enum_producer = {1:{"f": ["host_metab_mod"]}}
    expected_producer = {"f": ["host_metab_mod"]}

    results = run_mincom(host_file='../toy/orgA.xml', bacteria_dir='../toy/symbionts/', seeds_file='../toy/seeds.xml', targets_file='../toy/targets_A.xml', option='minexch', enumeration=True, optsol=True)

    assert results['enum_bacteria'] == enum_bacteria
    assert results['enum_exchanged'] == enum_exchanged
    assert expected_producer == results['one_model_targetsproducers']
    assert results['enum_targetsproducers'] == enum_producer


def test_mincom_soup():
    expected_newly_productible = set(['f'])
    expected_producible = set(['f', 'c'])
    expected_bacteria = set(['orgB1','orgB2','orgB3']) #solution is one org among the 3
    expected_producer_b3 = {"f": ["host_metab_mod"], "c": ["host_metab_mod", "orgB3"]}
    expected_producer_b2 = {"f": ["host_metab_mod"], "c": ["host_metab_mod", "orgB2"]}
    expected_producer_b1 = {"f": ["host_metab_mod"], "c": ["host_metab_mod"]}

    results = run_mincom(host_file='../toy/orgA.xml', bacteria_dir='../toy/symbionts/', seeds_file='../toy/seeds.xml', targets_file='../toy/targets.xml', option='soup')

    assert set(results['newly_prod']) == expected_newly_productible
    assert set(results['producible']) == expected_producible
    assert set(results['bacteria']).issubset(expected_bacteria) and len(set(results['bacteria'])) ==1
    for target in expected_producible:
        assert set(expected_producer_b1[target]) == set(results['one_model_targetsproducers'][target]) or set(expected_producer_b2[target]) == set(results['one_model_targetsproducers'][target]) or set(expected_producer_b3[target]) == set(results['one_model_targetsproducers'][target])


def test_mincom_soup_optsol():
    expected_newly_productible = set(['f'])
    expected_bacteria = set(['orgB1','orgB2','orgB3']) #solution is one org among the 3
    expected_producer = {"f": ["host_metab_mod"]}

    results = run_mincom(host_file='../toy/orgA.xml', bacteria_dir='../toy/symbionts/', seeds_file='../toy/seeds.xml', targets_file='../toy/targets_A.xml', option='soup', optsol=True)

    assert set(results['newly_prod']) == expected_newly_productible
    assert set(results['bacteria']).issubset(expected_bacteria) and len(set(results['bacteria'])) ==1
    assert expected_producer == results['one_model_targetsproducers']


def test_mincom_soup_optsol_no_host():
    expected_newly_productible = set(['f'])
    expected_bacteria = set(['orgB1','orgB2','orgB3','orgA']) #solution is one org among the 3
    expected_producer = {"f": ["orgA"]}

    results = run_mincom(bacteria_dir='../toy/symbionts_nohost/', seeds_file='../toy/seeds.xml', targets_file='../toy/targets_A.xml', option='soup', optsol=True)

    assert set(results['newly_prod']) == expected_newly_productible
    assert set(results['bacteria']).issubset(expected_bacteria) and len(set(results['bacteria'])) ==2
    assert expected_producer == results['one_model_targetsproducers']


def test_mincom_soup_enumeration():
    enum_bacteria = {1: ['orgB3'], 2: ['orgB1'], 3: ['orgB2']}
    enum_producer = {1:{"f": ["host_metab_mod"]}, 2:{"f": ["host_metab_mod"]}, 3:{"f": ["host_metab_mod"]}}

    results = run_mincom(host_file='../toy/orgA.xml', bacteria_dir='../toy/symbionts/', seeds_file='../toy/seeds.xml', targets_file='../toy/targets_A.xml', option='soup', enumeration=True)

    assert sorted(enum_bacteria.values()) == sorted(results['enum_bacteria'].values())
    assert sorted(enum_bacteria.keys()) == sorted(results['enum_bacteria'].keys())
    assert results['enum_targetsproducers'] == enum_producer


def test_mincom_soup_enumeration_optsol():
    enum_bacteria = {1: ['orgB3'], 2: ['orgB1'], 3: ['orgB2']}
    enum_producer = {1:{"f": ["host_metab_mod"]}, 2:{"f": ["host_metab_mod"]}, 3:{"f": ["host_metab_mod"]}}
    expected_producer = {"f": ["host_metab_mod"]}

    results = run_mincom(host_file='../toy/orgA.xml', bacteria_dir='../toy/symbionts/', seeds_file='../toy/seeds.xml', targets_file='../toy/targets_A.xml', option='soup', enumeration=True, optsol=True)

    assert sorted(enum_bacteria.values()) == sorted(results['enum_bacteria'].values())
    assert sorted(enum_bacteria.keys()) == sorted(results['enum_bacteria'].keys())
    assert expected_producer == results['one_model_targetsproducers']
    assert results['enum_targetsproducers'] == enum_producer


def test_mincom_key_stones():
    results = run_mincom(host_file='../toy/orgA.xml', bacteria_dir='../toy/symbionts/', seeds_file='../toy/seeds.xml',
                        targets_file='../toy/targets.xml', union=True, intersection=True,
                        option='soup', output_json='test.json')
    dict_results = json.loads(open('test.json', 'r').read())
    expected_results = {'alternative_symbionts':['orgB3', 'orgB2', 'orgB1'],
                        'essential_symbionts':[],
                        'key_species':['orgB2', 'orgB1', 'orgB3']}

    for result_key in expected_results:
        assert sorted(dict_results[result_key]) == sorted(expected_results[result_key])
    os.remove('test.json')


def test_scopes():
    producible_targets = set()
    unproducible_targets = set(['f'])
    host_scope = set(['d', 'a', 'c', 'b'])
    microbiome_producible_targets = set(['f'])
    microbiome_unproducible_targets = set()
    microbiome_only = set(['f', 'e'])
    expected_producer = {"f": ["host_metab_mod"]}

    results = run_scopes(host_file='../toy/orgA.xml', bacteria_dir='../toy/symbionts/', seeds_file='../toy/seeds.xml', targets_file='../toy/targets_A.xml')

    assert set(results['host_prodtargets']) == producible_targets
    assert set(results['host_unprodtargets']) == unproducible_targets
    assert set(results['host_scope']) == host_scope
    assert set(results['com_prodtargets']) == microbiome_producible_targets
    assert set(results['com_unprodtargets']) == microbiome_unproducible_targets
    assert set(results['comhost_scope']) == microbiome_only
    assert results['targets_producers'] == expected_producer


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


def test_scopes_json_cli():
    subprocess.call(['miscoto', 'scopes', '-b', '../toy/symbionts/', '-m', '../toy/orgA.xml',
                    '-s', '../toy/seeds.xml', '-t', '../toy/targets_A.xml', '--output', 'test.json'])
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


def test_scopes_json_instance_cli():
    subprocess.call(['miscoto', 'instance', '-b', '../toy/symbionts/', '-m', '../toy/orgA.xml',
                    '-s', '../toy/seeds.xml', '-t', '../toy/targets_A.xml', '--output', 'test.lp'])
    subprocess.call(['miscoto', 'scopes', '-a', 'test.lp', '--output', 'test.json'])
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
    os.remove('test.lp')

def test_scopes_json_instance_no_host_cli():
    subprocess.call(['miscoto', 'instance', '-b', '../toy/symbionts/',
                    '-s', '../toy/seeds.xml', '-t', '../toy/targets.xml', '--output', 'instance_nohost_test.lp'])
    subprocess.call(['miscoto', 'mincom', '-a', 'instance_nohost_test.lp', '--output', 'instance_nohost_test.json', '--optsol', '--intersection', '--union', '--enumeration', '--option', 'minexch'])
    dict_results = json.loads(open('instance_nohost_test.json', 'r').read())
    expected_results = {"exchanged": [],
                        "inter_bacteria": [],
                        "inter_exchanged": [],
                        "inter_targetsproducers": {},
                        "key_species": ["orgB3", "orgB2"],
                        "inter_bacteria": [],
                        "inter_exchanged": [],
                        "inter_targetsproducers": {},
                        "newly_prod": ["c"],
                        "producible": [],
                        "score_optimum_inter": "1,1,0",
                        "score_optimum_union": "1,1,0",
                        "still_unprod": ["f"],
                        "union_bacteria": ["orgB3","orgB2"],
                        "union_exchanged": [],
                        'alternative_symbionts': ['orgB3', 'orgB2']}

    for result_key in expected_results:
        assert sorted(dict_results[result_key]) == sorted(expected_results[result_key])
    os.remove('instance_nohost_test.json')
    os.remove('instance_nohost_test.lp')

def test_focus_json():
    subprocess.call(['miscoto', 'focus', '-b', '../toy/symbionts_nohost/', '-s', '../toy/seeds.xml',
                    '-f', 'orgA', '--output', 'focus_res_test.json'])
    dict_results = json.loads(open('focus_res_test.json', 'r').read())
    expected_results = {"orgA": {"produced_alone": ["c", "d"],
                        "produced_in_community": ["c", "d", "f"],
                        "community_metabolic_gain": ["f"],
                        }}
    for result_key in expected_results:
        assert sorted(dict_results[result_key]) == sorted(expected_results[result_key])
    os.remove('focus_res_test.json')

def test_focus_cli():
    dict_results = run_focus(bacteria_dir='../toy/symbionts_nohost/', seeds_file='../toy/seeds.xml', focus_bact=['orgA'])

    expected_results = {"orgA": {"produced_alone": ["c", "d"],
                        "produced_in_community": ["c", "d", "f"],
                        "community_metabolic_gain": ["f"],
                        }}
    for result_key in expected_results:
        assert sorted(dict_results[result_key]) == sorted(expected_results[result_key])

def test_focus_list():
    dict_results = run_focus(bacteria_dir='../toy/symbionts_nohost/', seeds_file='../toy/seeds.xml', focus_bact=['orgA', 'orgB1', 'orgB2'])

    expected_results = {"orgA": {
                            "community_metabolic_gain": ["f"],
                            "produced_alone": ["c","d"],
                            "produced_in_community": ["c","d","f"]},
                        "orgB1": {
                            "community_metabolic_gain": ["e"],
                            "produced_alone": [],
                            "produced_in_community": ["e"]}, 
                        "orgB2": {
                            "community_metabolic_gain": ["e"],
                            "produced_alone": ["c"],
                            "produced_in_community": ["e","c"]}}
    for org in expected_results:
        for result_key in expected_results[org]:
            assert sorted(dict_results[org][result_key]) == sorted(expected_results[org][result_key])

def test_focus_all():
    dict_results = run_focus(bacteria_dir='../toy/symbionts_nohost/', seeds_file='../toy/seeds.xml', focus_bact=[], all_networks=True)

    expected_results = {"orgA": {
                            "community_metabolic_gain": ["f"],
                            "produced_alone": ["c","d"],
                            "produced_in_community": ["c","d","f"]},
                        "orgB1": {
                            "community_metabolic_gain": ["e"],
                            "produced_alone": [],
                            "produced_in_community": ["e"]}, 
                        "orgB2": {
                            "community_metabolic_gain": ["e"],
                            "produced_alone": ["c"],
                            "produced_in_community": ["e","c"]},
                        "orgB3": {
                            "community_metabolic_gain": [],
                            "produced_alone": ["e", "d", "c"],
                            "produced_in_community": ["e", "d", "c"]}}
    for org in expected_results:
        for result_key in expected_results[org]:
            assert sorted(dict_results[org][result_key]) == sorted(expected_results[org][result_key])

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
    for result_key in expected_results:
        assert sorted(dict_results[result_key]) == sorted(expected_results[result_key])
    os.remove('test.json')


def test_create_json_mincom_minexch_instance():
    run_instance(host_file='../toy/orgA.xml', bacteria_dir='../toy/symbionts/',
                        seeds_file='../toy/seeds.xml', targets_file='../toy/targets_A.xml',
                        output='test.lp')

    results = run_mincom(lp_instance_file='test.lp', option='minexch', intersection=True,
                        enumeration=True, union=True, optsol=True, output_json='test.json')
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
    for result_key in expected_results:
        assert sorted(dict_results[result_key]) == sorted(expected_results[result_key])
    os.remove('test.json')
    os.remove('test.lp')


def test_create_json_mincom_minexch_cli():
    subprocess.call(['miscoto', 'mincom', '-b', '../toy/symbionts/', '-m', '../toy/orgA.xml',
                        '-s', '../toy/seeds.xml', '-t', '../toy/targets_A.xml', '-o', 'minexch',
                        '--intersection', '--union', '--enumeration', '--optsol', '--output', 'test.json'])
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
    for result_key in expected_results:
        assert sorted(dict_results[result_key]) == sorted(expected_results[result_key])
    os.remove('test.json')


def test_create_json_mincom_minexch_instance_cli():
    subprocess.call(['miscoto', 'instance', '-b', '../toy/symbionts/', '-m', '../toy/orgA.xml',
                    '-s', '../toy/seeds.xml', '-t', '../toy/targets_A.xml', '--output', 'test.lp'])

    subprocess.call(['miscoto', 'mincom', '-a', 'test.lp', '-o', 'minexch',
                        '--intersection', '--union', '--enumeration', '--optsol', '--output', 'test.json'])

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
    for result_key in expected_results:
        assert sorted(dict_results[result_key]) == sorted(expected_results[result_key])
    os.remove('test.json')
    os.remove('test.lp')


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


def test_create_json_mincom_soup_cli():
    subprocess.call(['miscoto', 'mincom', '-b', '../toy/symbionts/', '-m', '../toy/orgA.xml',
                        '-s', '../toy/seeds.xml', '-t', '../toy/targets_A.xml', '-o', 'soup',
                        '--enumeration', '--optsol', '--output', 'test.json'])
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


def test_create_json_mincom_soup_instance_cli():
    subprocess.call(['miscoto', 'instance', '-b', '../toy/symbionts/', '-m', '../toy/orgA.xml',
                    '-s', '../toy/seeds.xml', '-t', '../toy/targets_A.xml', '--output', 'test.lp'])

    subprocess.call(['miscoto', 'mincom', '-a', 'test.lp', '-o', 'soup',
                        '--enumeration', '--optsol', '--output', 'test.json'])
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
    os.remove('test.lp')


if __name__ == "__main__":
    print("** testing scope **")
    test_scopes()
    print("** testing mincom **")
    test_mincom_soup_enumeration_optsol()
    test_mincom_soup_enumeration()
    test_mincom_soup_optsol_no_host()
    test_mincom_soup_optsol()
    test_mincom_soup()
    test_mincom_minexch_enumeration_optsol()
    print("** testing instance creation")
    test_instance()
