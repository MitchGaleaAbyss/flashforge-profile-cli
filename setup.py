#!/usr/bin/env python3
from distutils.core import setup

setup(
    name = "flashforge-profile-cli",
    version = "0.0.1",
    url = "https://github.com/MitchGaleaAbyss/flashforge-profile-cli",
    description = "A command-line interface to for flashforge profile management",
    author = "Mitchell Galea",
    author_email = "m.galea@abysssollutions.com.au",
    scripts=["flashforge-profile-cli"],
    packages=["flashforge_profile_cli"],
)