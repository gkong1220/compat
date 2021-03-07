import argparse
import os
import re
import requests

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


def get_project_info(project_name, project_version):
    """
    Get pypi.org JSON info on project.

    Args:
        project_name: str name of project
    Output:
        info: dict with info
    """
    r = requests.get("https://pypi.org/pypi/{}/{}/json".format(project_name, project_version))
    if r.status_code == 404:
        print(Fore.RED + "{} could not be found".format(project_name))
        return
    return r.json()


def check_compatible(project_name, project_version, project_info, check_version):
    """
    Check if requirement compatible with specific python version.

    Args:
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

    if check_version in compatible_versions:
        print(Fore.GREEN + "{} {} is compatible!".format(project_name, project_version))
    else:
        print(Fore.RED + "{} {} may not be compatible.".format(project_name, project_version))
        print("\tCompatible versions: {}".format(sorted(compatible_versions)))


def main():
    parser = argparse.ArgumentParser(description="Check requirements.txt for python version compatability.")
    parser.add_argument("path", default=None, help="path to requirements.txt", type=lambda x: path_is_valid(parser, x))
    parser.add_argument("-v", "--version", default=None, required=True, help="check if requirements compatible with this python version i.e. X or X.X")

    args = parser.parse_args()
    requirements_text = args.path.readlines()

    for requirement in requirements_text:
        strategy = "normal" if "==" in requirement else "wheel"
        (project_name, project_version) = parse_project_and_version(strategy, requirement)
        info = get_project_info(project_name, project_version)
        if info:
            check_compatible(project_name, project_version, info, args.version)


    args.path.close()


if __name__ == "__main__":
    main()

