# -----------------------------------------------------------------------------
# Copyright (c) 2005-2022, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
# -----------------------------------------------------------------------------

import argparse
import sys

import pkg_resources
import pytest

from PyInstaller import compat


def paths_to_test(include_only=None):
    """
    If ``include_only`` is falsey, this functions returns paths from all entry points. Otherwise, this parameter
    must be a string or sequence of strings. In this case, this function will return *only* paths from entry points
    whose ``module_name`` begins with the provided string(s).
    """
    # Convert a string to a list.
    if isinstance(include_only, compat.string_types):
        include_only = [include_only]

    # Walk through all entry points.
    test_path_list = []
    for entry_point in pkg_resources.iter_entry_points("pyinstaller40", "tests"):
        # Implement ``include_only``.
        if (
            not include_only  # If falsey, include everything,
            # Otherwise, include only the specified modules.
            or any(entry_point.module_name.startswith(name) for name in include_only)
        ):
            test_path_list += list(entry_point.load()())
    return test_path_list


# Run pytest on all tests registered by the PyInstaller setuptools testing entry point. If provided,
# the ``include_only`` argument is passed to ``path_to_test``.
def run_pytest(*args, **kwargs):
    paths = paths_to_test(include_only=kwargs.pop("include_only", None))
    # Return an error code if no tests were discovered.
    if not paths:
        print("Error: no tests discovered.", sys.stderr)
        # This indicates no tests were discovered; see
        # https://docs.pytest.org/en/latest/usage.html#possible-exit-codes.
        return 5
    else:
        # See https://docs.pytest.org/en/latest/usage.html#calling-pytest-from-python-code.
        # Omit ``args[0]``, which is the name of this script.
        paths.append(args[1:])
        print("pytest " + " ".join(paths))
        return pytest.main(paths, **kwargs)


if __name__ == "__main__":
    # Look only for the ``--include_only`` argument.
    parser = argparse.ArgumentParser(description='Run PyInstaller packaging tests.')
    parser.add_argument(
        "--include_only",
        action="append",
        help="Only run tests from the specified package.",
    )
    args, unknown = parser.parse_known_args(sys.argv)
    # Convert the parsed args into a dict using ``vars(args)``.
    sys.exit(run_pytest(*unknown, **vars(args)))
