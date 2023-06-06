#!/usr/bin/env python3

import subprocess

import setuptools

try:
    ret = subprocess.check_output(
        "git describe --tags --abbrev=0",
        shell=True,
    )
    version = ret.decode("utf-8").strip()
except:
    version = "main"

with open("README.md", "r", encoding="utf-8") as readme:
    long_description = readme.read()


setuptools.setup(
    name="robotpy-commands-v2",
    version=version,
    author="RobotPy Development Team",
    author_email="robotpy@googlegroups.com",
    description="WPILib command framework v2",
    url="https://github.com/robotpy/robotpy-commands-v2",
    packages=["commands2"],
    install_requires=["wpilib~=2023.4.3"],
    license="BSD-3-Clause",
    python_requires=">=3.8",
    include_package_data=True,
)
