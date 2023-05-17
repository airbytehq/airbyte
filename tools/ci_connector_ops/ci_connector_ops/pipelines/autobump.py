#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import re
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple

import git
import openai
import yaml
from ci_connector_ops.utils import Connector


class SemverComponent(Enum):
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"


CONVENTIONAL_COMMIT_PREFIX_TO_BUMP_TYPE = {
    "feat": SemverComponent.MINOR,
    "fix": SemverComponent.PATCH,
    "chore": SemverComponent.PATCH,
    "docs": SemverComponent.PATCH,
    "style": SemverComponent.PATCH,
    "refactor": SemverComponent.PATCH,
    "perf": SemverComponent.PATCH,
    "test": SemverComponent.PATCH,
    "build": SemverComponent.PATCH,
    "ci": SemverComponent.PATCH,
    "revert": SemverComponent.PATCH,
    "release": SemverComponent.MAJOR,
    "major": SemverComponent.MAJOR,
    "minor": SemverComponent.MINOR,
    "patch": SemverComponent.PATCH,
    "breaking": SemverComponent.MAJOR,
}


def generate_changelog_entry_with_ai(connectors: List[Connector], commits: List[git.Commit], git_diff: str, open_ai_api_key: str) -> str:
    """Generate a changelog entry with the OpenAI API."""

    openai.api_key = open_ai_api_key

    connector_names = ",".join([connector.technical_name for connector in connectors])
    commits = ",".join([commit.message for commit in commits])
    prompt = f"Generate a short message, with actual sense of the changes made, but feel free to ignore the less import changes, for the following connectors {connector_names} with the following commits:\n\n{commits}\n\n---\n\n and the following git diff:\n\n{git_diff}\n\n---\n\nThe git diff should have more importance over commit messages if commit messages are very short."
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
    return response.choices[0].message.content.replace("\n", " ")


def guess_semver_version_with_ai(git_diff, open_ai_api_key: str) -> Tuple[Optional[SemverComponent], str]:
    """Generate a semver version bump with the OpenAI API."""
    prompt = f"Help me define if the version bump should be a patch, minor or major according to the following git diff:\n\n{git_diff}\n\n---\n\nPlease first tell me the type of semver version bump on the first line, with only a single word and then add a newline and tell me why you made this decision."
    openai.api_key = open_ai_api_key
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}], temperature=0.2)
    version_bump_type, reason = response.choices[0].message.content.split("\n\n")
    if "major" in version_bump_type.lower():
        version_bump_type = SemverComponent.MAJOR
    elif "minor" in version_bump_type.lower():
        version_bump_type = SemverComponent.MINOR
    elif "patch" in version_bump_type.lower():
        version_bump_type = SemverComponent.PATCH
    else:
        version_bump_type = None
    return version_bump_type, reason


def get_connector_version_part(connector: Connector) -> Tuple[int, int, int]:
    """Get a part of the version of a connector from its metadata.yaml file."""
    version_parts = re.findall(r"\d+", connector.version)
    return [int(part) for part in version_parts]


def bump_connector_version_from_component(connector: Connector, component: SemverComponent) -> Tuple[int, int, int]:
    """Bump a part of the version of a connector."""
    version_parts = get_connector_version_part(connector)
    return bump_for_component(version_parts, component)


def version_parts_to_string(version_parts: Tuple[int, int, int]) -> str:
    bumped_version = ".".join([str(part) for part in version_parts])
    return bumped_version


def bump_for_component(version_parts: Tuple[int, int, int], component: str) -> Tuple[int, int, int]:
    """Bump a part of the version of a connector."""
    major, minor, patch = version_parts
    if component == SemverComponent.MAJOR:
        major += 1
        minor = 0
        patch = 0
    elif component == SemverComponent.MINOR:
        minor += 1
        patch = 0
    elif component == SemverComponent.PATCH:
        patch += 1
    return major, minor, patch


def get_new_version_from_conventional_commit_messages(commits: List[git.Commit], connector: Connector) -> Optional[str]:
    original_version_parts = get_connector_version_part(connector)
    major, minor, patch = original_version_parts

    bumped_minor = False
    bumped_patch = False

    for commit in commits:
        commit_prefix = commit.message.split(":")[0]
        component = CONVENTIONAL_COMMIT_PREFIX_TO_BUMP_TYPE.get(commit_prefix.lower())
        if component == SemverComponent.MAJOR:
            major += 1
            minor = 0
            patch = 0
            break
        elif component == SemverComponent.MINOR and not bumped_minor:
            minor += 1
            patch = 0
            bumped_minor = True
        elif component == SemverComponent.PATCH and not bumped_patch and not bumped_minor:
            patch += 1
            bumped_patch = True

    new_version_parts = major, minor, patch
    # If the new version is the same as the original one, we can't infer the new version.
    if original_version_parts == new_version_parts:
        return None
    return new_version_parts


def get_connector_new_version(
    connector: Connector, use_conventional_commit_messages: bool, ai_version_bump_component: SemverComponent, git_commits
) -> Optional[str]:
    ai_determined_version = bump_connector_version_from_component(connector, ai_version_bump_component)
    conventional_commit_determined_version = get_new_version_from_conventional_commit_messages(git_commits, connector)
    if conventional_commit_determined_version is not None and use_conventional_commit_messages:
        return version_parts_to_string(conventional_commit_determined_version)
    if ai_determined_version is not None:
        return version_parts_to_string(ai_determined_version)
    return None


def bump_version_in_files(connector: Connector, new_version: str) -> List[Path]:
    """Bump the version of a connector in its Dockerfile and metadata.yaml file."""
    connector_docker_file = connector.code_directory / "Dockerfile"
    connector_metadata_file = connector.code_directory / "metadata.yaml"

    new_docker_file_content = ""
    for line in connector_docker_file.read_text().splitlines():
        if "io.airbyte.version" in line:
            line = line.replace(connector.version, new_version)
        new_docker_file_content += line + "\n"
    connector_docker_file.write_text(new_docker_file_content)

    metadata_content = yaml.safe_load(connector_metadata_file.read_text())
    metadata_content["data"]["dockerImageTag"] = new_version
    connector_metadata_file.write_text(yaml.dump(metadata_content))
    return [connector_docker_file, connector_metadata_file]


def update_changelog_entry_with_ai(connector: Connector, new_version: str, changelog: str, openai_api_key: str) -> Path:
    """Update the changelog file with the new version."""
    openai.api_key = openai_api_key
    connector_documentation = connector.documentation_file_path.read_text()
    prompt = f"Find the changelog table in the following markdown document and add a new entry for the version {new_version}, with today's date in iso format and the subject {changelog}:\n{connector_documentation} \n\n Please return the full document with your changes."
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}], temperature=0.2)
    new_content = response.choices[0].message.content
    connector.documentation_file_path.write_text(new_content)
    return connector.documentation_file_path


def commit_modified_files(modified_files: List[Path], commit_message: str, push_to_origin: bool = False):
    repo = git.Repo()
    repo.index.add(modified_files)
    repo.index.commit(commit_message, skip_hooks=True)
    if push_to_origin:
        repo.git.push("--set-upstream", repo.remote().name, repo.active_branch.name)


def do_it(connector, use_conventional_commits, ai_version_bump_component, git_commits, changelog, openai_api_key):
    new_version = get_connector_new_version(connector, use_conventional_commits, ai_version_bump_component, git_commits)
    if new_version is None:
        print(f"Could not determine a new version for connector {connector.technical_name}")
        return
    bumped_files = bump_version_in_files(connector, new_version)
    changelog_file = update_changelog_entry_with_ai(connector, new_version, changelog, openai_api_key)
    print(f"Successfully bumped version of connector {connector.technical_name} to {new_version}")
    print(f"Files bumped: {bumped_files}")
    print(f"Changelog file updated: {changelog_file}")
    modified_files = bumped_files + [changelog_file]
    commit_message = f"[skip ci] 🤖 Bump version of connector {connector.technical_name} to {new_version}"
    commit_modified_files(modified_files, commit_message, push_to_origin=True)
