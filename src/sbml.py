#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import re
from pyasp.asp import *
from pyasp.term import *
import xml.etree.ElementTree as etree
from xml.etree.ElementTree import XML, fromstring, tostring

def get_model(sbml):
    """
    return the model of a SBML
    """
    model_element = None
    for e in sbml:
        if e.tag[0] == "{":
            uri, tag = e.tag[1:].split("}")
        else:
            tag = e.tag
        if tag == "model":
            model_element = e
            break
    return model_element

def get_listOfCompartments(model):
    listOfCompartments = None
    for e in model:
        if e.tag[0] == "{":
          uri, tag = e.tag[1:].split("}")
        else: tag = e.tag
        if tag == "listOfCompartments":
          listOfCompartments = e
          break
    return(listOfCompartments)

def get_listOfSpecies(model):
    """
    return list of species of a SBML model
    """
    listOfSpecies = None
    for e in model:
        if e.tag[0] == "{":
            uri, tag = e.tag[1:].split("}")
        else:
            tag = e.tag
        if tag == "listOfSpecies":
            listOfSpecies = e
            break
    return listOfSpecies

def get_listOfReactions(model):
    """
    return list of reactions of a SBML model
    """
    listOfReactions = None
    for e in model:
        if e.tag[0] == "{":
            uri, tag = e.tag[1:].split("}")
        else:
            tag = e.tag
        if tag == "listOfReactions":
            listOfReactions = e
            break
    return listOfReactions

def get_listOfReactants(reaction):
    """
    return list of reactants of a reaction
    """
    listOfReactants = None
    for e in reaction:
        if e.tag[0] == "{":
            uri, tag = e.tag[1:].split("}")
        else:
            tag = e.tag
        if tag == "listOfReactants":
            listOfReactants = e
            break
    return listOfReactants

def get_listOfProducts(reaction):
    """
    return list of products of a reaction
    """
    listOfProducts = None
    for e in reaction:
        if e.tag[0] == "{":
            uri, tag = e.tag[1:].split("}")
        else:
            tag = e.tag
        if tag == "listOfProducts":
            listOfProducts = e
            break
    return listOfProducts

def readSBMLnetwork(filename, name) :
    """
    Read a SBML network and turn it into ASP-friendly data
    """
    lpfacts = TermSet()

    tree = etree.parse(filename)
    sbml = tree.getroot()
    model = get_model(sbml)

    listOfReactions = get_listOfReactions(model)
    for e in listOfReactions:
        if e.tag[0] == "{":
            uri, tag = e.tag[1:].split("}")
        else:
            tag = e.tag
        if tag == "reaction":
            reactionId = e.attrib.get("id")
            lpfacts.add(Term('dreaction', ["\""+reactionId+"\""])) #, "\""+name+"\""
            if(e.attrib.get("reversible")=="true"):
                lpfacts.add(Term('reversible', ["\""+reactionId+"\""]))

            listOfReactants = get_listOfReactants(e)
            # if listOfReactants == None :
            #     print("\n Warning:",reactionId, "listOfReactants=None")
            if listOfReactants != None:
                for r in listOfReactants:
                    lpfacts.add(Term('reactant', ["\""+r.attrib.get("species")+"\"", "\""+reactionId+"\""])) #,"\""+name+"\""

            listOfProducts = get_listOfProducts(e)
            # if listOfProducts == None:
            #     print("\n Warning:",reactionId, "listOfProducts=None")
            if listOfProducts != None:
                for p in listOfProducts:
                    lpfacts.add(Term('product', ["\""+p.attrib.get("species")+"\"", "\""+reactionId+"\""])) #,"\""+name+"\""
    listofspecies = get_listOfSpecies(model)
    for e in listofspecies:
        if e.tag[0] == "{":
            uri, tag = e.tag[1:].split("}")
        else: tag = e.tag
        if tag == "species":
            speciesId = e.attrib.get("id")
            speciesNm = e.attrib.get("name")
            compartment = e.attrib.get("compartment")
            lpfacts.add(Term('species', ["\""+speciesId+"\"", "\""+speciesNm+"\"", "\""+compartment+"\"", "\""+name+"\""]))
    #print(lpfacts)
    return lpfacts

def readSBMLnetwork_symbionts(filename, name) :
    """
    Read a SBML network and turn it into ASP-friendly data with a ID for each fact
    """
    lpfacts = TermSet()

    tree = etree.parse(filename)
    sbml = tree.getroot()
    model = get_model(sbml)

    listOfReactions = get_listOfReactions(model)
    for e in listOfReactions:
        if e.tag[0] == "{":
            uri, tag = e.tag[1:].split("}")
        else:
            tag = e.tag
        if tag == "reaction":
            reactionId = e.attrib.get("id")
            lpfacts.add(Term('reaction', ["\""+reactionId+"\"", "\""+name+"\""])) #, "\""+name+"\""
            if(e.attrib.get("reversible")=="true"):
                lpfacts.add(Term('reversible', ["\""+reactionId+"\"", "\""+name+"\""]))

            listOfReactants = get_listOfReactants(e)
            # if listOfReactants == None :
            #     print("\n Warning:" + reactionId + "listOfReactants=None")
            if listOfReactants != None:
                for r in listOfReactants:
                    lpfacts.add(Term('reactant', ["\""+r.attrib.get("species")+"\"", "\""+reactionId+"\"", "\""+name+"\""])) #,"\""+name+"\""

            listOfProducts = get_listOfProducts(e)
            # if listOfProducts == None:
            #     print("\n Warning:" + reactionId + "listOfProducts=None")
            if listOfProducts != None:
                for p in listOfProducts:
                    lpfacts.add(Term('product', ["\""+p.attrib.get("species")+"\"", "\""+reactionId+"\"", "\""+name+"\""])) #,"\""+name+"\""
    listofspecies = get_listOfSpecies(model)
    for e in listofspecies:
        if e.tag[0] == "{":
            uri, tag = e.tag[1:].split("}")
        else: tag = e.tag
        if tag == "species":
            speciesId = e.attrib.get("id")
            speciesNm = e.attrib.get("name")
            compartment = e.attrib.get("compartment")
            lpfacts.add(Term('species', ["\""+speciesId+"\"", "\""+speciesNm+"\"", "\""+compartment+"\"", "\""+name+"\""]))

    #print(lpfacts)
    return lpfacts

def readSBMLnetwork_symbionts_noemptyrctprd(filename, name) :
    """
    Read a SBML network and turn it into ASP-friendly data with a ID for each fact
    """
    lpfacts = TermSet()

    tree = etree.parse(filename)
    sbml = tree.getroot()
    model = get_model(sbml)

    listOfReactions = get_listOfReactions(model)
    for e in listOfReactions:
        if e.tag[0] == "{":
            uri, tag = e.tag[1:].split("}")
        else:
            tag = e.tag
        if tag == "reaction":
            reactionId = e.attrib.get("id")

            listOfReactants = get_listOfReactants(e)
            listOfProducts = get_listOfProducts(e)
            # if listOfReactants == None :
            #     print("\n Warning:" + reactionId + "listOfReactants=None")
            if listOfReactants != None and listOfProducts != None:
                lpfacts.add(Term('reaction', ["\""+reactionId+"\"", "\""+name+"\""])) #, "\""+name+"\""
                if e.attrib.get("reversible")=="true":
                    lpfacts.add(Term('reversible', ["\""+reactionId+"\"", "\""+name+"\""]))
                for r in listOfReactants:
                    lpfacts.add(Term('reactant', ["\""+r.attrib.get("species")+"\"", "\""+reactionId+"\"", "\""+name+"\""])) #,"\""+name+"\""
                for p in listOfProducts:
                    lpfacts.add(Term('product', ["\""+p.attrib.get("species")+"\"", "\""+reactionId+"\"", "\""+name+"\""])) #,"\""+name+"\""
            else:
                print("reaction " + reactionId + " was ignored due to absent reactants or products")
    listofspecies = get_listOfSpecies(model)
    for e in listofspecies:
        if e.tag[0] == "{":
            uri, tag = e.tag[1:].split("}")
        else: tag = e.tag
        if tag == "species":
            speciesId = e.attrib.get("id")
            speciesNm = e.attrib.get("name")
            compartment = e.attrib.get("compartment")
            lpfacts.add(Term('species', ["\""+speciesId+"\"", "\""+speciesNm+"\"", "\""+compartment+"\"", "\""+name+"\""]))

    #print(lpfacts)
    return lpfacts

def readSBMLnetwork_em(filename, externalcomp="e") :
    """
    Read a SBML network for exchanged metabolites computation
    """
    lpfacts = TermSet()

    tree = etree.parse(filename)
    sbml = tree.getroot()
    model = get_model(sbml)

    name = model.attrib.get("id")
    if name == None:
        print('Error: target and network smbl files for one organism must have identical model IDs. ' + filename + ' network file misses a model ID')
        quit()

    listOfReactions = get_listOfReactions(model)
    for e in listOfReactions:
        if e.tag[0] == "{":
            uri, tag = e.tag[1:].split("}")
        else: tag = e.tag
        if tag == "reaction":
            reactionId = e.attrib.get("id")
            lpfacts.add(Term('dreaction', ["\""+reactionId+"\"", "\""+name+"\""])) #
            if(e.attrib.get("reversible")=="true"):  lpfacts.add(Term('reversible', ["\""+reactionId+"\"", "\""+name+"\""]))

            listOfReactants = get_listOfReactants(e)
            # if listOfReactants== None : print("\n Warning:" + reactionId, " listOfReactants=None")
            #else:
            if listOfReactants != None:
                for r in listOfReactants:
                    lpfacts.add(Term('reactant', ["\""+r.attrib.get("species")+"\"", "\""+reactionId+"\"","\""+name+"\""])) #

            listOfProducts = get_listOfProducts(e)
            # if listOfProducts== None : print("\n Warning:" + reactionId, " listOfProducts=None")
            #else:
            if listOfProducts != None:
                for p in listOfProducts:
                    lpfacts.add(Term('product', ["\""+p.attrib.get("species")+"\"", "\""+reactionId+"\"","\""+name+"\""])) #
    lpfacts.add(Term('organism', ["\"" + name + "\""]))
    lpfacts.add(Term('external', ["\"" + externalcomp + "\""]))

    listofspecies = get_listOfSpecies(model)
    for e in listofspecies:
        if e.tag[0] == "{":
            uri, tag = e.tag[1:].split("}")
        else: tag = e.tag
        if tag == "species":
            speciesId = e.attrib.get("id")
            speciesNm = e.attrib.get("name")
            compartment = e.attrib.get("compartment")
            lpfacts.add(Term('species', ["\""+speciesId+"\"", "\""+speciesNm+"\"", "\""+compartment+"\"", "\""+name+"\""]))

    listofcompartments = get_listOfCompartments(model)
    for e in listofcompartments:
        if e.tag[0] == "{":
            uri, tag = e.tag[1:].split("}")
        else: tag = e.tag
        if tag == "compartment":
            compartmentId = e.attrib.get("id")
            lpfacts.add(Term('compartment', ["\""+compartmentId+"\"", "\""+name+"\""]))
    #print(lpfacts)
    return lpfacts, name

def readSBMLnetwork_em_noemptyrctprd(filename, externalcomp="e") :
    """
    Read a SBML network for exchanged metabolites computation
    """
    lpfacts = TermSet()

    tree = etree.parse(filename)
    sbml = tree.getroot()
    model = get_model(sbml)

    name = model.attrib.get("id")
    if name == None:
        print('Error: target and network smbl files for one organism must have identical model IDs. ' + filename + ' network file misses a model ID')
        quit()

    listOfReactions = get_listOfReactions(model)
    for e in listOfReactions:
        if e.tag[0] == "{":
            uri, tag = e.tag[1:].split("}")
        else: tag = e.tag
        if tag == "reaction":
            reactionId = e.attrib.get("id")

            listOfReactants = get_listOfReactants(e)
            listOfProducts = get_listOfProducts(e)
            # if listOfReactants == None :
            #     print("\n Warning:" + reactionId + "listOfReactants=None")
            if listOfReactants != None and listOfProducts != None:
                lpfacts.add(Term('dreaction', ["\""+reactionId+"\"", "\""+name+"\""])) #
                if(e.attrib.get("reversible")=="true"):  lpfacts.add(Term('reversible', ["\""+reactionId+"\"", "\""+name+"\""]))
                if e.attrib.get("reversible")=="true":
                    lpfacts.add(Term('reversible', ["\""+reactionId+"\"", "\""+name+"\""]))
                for r in listOfReactants:
                    lpfacts.add(Term('reactant', ["\""+r.attrib.get("species")+"\"", "\""+reactionId+"\"", "\""+name+"\""])) #,"\""+name+"\""
                for p in listOfProducts:
                    lpfacts.add(Term('product', ["\""+p.attrib.get("species")+"\"", "\""+reactionId+"\"", "\""+name+"\""])) #,"\""+name+"\""
            else:
                print("reaction " + reactionId + " was ignored due to absent reactants or products ( org=" + name +' )')

    lpfacts.add(Term('organism', ["\"" + name + "\""]))
    lpfacts.add(Term('external', ["\"" + externalcomp + "\""]))

    listofspecies = get_listOfSpecies(model)
    for e in listofspecies:
        if e.tag[0] == "{":
            uri, tag = e.tag[1:].split("}")
        else: tag = e.tag
        if tag == "species":
            speciesId = e.attrib.get("id")
            speciesNm = e.attrib.get("name")
            compartment = e.attrib.get("compartment")
            lpfacts.add(Term('species', ["\""+speciesId+"\"", "\""+speciesNm+"\"", "\""+compartment+"\"", "\""+name+"\""]))

    listofcompartments = get_listOfCompartments(model)
    for e in listofcompartments:
        if e.tag[0] == "{":
            uri, tag = e.tag[1:].split("}")
        else: tag = e.tag
        if tag == "compartment":
            compartmentId = e.attrib.get("id")
            lpfacts.add(Term('compartment', ["\""+compartmentId+"\"", "\""+name+"\""]))
    #print(lpfacts)
    return lpfacts, name


# read the targets

def readSBMLtargets(filename) :

    lpfacts = TermSet()

    tree = etree.parse(filename)
    sbml = tree.getroot()
    model = get_model(sbml)

    name = model.attrib.get("id")
    if name == None:
        print('Error: target and network smbl files for one organism must have identical model IDs. ' + filename + ' target file misses a model ID')
        quit()

    listOfSpecies = get_listOfSpecies(model)
    for e in listOfSpecies:
        if e.tag[0] == "{":
            uri, tag = e.tag[1:].split("}")
        else: tag = e.tag
        if tag == "species":
            lpfacts.add(Term('target', ["\""+e.attrib.get("id")+"\"", "\""+name+"\""]))
    return lpfacts, name

# read the seeds or targets if no need for the id of the model (in xml)

def readSBMLspecies(filename, speciestype) :
    """
    Read a SBML network return its species as seeds or targets
    """
    lpfacts = TermSet()

    tree = etree.parse(filename)
    sbml = tree.getroot()
    model = get_model(sbml)

    listOfSpecies = get_listOfSpecies(model)
    for e in listOfSpecies:
        if e.tag[0] == "{":
            uri, tag = e.tag[1:].split("}")
        else:
            tag = e.tag
        if tag == "species":
            lpfacts.add(Term(speciestype, ["\""+e.attrib.get("id")+"\""]))
    return lpfacts
