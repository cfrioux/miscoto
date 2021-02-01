#!/usr/bin/python
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

import re
import sys
import xml.etree.ElementTree as etree
from xml.etree.ElementTree import XML, fromstring, tostring
from clyngor.as_pyasp import TermSet, Atom

def get_model(sbml):
    """Get the model of a SBML

    Args:
        sbml (str): SBML file

    Returns:
        xml.etree.ElementTree.Element: SBML model
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
    """Get list of compartments in a SBML model
    
    Args:
        model (xml.etree.ElementTree.Element): SBML model
    
    Returns:
        xml.etree.ElementTree.Element: list of compartments
    """
    listOfCompartments = None
    for e in model:
        if e.tag[0] == "{":
          uri, tag = e.tag[1:].split("}")
        else: tag = e.tag
        if tag == "listOfCompartments":
          listOfCompartments = e
          break
    return listOfCompartments

def get_listOfSpecies(model):
    """Get list of Species of a SBML model
    
    Args:
        model (xml.etree.ElementTree.Element): SBML model
    
    Returns:
        xml.etree.ElementTree.Element: list of species
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
    """Get list of reactions of a SBML model
    
    Args:
        model (xml.etree.ElementTree.Element): SBML model
    
    Returns:
        xml.etree.ElementTree.Element: list of reactions
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
    """Get list of reactants of a reaction
    
    Args:
        reaction (xml.etree.ElementTree.Element): reaction
    
    Returns:
        xml.etree.ElementTree.Element: list of reactants
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
    """Get list of porducts of a reaction
    
    Args:
        reaction (xml.etree.ElementTree.Element): reaction
    
    Returns:
        xml.etree.ElementTree.Element: list of products
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

def readSBMLnetwork_symbionts(filename, name) :
    """Read a SBML metabolic network
    
    Args:
        filename (str): SBML file
        name (str): suffix to identify the type of network
    
    Returns:
        TermSet: metabolic model
    """
    lpfacts = TermSet()

    tree = etree.parse(filename)
    sbml = tree.getroot()
    model = get_model(sbml)

    listOfReactions = get_listOfReactions(model)
    if listOfReactions is None:
        logger.critical('No reaction in SBML '+filename)
        sys.exit(1)
    for e in listOfReactions:
        if e.tag[0] == "{":
            uri, tag = e.tag[1:].split("}")
        else:
            tag = e.tag
        if tag == "reaction":
            reactionId = e.attrib.get("id")
            lpfacts.add(Term('reaction', ["\""+reactionId+"\"", "\""+name+"\""])) 
            if(e.attrib.get("reversible")=="true"):
                lpfacts.add(Term('reversible', ["\""+reactionId+"\"", "\""+name+"\""]))

            listOfReactants = get_listOfReactants(e)
            # if listOfReactants == None :
            #     print("\n Warning:" + reactionId + "listOfReactants=None")
            if listOfReactants != None:
                for r in listOfReactants:
                    lpfacts.add(Term('reactant', ["\""+r.attrib.get("species").replace('"','')+"\"", "\""+reactionId+"\"", "\""+name+"\""])) #,"\""+name+"\""

            listOfProducts = get_listOfProducts(e)
            # if listOfProducts == None:
            #     print("\n Warning:" + reactionId + "listOfProducts=None")
            if listOfProducts != None:
                for p in listOfProducts:
                    lpfacts.add(Term('product', ["\""+p.attrib.get("species").replace('"','')+"\"", "\""+reactionId+"\"", "\""+name+"\""])) #,"\""+name+"\""
    listofspecies = get_listOfSpecies(model)
    for e in listofspecies:
        if e.tag[0] == "{":
            uri, tag = e.tag[1:].split("}")
        else: tag = e.tag
        if tag == "species":
            speciesId = e.attrib.get("id").replace('"','')
            speciesNm = e.attrib.get("name").replace('"','')
            compartment = e.attrib.get("compartment")
            lpfacts.add(Term('species', ["\""+speciesId+"\"", "\""+speciesNm+"\"", "\""+compartment+"\"", "\""+name+"\""]))

    return lpfacts

def readSBMLnetwork_symbionts_clyngor(filename, name) :
    """Read a SBML metabolic network
    
    Args:
        filename (str): SBML file
        name (str): suffix to identify the type of network
    
    Returns:
        TermSet: metabolic model
    """
    all_atoms = set()

    tree = etree.parse(filename)
    sbml = tree.getroot()
    model = get_model(sbml)

    listOfReactions = get_listOfReactions(model)
    if listOfReactions is None:
        logger.critical('No reaction in SBML '+filename)
        sys.exit(1)
    for e in listOfReactions:
        if e.tag[0] == "{":
            uri, tag = e.tag[1:].split("}")
        else:
            tag = e.tag
        if tag == "reaction":
            reactionId = e.attrib.get("id")
            all_atoms.add(Atom('reaction', ["\""+reactionId+"\"", "\""+name+"\""])) 
            if(e.attrib.get("reversible")=="true"):
                all_atoms.add(Atom('reversible', ["\""+reactionId+"\"", "\""+name+"\""]))

            listOfReactants = get_listOfReactants(e)
            # if listOfReactants == None :
            #     print("\n Warning:" + reactionId + "listOfReactants=None")
            if listOfReactants != None:
                for r in listOfReactants:
                    all_atoms.add(Atom('reactant', ["\""+r.attrib.get("species").replace('"','')+"\"", "\""+reactionId+"\"", "\""+name+"\""])) #,"\""+name+"\""

            listOfProducts = get_listOfProducts(e)
            # if listOfProducts == None:
            #     print("\n Warning:" + reactionId + "listOfProducts=None")
            if listOfProducts != None:
                for p in listOfProducts:
                    all_atoms.add(Atom('product', ["\""+p.attrib.get("species").replace('"','')+"\"", "\""+reactionId+"\"", "\""+name+"\""])) #,"\""+name+"\""
    listofspecies = get_listOfSpecies(model)
    for e in listofspecies:
        if e.tag[0] == "{":
            uri, tag = e.tag[1:].split("}")
        else: tag = e.tag
        if tag == "species":
            try:
                speciesId = e.attrib.get("id").replace('"','')
            except AttributeError:
                sys.exit("Empty ID field for species in the following SBML: " + filename)
            try:
                speciesNm = e.attrib.get("name").replace('"','')
            except AttributeError:
                sys.exit("Empty name field for species in the following SBML: " + filename)
            try:
                compartment = e.attrib.get("compartment")
            except AttributeError:
                sys.exit("Empty compartment field for species in the following SBML: " + filename)
            all_atoms.add(Atom('species', ["\""+speciesId+"\"", "\""+speciesNm+"\"", "\""+compartment+"\"", "\""+name+"\""]))

    lpfacts = TermSet(all_atoms)

    return lpfacts

def readSBMLnetwork_symbionts_noemptyrctprd(filename, name) :
    """Read a SBML metabolic network while ignoring the reactions that have no reactant or product
    
    Args:
        filename (str): SBML file
        name (str): suffix to identify the type of network
    
    Returns:
        TermSet: metabolic model
    """
    lpfacts = TermSet()

    tree = etree.parse(filename)
    sbml = tree.getroot()
    model = get_model(sbml)

    listOfReactions = get_listOfReactions(model)
    if listOfReactions is None:
        logger.critical('No reaction in SBML '+filename)
        sys.exit(1)
    for e in listOfReactions:
        if e.tag[0] == "{":
            uri, tag = e.tag[1:].split("}")
        else:
            tag = e.tag
        if tag == "reaction":
            reactionId = e.attrib.get("id")

            listOfReactants = get_listOfReactants(e)
            listOfProducts = get_listOfProducts(e)
            if listOfReactants != None and listOfProducts != None:
                lpfacts.add(Term('reaction', ["\""+reactionId+"\"", "\""+name+"\""]))
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

    lpfacts = TermSet(all_atoms)
    return lpfacts

def readSBMLnetwork_em(filename, externalcomp="e") :
    """Read a SBML metabolic network while considering external compartment
    
    Args:
        filename (str): SBML file
        externalcomp (str): Default to 'e'. external compartment
    
    Returns:
        TermSet, str: metabolic model and its name
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
    if listOfReactions is None:
        logger.critical('No reaction in SBML '+filename)
        sys.exit(1)
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
    """Read a SBML metabolic network while ignoring the reactions that have no reactant or product
    
    Args:
        filename (str): SBML file
        externalcomp (str): Default to 'e'. external compartment
    
    Returns:
        TermSet, str: metabolic model and its name
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
    if listOfReactions is None:
        logger.critical('No reaction in SBML '+filename)
        sys.exit(1)
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
    return lpfacts, name

def readSBMLtargets(filename):
    """Get SBML targets
    
    Args:
        filename (str): SBML file
    
    Returns:
        TermSet, str: targets and name of the model
    """
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

def readSBMLspecies(filename, speciestype) :
    """Get species of a SBML (seeds, targets)
    
    Args:
        filename (str): SBML file
        speciestype (str): seed or target
    
    Returns:
        TermSet: seeds or targets
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
            lpfacts.add(Term(speciestype, ["\""+e.attrib.get("id").replace('"','')+"\""]))
    return lpfacts

def readSBMLspecies_clyngor(filename, speciestype) :
    """
    Read a SBML network return its species as seeds or targets
    """
    all_atoms = set()

    tree = etree.parse(filename)
    sbml = tree.getroot()
    model = get_model(sbml)

    listOfSpecies = get_listOfSpecies(model)
    if listOfSpecies:
        for e in listOfSpecies:
            if e.tag[0] == "{":
                uri, tag = e.tag[1:].split("}")
            else:
                tag = e.tag
            if tag == "species":
                try:
                    all_atoms.add(Atom(speciestype, ["\""+e.attrib.get("id")+"\""]))
                except TypeError:
                    sys.exit("Empty ID field for species in the following SBML: " + filename)
    else:
        sys.exit("Invalid SBML (missing species or listOfSpecies) " + filename)

    lpfacts = TermSet(all_atoms)

    return lpfacts
