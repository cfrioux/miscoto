import os
import tempfile
from pyasp.asp import *

def get_scopes(instance_f, encoding):
    prg = [encoding, instance_f]
    options = ''
    solver = Gringo4Clasp(clasp_options=options)
    models = solver.run(prg,collapseTerms=True,collapseAtoms=False)
    return models[0]


def get_grounded_communities(instance, encoding):
    instance_f = instance.to_file()
    # print(os.path.abspath(instance_f))
    prg = [encoding, instance_f]
    grounder = Gringo4()
    grounding = grounder.run(prg)
    os.unlink(instance_f)
    return grounding

def get_grounded_communities_from_file(instance_f, encoding):
    prg = [encoding, instance_f]
    grounder = Gringo4()
    grounding = grounder.run(prg)
    # os.unlink(instance_f)
    return grounding

def get_communities_from_g(grounding):
    options = '--configuration jumpy --opt-strategy=usc,5'
    solver = Clasp(clasp_options=options)
    models = solver.run(grounding,collapseTerms=True,collapseAtoms=False)
    return models[0]

def get_communities(lp_instance, encoding):
    lp_f = lp_instance.to_file()
    prg = [encoding, lp_f]
    print(os.path.abspath(lp_f))
    options = '--configuration jumpy --opt-strategy=usc,5'
    solver = Gringo4Clasp(clasp_options=options)
    models = solver.run(prg,collapseTerms=True,collapseAtoms=False)
    os.unlink(lp_f)
    # print(models[0])
    return models[0]

def get_intersection_communities_from_g(grounding, optimum):
    options = '--configuration jumpy --opt-strategy=usc,5 --enum-mode cautious --opt-mode=optN --opt-bound=' +str(optimum)
    solver = Clasp(clasp_options=options)
    intersec = solver.run(grounding,collapseTerms=True,collapseAtoms=False)
    return intersec[0]

def get_intersection_communities_from_g_noopti(grounding):
    options = '--configuration jumpy --opt-strategy=usc,5 --enum-mode cautious --opt-mode=optN'
    solver = Clasp(clasp_options=options)
    intersec = solver.run(grounding,collapseTerms=True,collapseAtoms=False)
    return intersec[0]


def get_intersection_communities(lp_instance, optimum, encoding):
    lp_f = lp_instance.to_file()
    prg = [encoding, lp_f]
    options = '--configuration jumpy --opt-strategy=usc,5 --enum-mode cautious --opt-mode=optN --opt-bound=' +str(optimum)
    solver = Gringo4Clasp(clasp_options=options)
    intersec = solver.run(prg,collapseTerms=True,collapseAtoms=False)
    os.unlink(lp_f)
    return intersec[0]

def get_all_communities_from_g(grounding, optimum, nmodels=0):
    options = str(nmodels)+' --configuration handy --opt-strategy=usc,5 --opt-mode=optN --opt-bound=' +str(optimum)
    solver = Clasp(clasp_options=options)
    models = solver.run(grounding, collapseTerms=True, collapseAtoms=False)
    return models

def get_all_communities_from_g_noopti(grounding, nmodels=0):
    options = str(nmodels)+' --configuration handy --opt-strategy=usc,5 --opt-mode=optN '
    solver = Clasp(clasp_options=options)
    models = solver.run(grounding, collapseTerms=True, collapseAtoms=False)
    return models

def get_all_communities(lp_instance, optimum, encoding, nmodels=0):
    lp_f = lp_instance.to_file()
    prg = [encoding, lp_f]
    options = str(nmodels)+' --configuration handy --opt-strategy=usc,5 --opt-mode=optN --opt-bound=' +str(optimum)
    solver = Gringo4Clasp(clasp_options=options)
    models = solver.run(prg, collapseTerms=True, collapseAtoms=False)
    os.unlink(lp_f)
    return models

def get_union_communities_from_g(grounding, optimum):
    options ='--configuration jumpy --opt-strategy=usc,5 --enum-mode=brave --opt-mode=optN --opt-bound='+str(optimum)
    solver = Clasp(clasp_options=options)
    union = solver.run(grounding, collapseTerms=True, collapseAtoms=False)
    return union[0]

def get_union_communities_from_g_noopti(grounding):
    options ='--configuration jumpy --opt-strategy=usc,5 --enum-mode brave --opt-mode=optN'
    solver = Clasp(clasp_options=options)
    union = solver.run(grounding, collapseTerms=True, collapseAtoms=False)
    return union[0]

def get_union_communities(lp_instance, optimum, encoding):
    lp_f = lp_instance.to_file()
    prg = [encoding, lp_f]
    options ='--configuration jumpy --opt-strategy=usc,5 --enum-mode=brave --opt-mode=optN --opt-bound='+str(optimum)
    solver = Gringo4Clasp(clasp_options=options)
    union = solver.run(prg, collapseTerms=True, collapseAtoms=False)
    os.unlink(lp_f)
    return union[0]

def get_unproducible(draft, seeds, targets, encoding):
    draft_f = draft.to_file()
    seed_f =  seeds.to_file()
    target_f = targets.to_file()
    prg = [encoding, draft_f, seed_f, target_f]
    solver = Gringo4Clasp()
    models = solver.run(prg,collapseTerms=True,collapseAtoms=False)
    os.unlink(draft_f)
    os.unlink(seed_f)
    os.unlink(target_f)
    return models[0]

def get_transported(instance, encoding):
    instance_f = instance.to_file()
    prg = [encoding, instance_f]
    solver = Gringo4Clasp()
    models = solver.run(prg,collapseTerms=True,collapseAtoms=False)
    # print(os.path.abspath(instance_f))
    os.unlink(instance_f)
    return models[0]


def get_grounded_instance_exchanged_metabolites(instance, encoding, exchanged_in_escope):
    instance_f = instance.to_file()
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

def get_grounded_instance_exchanged_metabolites_from_file(instance_f, encoding, exchanged_in_escope):
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
    options = "--configuration=jumpy --opt-strategy=usc,5"
    solver = Clasp(clasp_options=options)
    models = solver.run(grounding,collapseTerms=True,collapseAtoms=False)
    return models

def get_exchanged_metabolites_intersection(grounding, optimum):
    options='--configuration jumpy --opt-strategy=usc,5 --enum-mode cautious --opt-mode=optN --opt-bound='+str(optimum)
    solver = Clasp(clasp_options=options)
    intersec = solver.run(grounding, collapseTerms=True, collapseAtoms=False)
    return intersec[0]

def get_exchanged_metabolites_allsol(grounding, optimum, nmodels=0):
    options = str(nmodels)+' --configuration jumpy --opt-strategy=usc,5 --opt-mode=optN --opt-bound='+str(optimum)
    solver = Clasp(clasp_options=options)
    models = solver.run(grounding, collapseTerms=True, collapseAtoms=False)
    return models

def get_exchanged_metabolites_union(grounding, optimum):
    options ='--configuration jumpy --opt-strategy=usc,5 --enum-mode brave --opt-mode=optN --opt-bound='+str(optimum)
    solver = Clasp(clasp_options=options)
    union = solver.run(grounding, collapseTerms=True, collapseAtoms=False)
    return union[0]
