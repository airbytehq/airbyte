import os

from .base_comparator import BaseComparator
from ..utils import ConnectorUnderTest, sh_dash_c
from dagger import Client, Container


class DiffComparator(BaseComparator):

    def __init__(self, dagger_client: Client, test_output_directory: str):
        self._test_output_directory = test_output_directory
        self._in_container_results_directory = "/tmp"
        self._in_container_results_file = f"{self._in_container_results_directory}/diff_output.txt"
        self._container = (
            dagger_client.container().from_("debian:buster")
            .with_directory(self._in_container_results_directory,
                            dagger_client.host().directory(self._test_output_directory)))
        os.makedirs(self._in_container_results_directory, exist_ok=True)

    async def _diff(self, container: Container, control_connector: ConnectorUnderTest, target_connector: ConnectorUnderTest) -> Container:
        control_directory = f"{self._in_container_results_directory}/{control_connector.version}"
        target_directory = f"{self._in_container_results_directory}/{target_connector.version}"

        return (
            container
            .with_exec(
                sh_dash_c([f"diff -ur --exclude=raw_output.txt "
                           f"{control_directory} {target_directory} > "
                           f"{self._in_container_results_file} 2>&1 | "
                           f"tee -a {self._in_container_results_file}"])
            )
        )

    async def compare(self, control_connector: ConnectorUnderTest, target_connector: ConnectorUnderTest) -> Container:
        container = await self._diff(self._container, control_connector, target_connector)
        await container.file(self._in_container_results_file).export(f"{self._test_output_directory}/diff_output.txt")
        return container
