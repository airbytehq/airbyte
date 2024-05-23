#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import re
from typing import TYPE_CHECKING

import dagger
import git
import requests
import toml
from connector_ops.utils import ConnectorLanguage  # type: ignore
from jinja2 import Environment, PackageLoader, select_autoescape
from pipelines.airbyte_ci.connectors.bump_version.pipeline import AddChangelogEntry, SetConnectorVersion, get_bumped_version
from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.context import ConnectorContext, PipelineContext
from pipelines.airbyte_ci.connectors.reports import ConnectorReport, Report
from pipelines.consts import LOCAL_BUILD_PLATFORM
from pipelines.dagger.actions.python.common import with_python_connector_installed
from pipelines.helpers.execution.run_steps import STEP_TREE, StepToRun, run_steps
from pipelines.models.steps import Step, StepResult, StepStatus

if TYPE_CHECKING:
    from typing import Iterable, List, Optional

    from anyio import Semaphore

PACKAGE_NAME_PATTERN = r"^([a-zA-Z0-9_.\-]+)(?:\[(.*?)\])?([=~><!]=?[a-zA-Z0-9\.]+)?$"


class CheckIsMigrationCandidate(Step):
    """Check if the connector is a candidate for migration to poetry.
    Candidate conditions:
    - The connector is a Python connector.
    - The connector has a setup.py file.
    - The connector has a base image defined in the metadata.
    - The connector has not been migrated to poetry yet.
    """

    context: ConnectorContext

    title = "Check if the connector is a candidate for migration to poetry."
    airbyte_repo = git.Repo(search_parent_directories=True)

    async def _run(self) -> StepResult:
        connector_dir_entries = await (await self.context.get_connector_dir()).entries()
        if self.context.connector.language not in [ConnectorLanguage.PYTHON, ConnectorLanguage.LOW_CODE]:
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stderr="The connector is not a Python connector.",
            )
        if "poetry.lock" in connector_dir_entries and "pyproject.toml" in connector_dir_entries:
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stderr="The connector has already been migrated to poetry.",
            )
        if "setup.py" not in connector_dir_entries:
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stderr="The connector can't be migrated to poetry because it does not have a setup.py file.",
            )
        if not self.context.connector.metadata.get("connectorBuildOptions", {}).get("baseImage"):
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stderr="The connector can't be migrated to poetry because it does not have a base image defined in the metadata.",
            )

        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
        )


class PoetryInit(Step):
    context: ConnectorContext

    title = "Generate pyproject.toml and poetry.lock"
    python_version = "^3.9,<3.12"
    build_system = {
        "requires": ["poetry-core>=1.0.0"],
        "build-backend": "poetry.core.masonry.api",
    }

    def __init__(self, context: PipelineContext, new_version: str | None) -> None:
        super().__init__(context)
        self.new_version = new_version

    @property
    def package_name(self) -> str:
        return self.context.connector.technical_name.replace("-", "_")

    def get_package_info(self, package_info: str) -> dict:
        package_info_dict = {}
        for line in package_info.splitlines():
            # Ignoring locally installed packages
            if ":" not in line:
                continue
            key, value = line.split(": ")
            package_info_dict[key] = value
        return {
            "version": self.context.connector.version,
            "name": package_info_dict["Name"],
            "description": package_info_dict["Summary"],
            "authors": [package_info_dict["Author"] + " <" + package_info_dict["Author-email"] + ">"],
            "license": self.context.connector.metadata["license"],
            "readme": "README.md",
            "documentation": self.context.connector.metadata["documentationUrl"],
            "homepage": "https://airbyte.com",
            "repository": "https://github.com/airbytehq/airbyte",
        }

    def to_poetry_dependencies(self, requirements_style_deps: Iterable[str], latest_dependencies_for_hard_pin: dict) -> dict:
        dependencies = {}
        for deps in requirements_style_deps:
            if "," in deps:
                deps = deps.split(",")[0]
            match = re.match(PACKAGE_NAME_PATTERN, deps)
            assert match, f"Failed to parse package name and version from {deps}"
            name = match.group(1)
            extras = match.group(2)
            version = match.group(3)
            if extras:
                extras = extras.split(",")
            if name in latest_dependencies_for_hard_pin:
                version = f"=={latest_dependencies_for_hard_pin[name]}"
            elif "~=" in deps:
                # We prefer caret (^) over tilde (~) for the version range
                # See https://python-poetry.org/docs/dependency-specification/
                version = version.replace("~=", "^")
            elif "==" not in deps:
                # The package version is not pinned and not installed in the released connector
                # It's because it's a test dependency
                # Poetry requires version to be declared so we should get the latest version from PyPI
                version = f"^{self.get_latest_version_from_pypi(name)}"
            if extras:
                version = {"extras": extras, "version": version}
            dependencies[name] = version
        return dependencies

    def get_latest_version_from_pypi(self, package_name: str) -> str:
        url = f"https://pypi.org/pypi/{package_name}/json"

        # Send GET request to the PyPI API
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for any HTTP error status

        # Parse the JSON response
        data = response.json()

        # Extract the latest version from the response
        latest_version = data["info"]["version"]

        return latest_version

    async def get_dependencies(self, connector_container: dagger.Container, groups: Optional[List[str]] = None) -> set[str]:
        package = "." if not groups else f'.[{",".join(groups)}]'
        connector_container = await connector_container.with_exec(["pip", "install", package])

        pip_install_dry_run_output = await connector_container.with_exec(["pip", "install", package, "--dry-run"]).stdout()

        non_transitive_deps = []
        for line in pip_install_dry_run_output.splitlines():
            if "Requirement already satisfied" in line and "->" not in line:
                non_transitive_deps.append(line.replace("Requirement already satisfied: ", "").split(" ")[0].replace("_", "-"))
        return set(non_transitive_deps)

    async def _run(self) -> StepResult:
        base_image_name = self.context.connector.metadata["connectorBuildOptions"]["baseImage"]
        base_container = self.dagger_client.container(platform=LOCAL_BUILD_PLATFORM).from_(base_image_name)
        connector_container = await with_python_connector_installed(
            self.context,
            base_container,
            str(self.context.connector.code_directory),
        )
        with_egg_info = await connector_container.with_exec(["python", "setup.py", "egg_info"])

        egg_info_dir = with_egg_info.directory(f"{self.package_name}.egg-info")
        egg_info_files = {file_path: await egg_info_dir.file(file_path).contents() for file_path in await egg_info_dir.entries()}

        package_info = self.get_package_info(egg_info_files["PKG-INFO"])
        dependencies = await self.get_dependencies(connector_container)
        dev_dependencies = await self.get_dependencies(connector_container, groups=["dev", "tests"]) - dependencies
        latest_pip_freeze = (
            await self.context.dagger_client.container(platform=LOCAL_BUILD_PLATFORM)
            .from_(f"{self.context.connector.metadata['dockerRepository']}:latest")
            .with_exec(["pip", "freeze"], skip_entrypoint=True)
            .stdout()
        )
        latest_dependencies = {
            name_version.split("==")[0]: name_version.split("==")[1]
            for name_version in latest_pip_freeze.splitlines()
            if "==" in name_version
        }
        poetry_dependencies = self.to_poetry_dependencies(dependencies, latest_dependencies)
        poetry_dev_dependencies = self.to_poetry_dependencies(dev_dependencies, latest_dependencies)
        scripts = {self.context.connector.technical_name: f"{self.package_name}.run:run"}

        pyproject = {
            "build-system": self.build_system,
            "tool": {
                "poetry": {
                    **package_info,
                    "packages": [{"include": self.package_name}],
                    "dependencies": {"python": self.python_version, **poetry_dependencies},
                    "group": {"dev": {"dependencies": poetry_dev_dependencies}},
                    "scripts": scripts,
                }
            },
        }
        toml_string = toml.dumps(pyproject)
        try:
            with_poetry_lock = await connector_container.with_new_file("pyproject.toml", contents=toml_string).with_exec(
                ["poetry", "install"]
            )
        except dagger.ExecError as e:
            return StepResult(
                step=self,
                status=StepStatus.FAILURE,
                stderr=str(e),
            )

        dir = with_poetry_lock
        if self.new_version:
            dir = await dir.with_exec(["poetry", "version", self.new_version])

        await dir.file("pyproject.toml").export(f"{self.context.connector.code_directory}/pyproject.toml")
        self.logger.info(f"Generated pyproject.toml for {self.context.connector.technical_name}")
        await dir.file("poetry.lock").export(f"{self.context.connector.code_directory}/poetry.lock")
        self.logger.info(f"Generated poetry.lock for {self.context.connector.technical_name}")
        return StepResult(step=self, status=StepStatus.SUCCESS, output=(dependencies, dev_dependencies))


class DeleteSetUpPy(Step):
    context: ConnectorContext

    title = "Delete setup.py"

    async def _run(self) -> StepResult:
        setup_path = self.context.connector.code_directory / "setup.py"
        original_setup_py = setup_path.read_text()
        setup_path.unlink()
        self.logger.info(f"Removed setup.py for {self.context.connector.technical_name}")
        return StepResult(step=self, status=StepStatus.SUCCESS, output=original_setup_py)


class RestorePoetryState(Step):
    context: ConnectorContext

    title = "Restore original state"

    def __init__(self, context: ConnectorContext) -> None:
        super().__init__(context)
        self.setup_path = context.connector.code_directory / "setup.py"
        self.metadata_path = context.connector.code_directory / "metadata.yaml"
        self.pyproject_path = context.connector.code_directory / "pyproject.toml"
        self.poetry_lock_path = context.connector.code_directory / "poetry.lock"
        self.readme_path = context.connector.code_directory / "README.md"
        self.doc_path = context.connector.documentation_file_path
        self.original_setup_py = self.setup_path.read_text() if self.setup_path.exists() else None
        self.original_metadata = self.metadata_path.read_text()
        self.original_docs = self.doc_path.read_text() if self.doc_path and self.doc_path.exists() else None
        self.original_readme = self.readme_path.read_text()

    async def _run(self) -> StepResult:
        if self.original_setup_py:
            self.setup_path.write_text(self.original_setup_py)
        self.logger.info(f"Restored setup.py for {self.context.connector.technical_name}")
        self.metadata_path.write_text(self.original_metadata)
        self.logger.info(f"Restored metadata.yaml for {self.context.connector.technical_name}")
        if self.doc_path and self.original_docs:
            self.doc_path.write_text(self.original_docs)
        self.logger.info(f"Restored documentation file for {self.context.connector.technical_name}")
        self.readme_path.write_text(self.original_readme)
        self.logger.info(f"Restored README.md for {self.context.connector.technical_name}")
        if self.poetry_lock_path.exists():
            self.poetry_lock_path.unlink()
            self.logger.info(f"Removed poetry.lock for {self.context.connector.technical_name}")
        if self.pyproject_path.exists():
            self.pyproject_path.unlink()
            self.logger.info(f"Removed pyproject.toml for {self.context.connector.technical_name}")

        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
        )


class RegressionTest(Step):
    """Run the regression test for the connector.
    We test that:
    - The original dependencies are installed in the new connector image.
    - The dev dependencies are not installed in the new connector image.
    - The connector spec command successfully.
    """

    context: ConnectorContext

    title = "Run regression test"

    async def _run(
        self, new_connector_container: dagger.Container, original_dependencies: List[str], original_dev_dependencies: List[str]
    ) -> StepResult:
        try:
            await self.check_all_original_deps_are_installed(new_connector_container, original_dependencies, original_dev_dependencies)
        except (AttributeError, AssertionError) as e:
            return StepResult(
                step=self,
                status=StepStatus.FAILURE,
                stderr=f"Failed checking if the original dependencies are installed:\n {str(e)}",
                exc_info=e,
            )

        try:
            await new_connector_container.with_exec(["spec"])
            await new_connector_container.with_mounted_file(
                "pyproject.toml", (await self.context.get_connector_dir(include=["pyproject.toml"])).file("pyproject.toml")
            ).with_exec(["poetry", "run", self.context.connector.technical_name, "spec"], skip_entrypoint=True)
        except dagger.ExecError as e:
            return StepResult(
                step=self,
                status=StepStatus.FAILURE,
                stderr=str(e),
            )
        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
        )

    async def check_all_original_deps_are_installed(
        self, new_connector_container: dagger.Container, original_main_dependencies: List[str], original_dev_dependencies: List[str]
    ) -> None:
        previous_pip_freeze = (
            await self.dagger_client.container(platform=LOCAL_BUILD_PLATFORM)
            .from_(f'{self.context.connector.metadata["dockerRepository"]}:latest')
            .with_exec(["pip", "freeze"], skip_entrypoint=True)
            .stdout()
        ).splitlines()
        current_pip_freeze = (await new_connector_container.with_exec(["pip", "freeze"], skip_entrypoint=True).stdout()).splitlines()
        main_dependencies_names = []
        for dep in original_main_dependencies:
            match = re.match(PACKAGE_NAME_PATTERN, dep)
            if match:
                main_dependencies_names.append(match.group(1))

        dev_dependencies_names = []
        for dep in original_dev_dependencies:
            match = re.match(PACKAGE_NAME_PATTERN, dep)
            if match:
                dev_dependencies_names.append(match.group(1))

        previous_package_name_version_mapping: dict[str, str] = {}
        for dep in previous_pip_freeze:
            if "==" in dep:
                match = re.match(PACKAGE_NAME_PATTERN, dep)
                if match:
                    previous_package_name_version_mapping[match.group(1)] = dep

        current_package_name_version_mapping: dict[str, str] = {}
        for dep in current_pip_freeze:
            if "==" in dep:
                match = re.match(PACKAGE_NAME_PATTERN, dep)
                if match:
                    current_package_name_version_mapping[match.group(1)] = dep

        for main_dep in main_dependencies_names:
            assert main_dep in current_package_name_version_mapping, f"{main_dep} not found in the latest pip freeze"
            assert (
                current_package_name_version_mapping[main_dep] == previous_package_name_version_mapping[main_dep]
            ), f"Poetry installed a different version of {main_dep} than the previous version. Previous: {previous_package_name_version_mapping[main_dep]}, current: {current_package_name_version_mapping[main_dep]}"
        for dev_dep in dev_dependencies_names:
            if dev_dep not in main_dependencies_names:
                assert (
                    dev_dep not in current_package_name_version_mapping
                ), f"A dev dependency ({dev_dep}) was installed by poetry in the container image"


class UpdateReadMe(Step):
    context: ConnectorContext

    title = "Update README.md"

    async def _run(self) -> StepResult:
        readme_path = self.context.connector.code_directory / "README.md"
        jinja_env = Environment(
            loader=PackageLoader("pipelines.airbyte_ci.connectors.migrate_to_poetry"),
            autoescape=select_autoescape(),
            trim_blocks=False,
            lstrip_blocks=True,
        )
        readme_template = jinja_env.get_template("README.md.j2")
        updated_readme = readme_template.render(connector=self.context.connector)
        readme_path.write_text(updated_readme)
        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
        )


async def run_connector_migration_to_poetry_pipeline(
    context: ConnectorContext, semaphore: "Semaphore", changelog: bool, bump: str | None
) -> Report:
    restore_original_state = RestorePoetryState(context)
    if bump:
        new_version = get_bumped_version(context.connector.version, bump)
    else:
        new_version = None
    context.targeted_platforms = [LOCAL_BUILD_PLATFORM]
    steps_to_run: STEP_TREE = []

    steps_to_run.append(
        [StepToRun(id=CONNECTOR_TEST_STEP_ID.MIGRATE_POETRY_CHECK_MIGRATION_CANDIDATE, step=CheckIsMigrationCandidate(context))]
    )

    steps_to_run.append(
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.MIGRATE_POETRY_POETRY_INIT,
                step=PoetryInit(context, new_version),
                depends_on=[CONNECTOR_TEST_STEP_ID.MIGRATE_POETRY_CHECK_MIGRATION_CANDIDATE],
            )
        ]
    )

    steps_to_run.append(
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.MIGRATE_POETRY_DELETE_SETUP_PY,
                step=DeleteSetUpPy(context),
                depends_on=[CONNECTOR_TEST_STEP_ID.MIGRATE_POETRY_POETRY_INIT],
            )
        ]
    )

    # steps_to_run.append(
    #     [
    #         StepToRun(
    #             id=CONNECTOR_TEST_STEP_ID.BUILD,
    #             step=BuildConnectorImages(context),
    #             depends_on=[CONNECTOR_TEST_STEP_ID.MIGRATE_POETRY_DELETE_SETUP_PY],
    #         )
    #     ]
    # )

    # steps_to_run.append(
    #     [
    #         StepToRun(
    #             id=CONNECTOR_TEST_STEP_ID.MIGRATE_POETRY_REGRESSION_TEST,
    #             step=RegressionTest(context),
    #             depends_on=[CONNECTOR_TEST_STEP_ID.BUILD],
    #             args=lambda results: {
    #                 "new_connector_container": results[CONNECTOR_TEST_STEP_ID.BUILD].output[LOCAL_BUILD_PLATFORM],
    #                 "original_dependencies": results[CONNECTOR_TEST_STEP_ID.MIGRATE_POETRY_POETRY_INIT].output[0],
    #                 "original_dev_dependencies": results[CONNECTOR_TEST_STEP_ID.MIGRATE_POETRY_POETRY_INIT].output[1],
    #             },
    #         )
    #     ]
    # )

    if new_version:
        steps_to_run.append(
            [
                StepToRun(
                    id=CONNECTOR_TEST_STEP_ID.SET_CONNECTOR_VERSION,
                    step=SetConnectorVersion(context, new_version),
                    depends_on=[CONNECTOR_TEST_STEP_ID.MIGRATE_POETRY_DELETE_SETUP_PY],
                )
            ]
        )

    if new_version and changelog:
        steps_to_run.append(
            [
                StepToRun(
                    id=CONNECTOR_TEST_STEP_ID.ADD_CHANGELOG_ENTRY,
                    step=AddChangelogEntry(
                        context,
                        new_version,
                        "Manage dependencies with Poetry.",
                        "0",
                    ),
                    depends_on=[CONNECTOR_TEST_STEP_ID.MIGRATE_POETRY_REGRESSION_TEST],
                )
            ]
        )

    steps_to_run.append(
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.MIGRATE_POETRY_UPDATE_README,
                step=UpdateReadMe(context),
                depends_on=[CONNECTOR_TEST_STEP_ID.MIGRATE_POETRY_DELETE_SETUP_PY],
            )
        ]
    )
    async with semaphore:
        async with context:
            try:
                result_dict = await run_steps(
                    runnables=steps_to_run,
                    options=context.run_step_options,
                )
            except Exception as e:
                await restore_original_state.run()
                raise e
            results = list(result_dict.values())
            if any(step_result.status is StepStatus.FAILURE for step_result in results):
                await restore_original_state.run()
            report = ConnectorReport(context, steps_results=results, name="TEST RESULTS")
            context.report = report

    return report
