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

import argparse
import logging
import pkg_resources
import sys
import time

from miscoto.miscoto_instance import run_instance
from miscoto.miscoto_mincom import run_mincom
from miscoto.miscoto_scopes import run_scopes
from miscoto.miscoto_focus import run_focus
from shutil import which

VERSION = pkg_resources.get_distribution("miscoto").version
LICENSE = """Copyright (C) Dyliss
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
miscoto is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.\n
"""
MESSAGE = """
Explore microbiomes and select minimal communities within them.
"""
REQUIRES = """
Requires Clingo and clyngor package: "pip install clyngor clyngor-with-clingo"
"""

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Check ASP binaries.
if not which('clingo'):
    logger.critical('clingo is not in the Path, miscoto can not work without it.')
    logger.critical('You can install with: pip install clyngor-with-clingo')
    sys.exit(1)

logging.basicConfig(format='%(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def main():
    """Run programm.
    """
    start_time = time.time()
    parser = argparse.ArgumentParser(
        "miscoto",
        description=MESSAGE + " For specific help on each subcommand use: miscoto {cmd} --help",
        epilog=REQUIRES
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s " + VERSION + "\n" + LICENSE)

    # parent parser
    # Miscoto instance specific arguments.
    parent_parser_b = argparse.ArgumentParser(add_help=False)
    parent_parser_b.add_argument(
        "-b",
        "--bactsymbionts",
        dest="bactsymbionts",
        help="directory of symbionts models, all in sbml format",
        required=True,
    )
    parent_parser_s = argparse.ArgumentParser(add_help=False)
    parent_parser_s.add_argument(
        "-s",
        "--seeds",
        dest="seeds",
        help="seeds in SBML format",
        required=True,
    )
    parent_parser_m = argparse.ArgumentParser(add_help=False)
    parent_parser_m.add_argument(
        "-m",
        "--modelhost",
        dest="modelhost",
        help="host metabolic network in SBML format",
        required=False,
    )
    parent_parser_t = argparse.ArgumentParser(add_help=False)
    parent_parser_t.add_argument(
        "-t",
        "--targets",
        dest="targets",
        help="targets in SBML format",
        required=False,
    )
    parent_parser_o = argparse.ArgumentParser(add_help=False)
    parent_parser_o.add_argument(
        "--output",
        dest="output",
        help="output file",
        required=False,
    )

    # Miscoto mincom and scopes specific arguments.
    # Need to recreate some arguments as they are optional in mincom and scopes.
    parent_parser_opt_b = argparse.ArgumentParser(add_help=False)
    parent_parser_opt_b.add_argument(
        "-b",
        "--bactsymbionts",
        dest="bactsymbionts",
        help="directory of symbionts models, all in sbml format",
        required=False,
    )
    parent_parser_opt_s = argparse.ArgumentParser(add_help=False)
    parent_parser_opt_s.add_argument(
        "-s",
        "--seeds",
        dest="seeds",
        help="seeds in SBML format",
        required=False,
    )
    parent_parser_a = argparse.ArgumentParser(add_help=False)
    parent_parser_a.add_argument(
        "-a",
        "--asp",
        dest="asp",
        help="instance if already created with miscoto_instance",
        required=False,
    )

    # Miscoto mincom specific arguments.
    parent_parser_op = argparse.ArgumentParser(add_help=False)
    parent_parser_op.add_argument(
        "-o",
        "--option",
        dest="option",
        help="subcom option: soup, minexch",
        required=True,
    )
    parent_parser_e = argparse.ArgumentParser(add_help=False)
    parent_parser_e.add_argument(
        "--enumeration",
        dest="enumeration",
        help="enumeration of optimal solutions",
        required=False,
        action="store_true"
    )
    parent_parser_i = argparse.ArgumentParser(add_help=False)
    parent_parser_i.add_argument(
        "--intersection",
        dest="intersection",
        help="intersection of optimal solutions",
        required=False,
        action="store_true"
    )
    parent_parser_opt = argparse.ArgumentParser(add_help=False)
    parent_parser_opt.add_argument(
        "--optsol",
        dest="optsol",
        help="one optimal solutions",
        required=False,
        action="store_true"
    )
    parent_parser_u = argparse.ArgumentParser(add_help=False)
    parent_parser_u.add_argument(
        "--union",
        dest="union",
        help="union of optimal solutions",
        required=False,
        action="store_true"
    )

    # Miscoto focus specific argument.
    parent_parser_f = argparse.ArgumentParser(add_help=False)
    parent_parser_f.add_argument(
        "-f",
        "--focus",
        nargs="+",
        dest="focus",
        help="basename of the metabolic network to be analysed in the community",
        required=False,
        default=[]
    )

    parent_parser_all = argparse.ArgumentParser(add_help=False)
    parent_parser_all.add_argument(
        "--all",
        dest="all",
        help="focus on all bacteria of the community",
        required=False,
        action="store_true"
    )

    # subparsers
    subparsers = parser.add_subparsers(
        title='subcommands',
        description='valid subcommands:',
        dest="cmd")
    instance_parser = subparsers.add_parser(
        "instance",
        help="Prepares instance for miscoto.",
        parents=[
            parent_parser_b, parent_parser_s, parent_parser_m, parent_parser_t,
            parent_parser_o
        ],
        description=
        """
        Prepares instance for miscoto. Useful in a benchmark context: pre-calculating
        the instance ensures that SBML files do not have to be read again.
        Instances are text files that can be modified between runs through multiple
        ways, including the use of bash tools
        """
    )

    focus_parser = subparsers.add_parser(
        "focus",
        help="Focus on one, several or all species and determine what they can produce alone or in its community.",
        parents=[
            parent_parser_b, parent_parser_s, parent_parser_f,
            parent_parser_o, parent_parser_all
        ],
        description=
        """
        Calculates the producible metabolites for one (or several or all) metabolic network 
        of interest in two conditions. First when considered alone
        in the given nutritional conditions. Secondly, among its community,
        in the same nutritional conditions but those are necesarily
        altered by what other species are likely to produce.
        The name of the microbe of interest corresponds to the basename of
        its corresponding file in the symbionts input directory, e.g.
        for a file named `ecoli.sbml`, the given basename must be `ecoli`
        """
    )

    mincom_parser = subparsers.add_parser(
        "mincom",
        help="Compute a community from a microbiome.",
        parents=[
            parent_parser_opt_b, parent_parser_opt_s, parent_parser_t,
            parent_parser_m, parent_parser_o,
            parent_parser_op, parent_parser_a, parent_parser_e, parent_parser_i,
            parent_parser_u, parent_parser_opt
        ],
        description=
        """
        Computes a community from a microbiome
        Inputs: SBML models (symbionts and optionally host) + seeds + targets or an
        instance pre-created with miscoto_instance.py,
        option: soup = minimal size community in a mixed-bag
        framework. minexch = minimal size and minimal exchange community.
        Can compute one minimal solution and or union, intersection, enumeration of
        all minimal solutions
        """,
        usage = """
        **1** from SBML files with or without a host metabolic model
        miscoto mincom [-m host.sbml] -b symbiont_directory -s seeds.sbml -t targets.sbml -o option [--intersection] [--union] [--enumeration] [--optsol] [--output]
        \n
        **2** from a pre-computed instance with possibly (additional) seeds or targets
        miscoto mincom -a instance.lp -o option [-s seeds.sbml] [-t targets.sbml] [--intersection] [--union] [--enumeration] [--optsol] [--output]
        \n
        Option -o is either 'soup' or 'minexch' depending on the wanted modeling method
        \n
        """
    )

    scopes_parser = subparsers.add_parser(
        "scopes",
        help="Compute the scope and target produciblity of a host.",
        parents=[
            parent_parser_opt_b, parent_parser_opt_s, parent_parser_t,
            parent_parser_m, parent_parser_o, parent_parser_a
        ],
        description=
        """
        Computes the scope and target produciblity of a host (optional) and the added-value
        of microbiome cooperation regarding scope and target producibility. The microbiome result part
        gives the targets and compounds that are producible providing cooperation occurs
        within the community of host + all symbionts and that were not producible with
        the host alone (if any host provided).
        Computation from SBML models or an instance pre-created with miscoto_instance.py
        """,
        usage="""
        **1** from SBML files with a host metabolic model \n
        miscoto scopes -m host.sbml -b symbiont_directory -s seeds.sbml [-t targets.sbml] [--output outputfile.json]
        \n
        **2** from SBML files of symbionts without host \n
        miscoto scopes -b symbiont_directory -s seeds.sbml [-t targets.sbml] [--output outputfile.json]
        \n
        **3** from a pre-computed instance with possibly (additional) seeds or targets \n
        miscoto scopes -a instance.lp [-s seeds.sbml] [-t targets.sbml] [--output outputfile.json]
        """
    )

    args = parser.parse_args()

    # If no argument print the help.
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if args.cmd == "scopes":
        run_scopes(args.asp, args.targets, args.seeds, args.bactsymbionts, args.modelhost, args.output)
    elif args.cmd == "mincom":
        if args.intersection:
            intersection_arg = True
        else:
            intersection_arg = False
        if args.enumeration:
            enumeration_arg = True
        else:
            enumeration_arg = False
        if args.union:
            union_arg = True
        else:
            union_arg = False
        if args.optsol:
            optsol = True
        else:
            optsol = False
        run_mincom(args.option, args.bactsymbionts, args.asp, args.targets, args.seeds, args.modelhost,
                    intersection_arg, enumeration_arg, union_arg, optsol, args.output)
    elif args.cmd == "instance":
        run_instance(args.bactsymbionts, args.seeds, args.modelhost, args.targets, args.output)
    elif args.cmd == "focus":
        if not args.all and not args.focus:
            logger.error("ERROR - Either a list of networks with -f/--focus or the --all flag must be given as arguments.")
            sys.exit(1)
        if args.all and args.focus:
            logger.warning("WARNING - The --focus/-f argument was given along with the --all flag. All metabolic networks will be considered for analysis.")

        run_focus(args.seeds, args.bactsymbionts, args.focus, args.output, args.all)
    else:
        logger.critical("Invalid commands for miscoto.")
        parser.print_help()
        sys.exit(1)
