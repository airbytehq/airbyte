#-----------------------------------------------------------------------------
# Copyright (c) 2022-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------

from typing import Tuple

import os
import hashlib


def normalize_icon_type(icon_path: str, allowed_types: Tuple[str], convert_type: str, workpath: str) -> str:
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
        raise FileNotFoundError(f"Icon input file {icon_path} not found")

    _, extension = os.path.splitext(icon_path)
    extension = extension[1:]  # get rid of the "." in ".whatever"

    # if the file is already in the right format, pass it back unchanged
    if extension in allowed_types:
        # Check both the suffix and the header of the file to guard against the user confusing image types.
        signatures = hex_signatures[extension]
        with open(icon_path, "rb") as f:
            header = f.read(max(len(s) for s in signatures))
        if any(list(header)[:len(s)] == s for s in signatures):
            return icon_path

    # The icon type is wrong! Let's try and import PIL
    try:
        from PIL import Image as PILImage
        import PIL

    except ImportError:
        raise ValueError(
            f"Received icon image '{icon_path}' which exists but is not in the correct format. On this platform, "
            f"only {allowed_types} images may be used as icons. If Pillow is installed, automatic conversion will "
            f"be attempted. Please install Pillow or convert your '{extension}' file to one of {allowed_types} "
            f"and try again."
        )

    # Let's try to use PIL to convert the icon file type
    try:
        _generated_name = f"generated-{hashlib.sha256(icon_path.encode()).hexdigest()}.{convert_type}"
        generated_icon = os.path.join(workpath, _generated_name)
        with PILImage.open(icon_path) as im:
            # If an image uses a custom palette + transparency, convert it to RGBA for a better alpha mask depth.
            if im.mode == "P" and im.info.get("transparency", None) is not None:
                # The bit depth of the alpha channel will be higher, and the images will look better when eventually
                # scaled to multiple sizes (16,24,32,..) for the ICO format for example.
                im = im.convert("RGBA")
            im.save(generated_icon)
        icon_path = generated_icon
    except PIL.UnidentifiedImageError:
        raise ValueError(
            f"Something went wrong converting icon image '{icon_path}' to '.{convert_type}' with Pillow, "
            f"perhaps the image format is unsupported. Try again with a different file or use a file that can "
            f"be used without conversion on this platform: {allowed_types}"
        )

    return icon_path


# Possible initial bytes of icon types PyInstaller needs to be able to recognise.
# Taken from: https://en.wikipedia.org/wiki/List_of_file_signatures
hex_signatures = {
    "png": [[0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]],
    "exe": [[0x4D, 0x5A], [0x5A, 0x4D]],
    "ico": [[0x00, 0x00, 0x01, 0x00]],
    "icns": [[0x69, 0x63, 0x6e, 0x73]],
}
