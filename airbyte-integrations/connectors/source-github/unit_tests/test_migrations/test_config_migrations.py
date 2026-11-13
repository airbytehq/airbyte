#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json

from unit_tests.utils import make_source


def write_config(tmp_path, config):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config, indent=2) + "\n")
    return config_path


def test_migrate_repository_to_repositories(tmp_path, capsys):
    """Legacy `repository` (space-separated string) is migrated to `repositories` (sorted
    list) by the manifest's `config_migrations`, the file is rewritten, and a CONNECTOR_CONFIG
    control message is emitted."""
    config = {"repository": "a/b c/d", "credentials": {"access_token": "t"}}
    config_path = write_config(tmp_path, config)

    source = make_source(config=config, config_path=str(config_path))

    assert source._config["repositories"] == ["a/b", "c/d"]
    # The file was rewritten with the new key, keeping the legacy one so a downgrade works.
    rewritten = json.loads(config_path.read_text())
    assert rewritten["repositories"] == ["a/b", "c/d"]
    assert rewritten["repository"] == "a/b c/d"
    assert '"type":"CONTROL"' in capsys.readouterr().out


def test_migrate_branch_to_branches(tmp_path, capsys):
    config = {"branch": "main feature", "repositories": ["a/b"], "credentials": {"access_token": "t"}}
    config_path = write_config(tmp_path, config)

    source = make_source(config=config, config_path=str(config_path))

    assert source._config["branches"] == ["feature", "main"]
    rewritten = json.loads(config_path.read_text())
    assert rewritten["branches"] == ["feature", "main"]
    assert rewritten["branch"] == "main feature"
    assert '"type":"CONTROL"' in capsys.readouterr().out


def test_already_migrated_config_is_untouched(tmp_path, capsys):
    config = {"repositories": ["a/b"], "repository": "a/b c/d", "credentials": {"access_token": "t"}}
    config_path = write_config(tmp_path, config)

    source = make_source(config=config, config_path=str(config_path))

    assert source._config["repositories"] == ["a/b"]
    rewritten = json.loads(config_path.read_text())
    assert rewritten["repositories"] == ["a/b"]
    assert "branches" not in rewritten
    assert '"type":"CONTROL"' not in capsys.readouterr().out
