import argparse
import asyncio
import os
import re
import time

from aiohttp import ClientSession
from colorama import init, Fore, Back, Style

init(convert=True)


def path_is_valid(parser, path):
    """
    Returns open file handler if path leads
    to valid path.

    Args:
        parser: argparse object
        path: str path to requirements.txt file
    Output:
        file handler or parser error
    """
    try:
        return open(path, 'r')
    except FileNotFoundError:
        parser.error("Following file path \"{}\" does not exist. Please check again.".format(path))


def parse_project_and_version(strategy, requirement):
    """
    Parse requirements line in requirements.txt for 
    project name and version number specified if specified.

    Args:
        strategy: str "wheel" or "normal" determines parsing scheme
        requirement: str requirement line call out
    Output:
        project_info: str tuple (project_name, version_number)
    """
    version_regex = re.compile(r"(\d+(.\d+)+)")

    if strategy == "wheel":
        name_regex = re.compile(r"^\r?\w*(\W(.*)\-\d)")
        project_info = (name_regex.search(requirement).group(2), version_regex.search(requirement).group(1))
    elif strategy == "normal":
        requirement_components = requirement.split("==")
        project_info = (requirement_components[0], version_regex.search(requirement).group(1))
    return project_info


async def get_project_info(project_name, project_version, session):
    """
    Get pypi.org JSON info on project.

    Args:
        project_name: str name of project
        project_version: str requirements listed version number
        session: aiohttp ClientSession object
    Output:
        info: dict with info
    """
    r = await session.request(method="GET", url="https://pypi.org/pypi/{}/{}/json".format(project_name, project_version))
    if r.status == 404:
        print("{} could not be found".format(project_name))
        return
    return await r.json()


def check_compatible(project_name, project_version, project_info, check_version):
    """
    Check if requirement compatible with specific python version.

    Args:
        project_name: str project of interest
        project_version: str requirements listed version number
        project_info: json object received from get_project_info
        check_version: str cmd_line input
    Output:
        None
    """
    check_version_prefix = "Programming Language :: Python :: "
    classifiers = project_info["info"]["classifiers"]
    compatible_versions = set()
    for element in classifiers:
        if check_version_prefix in element:
            compatible_versions.add(element.split()[-1])

    result_string = "{}".format(project_name) + (" " * (40 - len(project_name)))
    if check_version in compatible_versions:
        result_string += "| " + Fore.GREEN + "Compatible" + Style.RESET_ALL + "    |"
    else:
        result_string += "| " + Fore.RED + "Incompatible" + Style.RESET_ALL + "  |"

    result_string += " {}".format(sorted(compatible_versions))
    print(result_string)


async def process_requirement(requirement, version, session):
    """
    Take individual requirement in requirements.txt
    and determine if it is compatible with the specified version.

    Args:
        requirement: str line from requirements.txt
        version: str python version specified via cmdline
        session: aiohttp ClientSession object
    Output:
        None
    """
    strategy = "normal" if "==" in requirement else "wheel"
    (project_name, project_version) = parse_project_and_version(strategy, requirement)
    info = await get_project_info(project_name, project_version, session)
    if info:
        check_compatible(project_name, project_version, info, version)


async def main():
    parser = argparse.ArgumentParser(description="Check requirements.txt for python version compatability.")
    parser.add_argument("path", default=None, help="path to requirements.txt", type=lambda x: path_is_valid(parser, x))
    parser.add_argument("-p", "--pyversion", default=None, required=True, help="check if requirements compatible with this python version i.e. X or X.X")

    args = parser.parse_args()
    requirements_text = args.path.readlines()
    print("\nProject					| Compatibility | Compatible Versions")
    print("=======================================================================================")
    async with ClientSession() as session:
        await asyncio.gather(*(process_requirement(requirement, args.pyversion, session) for requirement in requirements_text))


    args.path.close()


if __name__ == "__main__":
    s = time.perf_counter()
    asyncio.run(main())
    print()
    print(time.perf_counter() - s)

