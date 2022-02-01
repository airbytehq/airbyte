#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import json
from pathlib import Path

from source_s3 import SourceS3


def test_transform_backslash_t_to_tab(tmp_path: Path) -> None:
    config_file = tmp_path / "config.json"
    with open(config_file, "w") as fp:
        json.dump({"format": {"delimiter": "\\t"}}, fp)
    source = SourceS3()
    config = source.read_config(str(config_file))
    assert config["format"]["delimiter"] == "\t"
    assert False
