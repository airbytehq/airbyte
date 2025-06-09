# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


import pytest
from source_google_drive.utils import get_folder_id


@pytest.mark.parametrize(
    "input, output, raises",
    [
        ("https://drive.google.com/drive/folders/1q2w3e4r5t6y7u8i9o0p", "1q2w3e4r5t6y7u8i9o0p", False),
        ("https://drive.google.com/drive/folders/1q2w3e4r5t6y7u8i9o0p/", "1q2w3e4r5t6y7u8i9o0p", False),
        ("https://drive.google.com/drive/folders/1q2w3e4r5t6y7u8i9o0p?usp=link_sharing", "1q2w3e4r5t6y7u8i9o0p", False),
        ("https://drive.google.com/drive/u/0/folders/1q2w3e4r5t6y7u8i9o0p/", "1q2w3e4r5t6y7u8i9o0p", False),
        ("https://drive.google.com/drive/u/0/folders/1q2w3e4r5t6y7u8i9o0p?usp=link_sharing", "1q2w3e4r5t6y7u8i9o0p", False),
        ("https://drive.google.com/drive/u/0/folders/1q2w3e4r5t6y7u8i9o0p#abc", "1q2w3e4r5t6y7u8i9o0p", False),
        ("https://docs.google.com/document/d/fsgfjdsh", None, True),
        ("https://drive.google.com/drive/my-drive", "root", False),
        ("http://drive.google.com/drive/u/0/folders/1q2w3e4r5t6y7u8i9o0p/", None, True),
        ("https://drive.google.com/", None, True),
    ],
)
def test_get_folder_id(input, output, raises):
    if raises:
        with pytest.raises(ValueError):
            get_folder_id(input)
    else:
        assert get_folder_id(input) == output
