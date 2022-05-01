#!/usr/bin/env python3

""" 
@flashforge_profile_cli.py

Command Line Interface to copy, modify and update flashforge profiles
"""

import argparse
import os
import sys

from typing import List

from flashforge_profile_cli.flashforge_profile import (
    FlashforgeProfile,
    InvalidProfile,
    InvalidParameter,
    InvalidProfilePath,
    parse_profile,
)


def main():
    def get_args() -> argparse.Namespace:
        """get command-line arguments

        Returns:
            argparse.Namespace: object with arguments
        """

        update_profiles_examples = """
update-profiles examples:
    - Run flashforge-profile-cli to update the profiles from the respositores
        flashforge-profile-cli update-profiles
    - Run flashforge-profile-cli to update the profiles from the respositores containing 1.8
        flashforge-profile-cli update-profiles \\
        --search-regex "1.8" """
        update_repo_examples = """
update-repo examples:
    - Run flashforge-profile-cli to update the repository from the profiles 
        flashforge-profile-cli update-repo
    - Run flashforge-profile-cli to update the repository from the profiles with 0.4mm nozzel
        flashforge-profile-cli update-repo\\
        --nozzle 0.4"""
        set_params_examples = """
set-param examples:
    - Run flashforge-profile-cli to set a param for all profiles to match the value in the input profile
        flashforge-profile-cli set-param \\
        --param "extruderTemp0" \\
        --input-profile-name "abs-1.8-full" 
    - Run flashforge-profile-cli to set a param for all machine id 22 profiles to match the value in the input profile
        flashforge-profile-cli set-param \\
        --param "extruderTemp0" \\
        --input-profile-name "abs-1.8-full" \\
        --machine-id 22 """

        example_text = "\n".join(
            [update_profiles_examples, update_repo_examples, set_params_examples]
        )
        parent_parser = argparse.ArgumentParser(add_help=False)
        parent_parser.add_argument(
            "--repo-path",
            "-r",
            type=str,
            default="~/src/abyss/abyss-flashforge/profiles/",
            help="path to repository profile directory",
        )
        parent_parser.add_argument(
            "--flashforge-path",
            "-f",
            type=str,
            default="~/.FlashPrint5/slice_profile/",
            help="path to flashforge profile directory",
        )
        parent_parser.add_argument(
            "--machine-id",
            "-m",
            type=str,
            default=None,
            help="only apply process to profiles with this machine id number",
        )
        parent_parser.add_argument(
            "--nozzle",
            "-n",
            type=str,
            default=None,
            help="only apply process to profiles with this nozzel diamater",
        )
        parent_parser.add_argument(
            "--search-regex",
            type=str,
            default=None,
            help="only apply process to profiles containing input string",
        )
        parser = argparse.ArgumentParser(
            description="Command Line Interface for flashforge profiles",
            epilog=example_text,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        subparsers = parser.add_subparsers(dest="command")
        update_profiles_parser = subparsers.add_parser(
            "update-profiles",
            help="updates the profiles used by flashprint from the respository",
            epilog=update_profiles_examples,
            parents=[parent_parser],
            formatter_class=argparse.RawTextHelpFormatter,
        )
        update_repo_parser = subparsers.add_parser(
            "update-repo",
            help="updates the profiles in the repository from the flashforge directory",
            epilog=update_repo_examples,
            parents=[parent_parser],
            formatter_class=argparse.RawTextHelpFormatter,
        )
        set_param_parser = subparsers.add_parser(
            "set-param",
            help="sets a param for all or selected profiles to match an input profile value",
            epilog=set_params_examples,
            parents=[parent_parser],
            formatter_class=argparse.RawTextHelpFormatter,
        )
        set_param_parser.add_argument(
            "--param",
            "-p",
            type=str,
            required=True,
            help="param name to be set",
        )
        set_param_parser.add_argument(
            "--input-profile-name",
            "-i",
            type=str,
            required=True,
            help="name of profile used to get the param value",
        )
        set_param_parser.add_argument(
            "--update-repo",
            "-u",
            action="store_true", 
            help="after setting params, update the repo"
        )
        return parser.parse_args()

    def sanitise_input(args):
        pass

    def get_profiles(
        path: str, machine_id: str, nozzle_diameter: str, search_regex: str
    ) -> List[FlashforgeProfile]:
        """gets a list of flashforge profiles from path and filtering

        Args:
            path (str): path of profile directory
            machine_id (str): machine id for filtering
            nozzle_diameter (str): nozzle diameter for filtering
            search_regex (str): search_regex for filtering

        Returns:
            List[FlashforgeProfile]: list of filtered flashforge profiles
        """

        profiles: List[FlashforgeProfile] = []

        for file in os.listdir(path):

            file_path = os.path.join(path, file)

            if not os.path.isfile(file_path):
                continue

            try:
                profiles.append(parse_profile(file_path))
            except (InvalidProfile, InvalidProfilePath):
                print(f"Invalid profile {file_path}, skipping")
                continue

        if machine_id:
            profiles = [
                profile for profile in profiles if profile.machine_id == machine_id
            ]

        if nozzle_diameter:
            profiles = [
                profile
                for profile in profiles
                if profile.nozzle_diameter == nozzle_diameter
            ]

        if search_regex:
            profiles = [
                profile for profile in profiles if search_regex in profile.file_name
            ]

        return profiles

    def update_profiles(args: argparse.Namespace):
        """updates the flashforge profiles from the repo

        Args:
            args (argparse.Namespace): commandline args
        """

        profiles = get_profiles(
            os.path.expanduser(args.repo_path),
            args.machine_id,
            args.nozzle,
            args.search_regex,
        )

        if not profiles:
            print("No valid profiles to update", file=sys.stderr)
            sys.exit(1)

        for profile in profiles:
            profile.export(os.path.expanduser(args.flashforge_path))

    def update_repo(args: argparse.Namespace):
        """updates the repo profiles from the flashforge profiles

        Args:
            args (argparse.Namespace): commandline args
        """

        profiles = get_profiles(
            os.path.expanduser(args.flashforge_path),
            args.machine_id,
            args.nozzle,
            args.search_regex,
        )

        if not profiles:
            print("No valid profiles to update", file=sys.stderr)
            sys.exit(1)

        for profile in profiles:
            profile.export(os.path.expanduser(args.repo_path))

    def set_param(args: argparse.Namespace):
        """sets a param from an input profile for selected or all profiles

        Args:
            args (argparse.Namespace): commandline args
        """

        profiles = get_profiles(
            os.path.expanduser(args.flashforge_path),
            args.machine_id,
            args.nozzle,
            args.search_regex,
        )

        if not profiles:
            print("No valid profiles found", file=sys.stderr)
            sys.exit(1)

        target_profile = None
        # gets the target profile
        for profile in profiles:
            if args.input_profile_name in profile.file_name:
                target_profile = profile
                break

        if not target_profile:
            print("input profile not found after filtering", file=sys.stderr)
            sys.exit(1)

        try:
            param_value = target_profile.get_param(args.param)
        except InvalidParameter:
            print(
                f"parameter not found in input profile, {target_profile.file_name}",
                file=sys.stderr,
            )
            sys.exit(1)

        for profile in profiles:
            try:
                profile.set_param(args.param, param_value)
                profile.export(os.path.expanduser(args.flashforge_path))
                if args.update_repo:
                    profile.export(os.path.expanduser(args.repo_path))
            except InvalidParameter:
                print(
                    f"parameter not found in profile, {profile.file_name}",
                    file=sys.stderr,
                )

    args = get_args()

    # sanitise_input(args)

    if args.command == "update-profiles":
        update_profiles(args)
    elif args.command == "update-repo":
        update_repo(args)
    elif args.command == "set-param":
        set_param(args)