[![PyPI version](https://img.shields.io/pypi/v/miscoto.svg)](https://pypi.org/project/Miscoto/) [![GitHub license](https://img.shields.io/github/license/cfrioux/miscoto.svg)](https://github.com/cfrioux/miscoto/blob/master/LICENSE) [![Actions Status](https://github.com/cfrioux/miscoto/workflows/Python%20package/badge.svg)](https://github.com/cfrioux/miscoto/actions) [![](https://img.shields.io/badge/doi-10.1093/bioinformatics/bty588-blueviolet.svg)](https://academic.oup.com/bioinformatics/article/34/17/i934/5093211)

# MiSCoTo
## Description
**Microbiome Screening and COmmunity selection using TOpology**

MiSCoTo is a Python3 (3.6 and higher) tool to explore microbiomes and select minimal communities within them.
It uses Answer Set Programming (ASP) to optimize community selection.

MiSCoTo follows the producibility in metabolic networks as defined by the [network expansion](http://www.ncbi.nlm.nih.gov/pubmed/15712108) algorithm.
Mainly, two rules are followed:
* a *recursive rule*: the products of a reactions are producible if **all** reactants of this reaction are themselves producible
* an *initiation rule*: producibility is initiated by the presence of nutrients, called *seeds*. 

A metabolite that is producible from a set of nutrients is described as being "in the scope of the seeds".
The computation is made using logic solvers (Answer Set Programming). The present modelling ignores the stoichiometry of reactions (2A + B --> C is considered equivalent to A + B --> C), and is therefore suited to non-curated or draft metabolic networks.

MiSCoTo computes the set of metabolites that are producible by a community (with or without a host). It can also compute minimal communities starting from a large community under a defined objective (production of targets by the community of by the host). 

**If you use MiSCoTo, please cite:** 

*Frioux C, Fremy E, Trottier C, Siegel A. Scalable and exhaustive screening of metabolic functions carried out by microbial consortia. Bioinformatics 2018;34:i934–43. [https://doi.org/10.1093/bioinformatics/bty588](https://doi.org/10.1093/bioinformatics/bty588).*

**If you look for a wider screening of communities, as well as metabolic network reconstruction for a large set of genomes** please look at [Metage2Metabo](https://github.com/AuReMe/metage2metabo)

Inputs: metabolic models, seeds (growth medium) and metabolic targets as SBML files (see examples in [toy](https://github.com/cfrioux/miscoto/tree/master/toy)).

Computations can be performed with a set of symbionts or a set of symbionts and a host. In the latter case, targets will be produced by the host, whereas in the former they will be produced by any member of the microbiota.

Important notice: be sure that two identical metabolites have the same name in all metabolic networks. Otherwise inconsistencies might occur between targets predicted as producible under the "soup" modeling and the "minexch" modeling.

### Microbiome exploration
Computation of the added value of the microbiota over a individual host with respect to targets or the whole scope of producible compounds.

Tool = `miscoto_scope.py`

### Community selection
Community selection uses parsimonious criteria:
* **size minimization** under mixed-bag assumption (one virtual compartment for the whole microbiome)
    * scales up to large microbiomes
    * computation of one, all, union or intersection of all communities
    * first step prior to exchange minimization to reduce the space of solutions
* **size and exchange minimizations** under a compartmentalized framework
    * computation of one, all, union or intersection of all communities and their associated exchanges
    * more computationnally demanding: a first step of size minimization is preferred. Use one selected minimal-size community or their union (if not too large i.e. around 50 symbionts or less on personal computers) as symbiont inputs

Tool = `miscoto_mincom.py`

## Install


Required package (starting from version 2.0 of the package):
* [clyngor](https://github.com/Aluriak/clyngor) (``pip install clyngor==0.3.20``) or  ``clyngor-with-clingo`` (``pip install clyngor-with-clingo``)

```
pip install miscoto
```

## Usage

    usage: miscoto [-h] [-v] {instance,focus,mincom,scopes} ...

    Explore microbiomes and select minimal communities within them. For specific
    help on each subcommand use: miscoto {cmd} --help

    optional arguments:
    -h, --help            show this help message and exit
    -v, --version         show program's version number and exit

    subcommands:
    valid subcommands:

    {instance,focus,mincom,scopes}
        instance            Prepares instance for miscoto.
        focus               Focus on one species and determine what it can produce
                            alone or in its community.
        mincom              Compute a community from a microbiome.
        scopes              Compute the scope and target produciblity of a host.

    Requires Clingo and clyngor package: "pip install clyngor clyngor-with-clingo"

* ``miscoto scopes`` compute the scope and target produciblity of a host (optional) and the added-
value of a microbiome regarding scope and target producibility. The microbiome
result part gives the targets and compounds that are producible providing
cooperation occurs within the community of host + all symbionts and that were
not producible with the host alone. Computation from SBML models or an
instance pre-created with miscoto_instance.py
    * from SBML files

        * usage 1: host, symbionts, seeds, [targets]
        ```
        miscoto scopes -m host.sbml -b symbiont_directory -s seeds.sbml -t targets.sbml [--output output_file]
        ```
        * usage 2: symbionts, seeds, [targets]
        ```
        miscoto scopes -b symbiont_directory -s seeds.sbml -t targets.sbml [--output output_file]
        ```
    * from a pre-computed instance with possibly (additional) seeds or targets
        * usage 3: instance, [seeds], [targets]    
        ```
        miscoto scopes -a instance.lp [-s seeds.sbml] [-t targets.sbml] [--output output_file]
        ```

    ```miscoto scopes``` can be called directly in Python
    ```python
    from miscoto import run_scopes

    run_scopes(lp_instance_file=xxx, targets_file=xxx, \
                seeds_file=xxx, bacteria_dir=xxx, \
                host_file=xxx, output_json=xxx)
    ```

* ``miscoto focus`` calculates the producible metabolites for one metabolic network of interest in
two conditions. First when considered alone in the given nutritional
conditions. Secondly, among its community, in the same nutritional conditions
but those are necesarily altered by what other species are likely to produce.

    Please note that the name of the microbe of interest corresponds to the basename of its corresponding file in the symbionts input directory, e.g. for a file named
    `ecoli.sbml`, the given basename must be `ecoli`.

        -h, --help            show this help message and exit
        -b BACTSYMBIONTS, --bactsymbionts BACTSYMBIONTS
                                directory of symbionts models, all in sbml format
        -s SEEDS, --seeds SEEDS
                                seeds in SBML format
        -f FOCUS, --focus FOCUS
                                basename of the metabolic network to be analysed in
                                the community
        --output OUTPUT       output file in json


    ```miscoto focus``` can be called directly in Python
    ```python
    from miscoto import run_focus

    run_focus(bacteria_dir=xxx, \
                seeds_file=xxx, focus_bact=xxx, \
                output_json=xxx)
    ```


* ``miscoto mincom`` computes a community from a microbiome Inputs: SBML models (symbionts and
optionally host) + seeds + targets or an instance pre-created with
miscoto_instance.py, option: soup = minimal size community in a mixed-bag
framework or minexch = minimal size and minimal exchange community. Can
compute one minimal solution and or union, intersection, enumeration of all
minimal solutions
    * from SBML files 
        * usage 1: host, symbionts, seeds, targets  
        ```
        miscoto mincom -m host.sbml -b symbiont_directory -s seeds.sbml -t targets.sbml -o option [--intersection] [--union] [--enumeration] [--optsol] [--output output_file]
        ```
        * usage 2: symbionts, seeds, targets
        ```
        miscoto mincom -b symbiont_directory -s seeds.sbml -t targets.sbml -o option [--intersection] [--union] [--enumeration] [--optsol] [--output output_file]
        ```

    * from a pre-computed instance with possibly (additional) seeds or targets 
        * usage 3: instance, [seeds], [targets]   
        ```
        miscoto mincom -a instance.lp -o option [-s seeds.sbml] [-t targets.sbml] [--intersection] [--union] [--enumeration] [--optsol] [--output output_file]
        ```
    ```miscoto mincom``` can be called directly in Python
    ```python
    from miscoto import run_mincom

    run_mincom(option='soup/minexch', \
                bacteria_dir=xxx, host_file=xxx,\
                targets_file=xxxx, seeds_file=xxx,\
                optsol=True/False, enumeration=True/False, \
                intersection=True/False, union=True/False, \
                output_json=xxx)

    run_mincom(option='soup/minexch', \
                bacteria_dir=xxx, \
                targets_file=xxxx, seeds_file=xxx,\
                optsol=True/False, enumeration=True/False, \
                intersection=True/False, union=True/False, \
                output_json=xxx)

    run_mincom(option='soup/minexch',\
                lp_instance_file=xxxx,\
                targets_file=xxxx, seeds_file=xxx,
                optsol=True/False, enumeration=True/False, \
                intersection=True/False, union=True/False, \
                output_json=xxx)
    ```

Using the `output_json` option, it is possible to create a json output file with these keys:

    * bacteria: bacteria in the optimal solution
    * still_unprod: unproducible compounds by the community
    * newly_prod: newly producible compounds by the community
    * union_bacteria: bacteria from all the minimal communities
    * inter_bacteria: bacteria from the intersection of all the minimal communities
    * one_model: results of the optimal solution
    * union_exchanged: all the exchanged compounds
    * inter_exchanged: intersection of the exchanged compounds
    * exchanged: exchanged compounds in the optimal solution
    * key_species: bacteria from all the minimal communities
    * essential_symbionts: bacteria from the intersection of all the minimal communities
    * alternative_symbionts: bacteria appearing in at least one minimal community but not in all (if intersection and union options are used)
    * targets_producers: for each target, the list of organisms able to produce this target in the full community with `miscoto_scopes` and in the selected minimal communities with `miscoto_mincom`

## Benchmark tips

For the screening of large communities, ASP-compliant instances can be pre-generated and easily modified to save time by avoiding the reading of all SBML files.
The instance can be modified (usable bacteria with the predicate ``bacteria("xxx").``, targets with predicates ``target("xxx").`` or seeds with predicates ``seeds("xxx").`` for example) using bash commands (e.g. sed) at each run.

``miscoto_instance.py`` creates such instance:

```
miscoto instance [-h] [-m MODELHOST] -s SEEDS [-t TARGETS] -b BACTSYMBIONTS [-o OUTPUT]
```

```python
from miscoto import run_instance

run_instance(bacteria_dir=xxx, seeds_file=xxx, host_file=xxx, targets_file=xxxx, output=xxx)
```
