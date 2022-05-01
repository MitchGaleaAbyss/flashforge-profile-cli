#!/usr/bin/env python3

""" 
@flashforge_profile.py

Parses, modifies and saves flashforge profile configs
"""

import os

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple


class InvalidParameter(Exception):
    """Raised when no parameters are found"""

    pass


class InvalidProfilePath(Exception):
    """Raised when the profile path is invalid"""

    pass


class InvalidProfile(Exception):
    """Raised when profile is invalid"""

    pass


@dataclass
class FlashforgeProfile:
    """Stores a flashforge profile and allows for modification of parameters"""

    """ machine id of profile as it is only used for comparison """
    machine_id: str

    """ nozzel diameter of profile, uses string as it is only used for comparison """
    nozzle_diameter: str

    """ name of profile """
    name: str

    """ file name of profile """
    file_name: str

    """ general profile parameters """
    general_params: dict

    """ custom profile parameters """
    custom_params: dict

    def get_param(self, param_name: str) -> str:
        """ Gets a parameter

        Args:
            param_name (str): the name of the parameter to set

        Returns:
            str: param to return
        """

        try:
            return self.general_params[param_name]
        except KeyError:
            pass
        try:
            return self.custom_params[param_name]
        except KeyError:
            raise InvalidParameter

    def set_param(self, param_name: str, param: str) -> None:
        """Sets a parameter

        Args:
            param_name (str): the name of the parameter to set
            param (str): the value of the parameter
        """

        if param_name in self.general_params:
            self.general_params[param_name] = param
            return
        if param_name in self.custom_params:
            self.custom_params[param_name] = param
            return
        raise InvalidParameter

    def export(self, path: str, use_file_name: bool = True) -> None:
        """Exports the profile to the specified path

        Args:
            path (str): path to export to
            use_file_name (bool): will append file_name assuming that path is directory
        """
        if use_file_name:
            path = os.path.join(path, self.file_name)

        with open(path, "w") as file:
            file.write("[General]\n")

            for general_param in self.general_params:
                line = f"{general_param}={self.general_params[general_param]}\n"
                file.write(line)

            file.write("\n")
            file.write("[Custom]\n")

            for custom_param in self.custom_params:
                line = f"{custom_param}={self.custom_params[custom_param]}\n"
                file.write(line)


def parse_profile_path(path: str) -> Tuple[str, str, str, str]:
    """parses the path to output machine_id, nozzle diamater, name and file_name

    Args:
        path (str): path of profile

    Raises:
        InvalidProfilePath: when the path is invalid

    Returns:
        Tuple[str, str, str, str]: returns machine_id, nozzle diamater, name and file_name
    """
    file_name = Path(path).name

    try:
        machine_id, nozzle_diameter, name = file_name.split("_", 2)
    except ValueError:
        raise InvalidProfilePath

    name = Path(name).stem
    return (machine_id, nozzle_diameter, name, file_name)


def parse_profile(path: str) -> FlashforgeProfile:
    """Parses a profile from a path

    Args:
        path (str): path of flashforge profile

    Returns:
        FlashforgeProfile: outputted FlashforgeProfile object
    """

    machine_id, nozzle_diameter, name, file_name = parse_profile_path(path)

    general_params = {}
    custom_params = {}

    param_type = None

    with open(path, "r") as file:

        for line in file:

            line = line.strip()
            if not line:
                continue
            if "[General]" in line:
                param_type = "General"
                continue
            if "[Custom]" in line:
                param_type = "Custom"
                continue

            try:
                param_name, param = line.split("=", 1)
            except ValueError:
                print(line, line.split("=", 1))
                raise ValueError

            if not param_type:
                raise InvalidProfile

            if param_type == "General":
                general_params[param_name] = param

            if param_type == "Custom":
                custom_params[param_name] = param

    return FlashforgeProfile(
        machine_id=machine_id,
        nozzle_diameter=nozzle_diameter,
        name=name,
        file_name=file_name,
        general_params=general_params,
        custom_params=custom_params,
    )


def main():

    profile = parse_profile("profiles/22_0.4_abs-1.8-light.cfg")

    print(profile.machine_id)
    print(profile.nozzle_diameter)
    print(profile.name)
    print(profile.file_name)

    profile.export(".")

    return 0


if __name__ == "__main__":
    main()
