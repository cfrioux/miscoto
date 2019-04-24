# MiSCoTo
## Description
**Microbiome Screening and COmmunity selection using TOpology**

MiSCoTo is a Python3 tool to explore microbiomes and select minimal communities within them.
It uses Answer Set Programming (ASP) to optimize community selection.

Inputs: metabolic models, seeds (growth medium) and metabolic targets.

Computations can be performed with a set of symbionts or a set of symbionts and a host. In the latter case, targets will be produced by the host, whereas in the former they will be produced by any member of the microbiome.

Important notice: be sure that two identical metabolites have the same name in all metabolic networks. Otherwise inconsistencies might occur between targets predicted as producible under the "soup" modeling and the "minexch" modeling.

Required package:
* ``pyasp`` (``pip install pyasp==1.4.3`` or ``pip install pyasp==1.4.3 --no-cache-dir`` in case of ASP solvers installation issues)

### Microbiome exploration
Computation of the added value of the microbiome over a individual host with respect to targets or the whole scope of producible compounds.

Tool = miscoto_scope.py

### Community selection
Community selection uses parsimonious criteria:
* **size minimization** under mixed-bag assumption (one virtual compartment for the whole microbiome)
    * scales up to large microbiomes
    * computation of one, all, union or intersection of all communities
    * first step prior to exchange minimization to reduce the space of solutions
* **size and exchange minimizations** under a compartmentalized framework
    * computation of one, all, union or intersection of all communities and their associated exchanges
    * more computationnally demanding: a first step of size minimization is preferred. Use one selected minimal-size community or their union (if not too large i.e. around 50 symbionts or less on personal computers) as symbiont inputs

Tool = miscoto_mincom.py

## Install

```
pip install miscoto
```

## Usage

* ``miscoto_scopes`` compute the scope and target produciblity of a host (optional) and the added-
value of a microbiome regarding scope and target producibility. The microbiome
result part gives the targets and compounds that are producible providing
cooperation occurs within the community of host + all symbionts and that were
not producible with the host alone. Computation from SBML models or an
instance pre-created with miscoto_instance.py
    * from SBML files

        * usage 1: host, symbionts, seeds, [targets]
        ```
        miscoto_scopes -m host.sbml -b symbiont_directory -s seeds.sbml -t targets.sbml
        ```
        * usage 2: symbionts, seeds, [targets]
        ```
        miscoto_scopes -b symbiont_directory -s seeds.sbml -t targets.sbml
        ```
    * from a pre-computed instance with possibly (additional) seeds or targets
        * usage 3: instance, [seeds], [targets]    
        ```
        miscoto_scopes -a instance.lp [-s seeds.sbml] [-t targets.sbml]
        ```

    ```miscoto_scopes``` can be called directly in Python
    ```python
    from miscoto import run_scopes

    run_scopes(lp_instance_file=xxx, targets_file=xxx, seeds_file=xxx, bacteria_dir=xxx, host_file=xxx)
    ```


* ``miscoto_mincom`` computes a community from a microbiome Inputs: SBML models (symbionts and
optionally host) + seeds + targets or an instance pre-created with
miscoto_instance.py, option: soup = minimal size community in a mixed-bag
framework or minexch = minimal size and minimal exchange community. Can
compute one minimal solution and or union, intersection, enumeration of all
minimal solutions
    * from SBML files 
        * usage 1: host, symbionts, seeds, targets  
        ```
        miscoto_mincom -m host.sbml -b symbiont_directory -s seeds.sbml -t targets.sbml -o option [--intersection] [--union] [--enumeration] [--optsol]
        ```
        * usage 2: symbionts, seeds, targets
        ```
        miscoto_mincom -b symbiont_directory -s seeds.sbml -t targets.sbml -o option [--intersection] [--union] [--enumeration] [--optsol]
        ```

    * from a pre-computed instance with possibly (additional) seeds or targets 
        * usage 3: instance, [seeds], [targets]   
        ```
        miscoto_mincom -a instance.lp -o option [-s seeds.sbml] [-t targets.sbml] [--intersection] [--union] [--enumeration] [--optsol]
        ```
    ```miscoto_mincom``` can be called directly in Python
    ```python
    from miscoto import run_mincom

    run_mincom(option='soup/minexch', \
                bacteria_dir=xxx, host_file=xxx,\
                targets_file=xxxx, seeds_file=xxx,\
                optsol=True/False, enumeration=True/False, \
                intersection=True/False, union=True/False)

    run_mincom(option='soup/minexch', \
                bacteria_dir=xxx, \
                targets_file=xxxx, seeds_file=xxx,\
                optsol=True/False, enumeration=True/False, \
                intersection=True/False, union=True/False)

    run_mincom(option='soup/minexch',\
                lp_instance_file=xxxx,\
                targets_file=xxxx, seeds_file=xxx,
                optsol=True/False, enumeration=True/False, \
                intersection=True/False, union=True/False)
    ```


## Benchmark tips

For the screening of large communities, ASP-compliant instances can be pre-generated and easily modified to save time by avoiding the reading of all SBML files.
The instance can be modified (usable bacteria with the predicate ``bacteria("xxx").``, targets with predicates ``target("xxx").`` or seeds with predicates ``seeds("xxx").`` for example) using bash commands (e.g. sed) at each run.

``miscoto_instance.py`` creates such instance:

```
miscoto_instance [-h] [-m MODELHOST] -s SEEDS [-t TARGETS] -b BACTSYMBIONTS [-o OUTPUT]
```

```python
from miscoto import run_instance

run_instance(bacteria_dir=xxx, seeds_file=xxx, host_file=xxx, targets_file=xxxx, output=xxx)
```
