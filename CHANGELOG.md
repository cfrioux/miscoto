# Changelog

# MiSCoTo v3.2.0  (2023-04-20)

## New

- `miscoto deadends` to compute deadend and orphan metabolites for the community (issue #15).
- `CHANGLEOG.md` showing the different versions and the associated changes.

## Test

- Add test for miscoto deadends.

## Modify

- Modify miscoto instance to work with only symbionts folder for miscoto deadends (seeds and targets are optional).
- Giving only a subcommand to miscoto returns the associated help.
- Remove some unused imports.
- Update readme according to miscoto deadends.
- Update license year.

## CI

-  Remove mirror to Inria Gitlab due to changes on thhe Gitlab version.

# MiSCoTo v3.1.2  (2022-03-18)

## New

- `miscoto focus` can now be run systematically for all species with the `--all` option

## Fix

- Latest clyngor versions led to errors that can be preventing by not using the clingo module when calling solver #14

## Test

- Tests are no longer done for Python 3.6 but for versions 3.7, 3.8, 3.9

## Doc

- Update `miscoto focus` section

## CI

-  Mirror to Inria Gitlab


# MiSCoTo v3.1.1 (2021-02-22)

## New

`miscoto focus` calculates the producible metabolites for one metabolic network of interest in two conditions. First when considered alone in the given nutritional conditions. Secondly, among its community, in the same nutritional conditions but those are necesarily altered by what other species are likely to produce.

## Doc 

* usage of `miscoto focus`
* fix docstringd

## Tests

* test `miscoto focus`

## Licence

MiSCoTo is now under the LGPL licence

# MiSCoTo v3.1.0 (2021-01-09)

## Fix

* consider reversible reactions to characterise target_producer_coop_initcom
* remove adding a host fact in `miscoto instance`when no host argument was provided

## Test

* test the second fix

# MiSCoTo v3.0.3 (2020-12-03)

## Add

* test for key species in mincom.

## Replace

* "keystone species" by "key species".

# MiSCoTo v3.0.2 (2020-11-18)

## Add

* Windows and MacOS tests in GitHub Actions.
* Windows compatibility.

# MiSCoTo v3.0.1 (2020-11-30)

## Add

* Error message if SBML files have no reactions.

# MiSCoTo v3.0.0 (2020-10-26)

## Add

* Merge all commands into one command with subcommands: e.g. `miscoto_scopes` becomes `miscoto scopes`
* Version can now be retrieved with `miscoto --version`
* Output messages are clearer than before

## Update

* Documentation
* Help of subcommands

## Fix 

* Typos

# MiSCoTo v2.1.2 (2020-09-16)

## New Features

* In `mincom -o soup` return in the json output a  new predicate that contains all producible targets in a minimal community. This new predicate is stored as "producible" in the json output. This featyre is useful in 2 cases:
    * In case there are compounds in targets that are also nutrients (seeds): they would not have appeared in `newly_producible`
    * In case a host is provided: the target compounds that the host can produce by itself would not have been stored in the json

## Fix

* Issue with the display of target producers in selected communities

## CI & Tests

* Add a new test and its associated target file in `toy` related to returning all producible targets

# Miscoto v2.1.1 (2020-07-28)

## Add

- final producers for the targets. Miscoto will search for the organisms able to activate the reaction producing each of the targets. This is computed in the full community with `miscoto_scopes` and in the selected minimal communities with `miscoto_mincom`. The information is stored in the `targets_producers` key in the json output.

## CI

- test for the new final producer feature.

# Miscoto v2.1.0 (2020-07-07)

## Modify mincom json ouput

- rename `optimum_inter` into `score_optimum_inter`

- rename `optimum_union` into `score_optimum_union`

- add result of --optsol in json with the `one_model` key.

- add `keystone_species`, `essential_symbionts` and `alternative_symbionts` in json if --union and --intersection are used together.

# Miscoto v2.0.8 (2020-06-30)

## Fix
* minexch behaviour (missing solution) when running without host

## CI
* add new tests for the above cases

# Miscoto v2.0.7 (2020-04-20)

Improvement of tests, better documentation, Github actions

# Miscoto v2.0.2 (2019-06-03)

First release that uses Clyngor rather than Pyasp for ASP support.

# Miscoto v1.2.0 (2019-06-03)

This is the last release of Miscoto using Pyasp as a support for ASP computing.
This version and the ones before are not compatible with [metage2metabo](https://github.com/AuReMe/metage2metabo)