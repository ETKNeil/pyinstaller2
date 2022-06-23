#-----------------------------------------------------------------------------
# Copyright (c) 2022, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError
import os
import hashlib


def normalize_icon_type(icon_path, allowed_types, convert_type, workpath)  :
    """
    Returns a valid icon path or raises an Exception on error.
    Ensures that the icon exists, and, if necessary, attempts to convert it to correct OS-specific format using Pillow.

    Takes:
    icon_path - the icon given by the user
    allowed_types - a tuple of icon formats that should be allowed through
        EX: ("ico", "exe")
    convert_type - the type to attempt conversion too if necessary
        EX: "icns"
    workpath - the temp directory to save any newly generated image files
    """

    # explicitly error if file not found
    if not os.path.exists(icon_path):
        raise FileNotFoundError("Icon input file {} not found".format(icon_path))

    _, extension = os.path.splitext(icon_path)
    extension = extension[1:]  # get rid of the "." in ".whatever"

    # if the file is already in the right format, pass it back unchanged
    if extension in allowed_types:
        return icon_path

    # The icon type is wrong! Let's try and import PIL
    try:
        from PIL import Image as PILImage
        import PIL

    except ImportError:
        raise ValueError(
            "Received icon image '{icon_path}' which exists but is not in the correct format. On this platform, "
            "only {allowed_types} images may be used as icons. If Pillow is installed, automatic conversion will "
            "be attempted. Please install Pillow or convert your '{extension}' file to one of {allowed_types} "
            "and try again."
        )

    # Let's try to use PIL to convert the icon file type
    try:
        _generated_name = "generated-{}.{}".format(hashlib.sha256(icon_path.encode()).hexdigest(),convert_type)
        generated_icon = os.path.join(workpath, _generated_name)
        with PILImage.open(icon_path) as im:
            im.save(generated_icon)
        icon_path = generated_icon
    except PIL.UnidentifiedImageError:
        raise ValueError(
            "Something went wrong converting icon image '{icon_path}' to '.{convert_type}' with Pillow, "
            "perhaps the image format is unsupported. Try again with a different file or use a file that can "
            "be used without conversion on this platform: {allowed_types}"
        )

    return icon_path
