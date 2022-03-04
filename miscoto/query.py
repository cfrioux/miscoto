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

import os
import tempfile
import clyngor
from miscoto import utils

def get_scopes(instance_f, encoding):
    """Get metabolic scope of a microbiota
    
    Args:
        instance_f (str): ASP instance file
        encoding (str): ASP model encoding
    
    Returns:
        TermSet: ASP model
    """
    prg = [encoding, instance_f]
    options = ''
    best_model = None
    models = clyngor.solve(prg, options=options, use_clingo_module=False)
    for model in models.discard_quotes.by_arity:
        best_model = model

    return best_model



def get_grounded_communities_from_file(instance_f, encoding):
    """Ground the model, from a file
    
    Args:
        instance_f (str): model file
        encoding (str): ASP model encoding
    
    Returns:
        bytes: grounded model
    """
    prg = [encoding, instance_f]
    grounding = clyngor.grounded_program(prg)

    return grounding

def get_communities_from_g(grounding):
    """Get optimal community, from grounding
    
    Args:
        grounding (bytes): grounded model
    
    Returns:
        TermSet: solution
    """
    options = '--configuration jumpy --opt-strategy=usc,oll'
    best_model = None
    models = clyngor.solve_from_grounded(grounding, options=options, use_clingo_module=False)
    for model in models.discard_quotes.by_arity.with_optimization:
        best_model = model
    return best_model


def get_communities(lp_instance, encoding):
    """Get optimal community, from TermSet
    
    Args:
        lp_instance (TermSet): microbiota model
        encoding (str): ASP model encoding
    
    Returns:
        TermSet: solution
    """
    options = '--configuration jumpy --opt-strategy=usc,5'
    prg = [encoding, lp_instance]
    best_model = None
    models = clyngor.solve(prg, options=options, use_clingo_module=False)
    for model in models.discard_quotes.by_arity.with_optimization:
        best_model = model

    return best_model

def get_intersection_communities_from_g(grounding, optimum):
    """Get intersection of solutions, from grounding
    
    Args:
        grounding (bytes): grounded model
        optimum (str): optimal score
    
    Returns:
        TermSet: intersection
    """
    options = '--configuration jumpy --opt-strategy=usc,5 --enum-mode cautious --opt-mode=optN,' +str(optimum)
    models = clyngor.solve_from_grounded(grounding, options=options, use_clingo_module=False)
    for model in models.discard_quotes.by_arity.with_optimization:
        best_model = model

    return best_model

def get_intersection_communities_from_g_noopti(grounding):
    """Get intersection of solutions, from grounding, without optimal score
    
    Args:
        grounding (bytes): grounded model
    
    Returns:
        TermSet: intersection
    """
    options = '--configuration jumpy --opt-strategy=usc,5 --enum-mode cautious --opt-mode=optN'
    models = clyngor.solve_from_grounded(grounding, options=options, use_clingo_module=False)
    for model in models.discard_quotes.by_arity.with_optimization:
        best_model = model

    return best_model

def get_intersection_communities_opti(lp_instance, optimum, encoding):
    """Get intersection of solutions, from TermSet
    
    Args:
        lp_instance (TermSet): microbiota model
        optimum (str): optimal score
        encoding (str): ASP model encoding

    Returns:
        TermSet: intersection
    """
    options = '--configuration jumpy --opt-strategy=usc,5 --enum-mode cautious --opt-mode=optN,' + str(optimum)
    prg = [encoding, lp_instance]
    best_model = None
    models = clyngor.solve(prg, options=options, use_clingo_module=False)
    for model in models.discard_quotes.by_arity.with_optimization:
        best_model = model

    return best_model

def get_intersection_communities(lp_instance, encoding):
    """Get intersection of solutions, from TermSet
    
    Args:
        lp_instance (TermSet): microbiota model
        optimum (str): optimal score
        encoding (str): ASP model encoding

    Returns:
        TermSet: intersection
    """
    options = '--configuration jumpy --opt-strategy=usc,5 --enum-mode cautious --opt-mode=optN'
    prg = [encoding, lp_instance]
    best_model = None
    models = clyngor.solve(prg, options=options, use_clingo_module=False)
    for model in models.discard_quotes.by_arity.with_optimization:
        best_model = model

    return best_model

def get_all_communities_from_g(grounding, optimum, nmodels=0):
    """Get all optimal communities, from grounding
    
    Args:
        grounding (bytes): grounded model
        optimum (str): optimal score
        nmodels (int, optional): Defaults to 0. number of models to compute, 0 = all
    
    Returns:
        list: list of Termsets
    """
    options = '--configuration handy --opt-strategy=usc,5 --opt-mode=optN,' +str(optimum)
    models = clyngor.solve_from_grounded(grounding, options=options, nb_model=nmodels, use_clingo_module=False).by_arity.discard_quotes
    opt_models = clyngor.opt_models_from_clyngor_answers(models)

    return opt_models

def get_all_communities_from_g_noopti(grounding, nmodels=0):
    """Get all optimal communities, from grounding, without optimal score
    
    Args:
        grounding (bytes): grounded model
        nmodels (int, optional): Defaults to 0. number of models, 0 = all

    Returns:
        list: list of TermSets
    """
    options = '--configuration handy --opt-strategy=usc,5 --opt-mode=optN'
    models = clyngor.solve_from_grounded(grounding, options=options, nb_model=nmodels, use_clingo_module=False).by_arity.discard_quotes
    opt_models = clyngor.opt_models_from_clyngor_answers(models)

    return opt_models

def get_all_communities_opti(lp_instance, optimum, encoding, nmodels=0):
    """Get all communities, from TermSet

    Args:
        lp_instance (TermSet): microbiota model
        optimum (str): optimal score
        encoding (str): ASP model encoding file
        nmodels (int, optional): Defaults to 0. number of models, 0 = all

    Returns:
        list: list of TermSets
    """
    options = '--configuration handy --opt-strategy=usc,0 --opt-mode=optN,' + str(optimum)
    prg = [encoding, lp_instance]
    models = clyngor.solve(prg, options=options, nb_model=nmodels, use_clingo_module=False).by_arity.discard_quotes
    opt_models = clyngor.opt_models_from_clyngor_answers(models)

    return opt_models

def get_all_communities(lp_instance, encoding, nmodels=0):
    """Get all communities, from TermSet
    
    Args:
        lp_instance (TermSet): microbiota model
        optimum (str): optimal score
        encoding (str): ASP model encoding file
        nmodels (int, optional): Defaults to 0. number of models, 0 = all
    
    Returns:
        list: list of TermSets
    """
    options = '--configuration handy --opt-strategy=usc,0 --opt-mode=optN'
    prg = [encoding, lp_instance]
    opt_models = clyngor.opt_models_from_clyngor_answers(clyngor.solve(prg, options=options, nb_model=nmodels, use_clingo_module=False).by_arity.discard_quotes)

    return opt_models

def get_union_communities_from_g(grounding, optimum):
    """Get union of all community solutions
    
    Args:
        grounding (bytes): grounded model
        optimum (str): optimal score
    
    Returns:
        TermSet: union
    """
    options = '--configuration jumpy --opt-strategy=usc,5 --enum-mode=brave --opt-mode=optN,' + str(optimum)
    models = clyngor.solve_from_grounded(grounding, options=options, use_clingo_module=False)
    best_model = None
    for model in models.by_arity.discard_quotes.with_optimization:
        best_model = model

    return best_model

def get_union_communities_from_g_noopti(grounding):
    """Get union of all community solutions, from grounding, without optimal score
    
    Args:
        grounding (bytes): grounded instance
    
    Returns:
        TermSet: union
    """
    options = '--configuration jumpy --opt-strategy=usc,5 --enum-mode brave --opt-mode=optN'
    models = clyngor.solve_from_grounded(grounding, options=options, use_clingo_module=False)
    best_model = None
    for model in models.by_arity.discard_quotes.with_optimization:
        best_model = model

    return best_model

def get_union_communities_optimum(lp_instance, optimum, encoding):
    """Get union of community solutions, from TermSet

    Args:
        lp_instance (TermSet): microbiota model
        optimum (str): optimal score
        encoding (str): ASP encoding model file
    
    Returns:
        TermSet: union
    """
    options ='--configuration jumpy --opt-strategy=usc,5 --enum-mode=brave --opt-mode=optN --opt-bound='+str(optimum)
    prg = [encoding, lp_instance]
    best_model = None
    models = clyngor.solve(prg, options=options, use_clingo_module=False)
    for model in models.discard_quotes.by_arity.with_optimization:
        best_model = model

    return best_model

def get_union_communities(lp_instance, encoding):
    """Get union of community solutions, from TermSet

    Args:
        lp_instance (TermSet): microbiota model
        optimum (str): optimal score
        encoding (str): ASP encoding model file
    
    Returns:
        TermSet: union
    """
    options ='--configuration jumpy --opt-strategy=usc,5 --enum-mode=brave --opt-mode=optN'
    prg = [encoding, lp_instance]
    best_model = None
    models = clyngor.solve(prg, options=options, use_clingo_module=False)
    for model in models.discard_quotes.by_arity.with_optimization:
        best_model = model

    return best_model

def get_unproducible(draft, seeds, targets, encoding):
    """Get unproducible targets in a microbiota
    
    Args:
        draft (TermSet): metabolic model
        seeds (TermSet): seeds
        targets (TermSet): targets
        encoding (str): ASP model encoding
    
    Returns:
        TermSet: unproducible targets
    """
    draft_f = utils.to_file(draft)
    seed_f =  utils.to_file(seeds)
    target_f = utils.to_file(targets)
    prg = [encoding, draft_f, seed_f, target_f]
    solver = Gringo4Clasp()
    models = solver.run(prg,collapseTerms=True,collapseAtoms=False)
    os.unlink(draft_f)
    os.unlink(seed_f)
    os.unlink(target_f)

    return models[0]

def get_transported(instance, encoding):
    """Get transported metabolites
    
    Args:
        instance (TermSet): microbiota model
        encoding (str): ASP model encoding
    
    Returns:
        TermSet: transported metabolites
    """
    instance_f = utils.to_file(instance)
    prg = [encoding, instance_f]
    solver = Gringo4Clasp()
    models = solver.run(prg,collapseTerms=True,collapseAtoms=False)
    os.unlink(instance_f)

    return models[0]


def get_grounded_instance_exchanged_metabolites(instance, encoding, exchanged_in_escope=False):
    """Get grounding under compartmentalized framework
    
    Args:
        instance (TermSet): microbiota model
        encoding (str): ASP model encoding
        exchanged_in_escope (bool, default=False): additional option for ASP
    
    Returns:
        bytes: grounded model
    """
    instance_f = utils.to_file(instance)
    if exchanged_in_escope:
        options = "--const exchanged_in_escope=1"
    else:
        options = "--const exchanged_in_escope=0"
    print(os.path.abspath(instance_f))
    prg = [encoding, instance_f]
    grounder = Gringo4(gringo_options=options)
    grounding = grounder.run(prg)
    os.unlink(instance_f)

    return grounding

def get_grounded_instance_exchanged_metabolites_from_file(instance_f, encoding, exchanged_in_escope=False):
    """Get grounding from file
    
    Args:
        instance_f (str): microbiota model file
        encoding (str): ASP model encoding
        exchanged_in_escope (bool, default=False): additional ASP option
    
    Returns:
        bytes: grounded model
    """
    if exchanged_in_escope:
        options = "--const exchanged_in_escope=1"
    else:
        options = "--const exchanged_in_escope=0"
    print(os.path.abspath(instance_f))
    prg = [encoding, instance_f]
    grounder = Gringo4(gringo_options=options)
    grounding = grounder.run(prg)
    return grounding

def get_exchanged_metabolites_onesol(grounding):
    """Select community in compartmentalized framework
    
    Args:
        grounding (bytes): grounded model
    
    Returns:
        TermSet: solution
    """
    options = "--configuration=jumpy --opt-strategy=usc,5"
    solver = Clasp(clasp_options=options)
    models = solver.run(grounding,collapseTerms=True,collapseAtoms=False)
    return models

def get_exchanged_metabolites_intersection(grounding, optimum):
    """Get intersection of communities solutions
    
    Args:
        grounding (bytes): grounded model
        optimum (str): optimal score
    
    Returns:
        TermSet: intersection
    """
    options='--configuration jumpy --opt-strategy=usc,5 --enum-mode cautious --opt-mode=optN --opt-bound='+str(optimum)
    solver = Clasp(clasp_options=options)
    intersec = solver.run(grounding, collapseTerms=True, collapseAtoms=False)
    return intersec[0]

def get_exchanged_metabolites_allsol(grounding, optimum, nmodels=0):
    """Get all communities
    
    Args:
        grounding (bytes): grounded model
        optimum (str): optimal score
        nmodels (int, optional): Defaults to 0. number of models, 0 = all
    
    Returns:
        Set: set of TermSets
    """
    options = str(nmodels)+' --configuration jumpy --opt-strategy=usc,5 --opt-mode=optN --opt-bound='+str(optimum)
    solver = Clasp(clasp_options=options)
    models = solver.run(grounding, collapseTerms=True, collapseAtoms=False)
    return models

def get_exchanged_metabolites_union(grounding, optimum):
    """Get union of community solutions
    
    Args:
        grounding (bytes): grounded model
        optimum (str): optimal score
    
    Returns:
        TermSet: union
    """
    options ='--configuration jumpy --opt-strategy=usc,5 --enum-mode brave --opt-mode=optN --opt-bound='+str(optimum)
    solver = Clasp(clasp_options=options)
    union = solver.run(grounding, collapseTerms=True, collapseAtoms=False)
    return union[0]
