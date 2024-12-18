# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import logging
import uuid

import dagger

from . import mitm_addons


class Proxy:
    """
    This class is a wrapper around a mitmproxy container. It allows to declare a mitmproxy container,
    bind it as a service to a different container and retrieve the mitmproxy stream file.
    """

    MITMPROXY_IMAGE = "mitmproxy/mitmproxy:10.2.4"
    MITM_STREAM_FILE = "stream.mitm"
    PROXY_PORT = 8080
    MITM_ADDONS_PATH = mitm_addons.__file__

    def __init__(
        self,
        dagger_client: dagger.Client,
        hostname: str,
        session_id: str,
        stream_for_server_replay: dagger.File | None = None,
    ) -> None:
        self.dagger_client = dagger_client
        self.hostname = hostname
        self.session_id = session_id
        self.stream_for_server_replay = stream_for_server_replay

    @property
    def dump_cache_volume(self) -> dagger.CacheVolume:
        # We namespace the cache by:
        # - Mitmproxy image name to make sure we're not re-using a cached artifact on a different and potentially incompatible mitmproxy version
        # - Hostname to avoid sharing the same https dump between different tests
        # - Session id to avoid sharing the same https dump between different runs of the same tests
        # The session id is set to the Airbyte Connection ID to ensure that no cache is shared between connections
        return self.dagger_client.cache_volume(f"{self.MITMPROXY_IMAGE}{self.hostname}{self.session_id}")

    @property
    def mitmproxy_dir_cache(self) -> dagger.CacheVolume:
        return self.dagger_client.cache_volume(self.MITMPROXY_IMAGE)

    def generate_mitmconfig(self):
        return (
            self.dagger_client.container()
            .from_(self.MITMPROXY_IMAGE)
            # Mitmproxy generates its self signed certs at first run, we need to run it once to generate the certs
            # They are stored in /root/.mitmproxy
            .with_exec(["timeout", "--preserve-status", "1", "mitmdump"])
            .directory("/root/.mitmproxy")
        )

    async def get_container(self, mitm_config: dagger.Directory) -> dagger.Container:
        """Get a container for the mitmproxy service.
        If a stream for server replay is provided, it will be used to replay requests to the same URL.

        Returns:
            dagger.Container: The container for the mitmproxy service.
            mitm_config (dagger.Directory): The directory containing the mitmproxy configuration.
        """
        container_addons_path = "/addons.py"
        proxy_container = (
            self.dagger_client.container()
            .from_(self.MITMPROXY_IMAGE)
            .with_exec(["mkdir", "/dumps"])
            # This is caching the mitmproxy stream files, which can contain sensitive information
            # We want to nuke this cache after test suite execution.
            .with_mounted_cache("/dumps", self.dump_cache_volume)
            # This is caching the mitmproxy self-signed certificate, no sensitive information is stored in it
            .with_file(
                container_addons_path,
                self.dagger_client.host().file(self.MITM_ADDONS_PATH),
            )
            .with_directory("/root/.mitmproxy", mitm_config)
        )

        # If the proxy was instantiated with a stream for server replay from a previous run, we want to use it.
        # Requests to the same URL will be replayed from the stream instead of being sent to the server.
        # This is useful to avoid rate limiting issues and limits responses drifts due to time based logics.
        if self.stream_for_server_replay is not None and await self.stream_for_server_replay.size() > 0:
            proxy_container = proxy_container.with_file("/cache.mitm", self.stream_for_server_replay)
            command = [
                "mitmdump",
                "-s",
                container_addons_path,
                "--flow-detail",
                "2",
                "--server-replay",
                "/cache.mitm",
                "--save-stream-file",
                f"/dumps/{self.MITM_STREAM_FILE}",
            ]
        else:
            command = [
                "mitmdump",
                "-s",
                container_addons_path,
                "--flow-detail",
                "2",
                "--save-stream-file",
                f"/dumps/{self.MITM_STREAM_FILE}",
            ]

        return proxy_container.with_exec(command)

    async def get_service(self, mitm_config: dagger.Directory) -> dagger.Service:
        return (await self.get_container(mitm_config)).with_exposed_port(self.PROXY_PORT).as_service()

    async def bind_container(self, container: dagger.Container) -> dagger.Container:
        """Bind a container to the proxy service and set environment variables to use the proxy for HTTP(S) traffic.

        Args:
            container (dagger.Container): The container to bind to the proxy service.

        Returns:
            dagger.Container: The container with the proxy service bound and environment variables set.
        """
        mitmconfig_dir = self.generate_mitmconfig()
        pem = mitmconfig_dir.file("mitmproxy-ca.pem")

        # Find the python version in the container to get the correct path for the requests cert file
        # We will overwrite this file with the mitmproxy self-signed certificate
        # I could not find a less brutal way to make Requests trust the mitmproxy self-signed certificate
        # I tried running update-ca-certificates + setting REQUESTS_CA_BUNDLE in the container but it did not work
        python_version_output = (await container.with_exec(["python", "--version"]).stdout()).strip()
        python_version = python_version_output.split(" ")[-1]
        python_version_minor_only = ".".join(python_version.split(".")[:-1])
        requests_cert_path = f"/usr/local/lib/python{python_version_minor_only}/site-packages/certifi/cacert.pem"
        current_user = (await container.with_exec(["whoami"]).stdout()).strip()
        try:
            return await (
                container.with_user("root")
                # Overwrite the requests cert file with the mitmproxy self-signed certificate
                .with_file(requests_cert_path, pem, owner=current_user)
                .with_env_variable("http_proxy", f"{self.hostname}:{self.PROXY_PORT}")
                .with_env_variable("https_proxy", f"{self.hostname}:{self.PROXY_PORT}")
                .with_user(current_user)
                .with_service_binding(self.hostname, await self.get_service(mitmconfig_dir))
            )
        except dagger.DaggerError as e:
            # This is likely hapenning on Java connector images whose certificates location is different
            # TODO handle this case
            logging.warn(f"Failed to bind container to proxy: {e}")
            return container

    async def retrieve_http_dump(self) -> dagger.File | None:
        """We mount the cache volume, where the mitmproxy container saves the stream file, to a fresh container.
        We then copy the stream file to a new directory and return it as a dagger.File.
        The copy operation to /to_export is required as Dagger does not support direct access to files in cache volumes.


        Returns:
            dagger.File | None: The mitmproxy stream file if it exists, None otherwise.
        """
        container = (
            self.dagger_client.container()
            .from_("alpine:latest")
            .with_env_variable("CACHEBUSTER", str(uuid.uuid4()))
            .with_mounted_cache("/dumps", self.dump_cache_volume)
        )
        dump_files = (await container.with_exec(["ls", "/dumps"]).stdout()).splitlines()
        if self.MITM_STREAM_FILE not in dump_files:
            return None
        return await (
            container.with_exec(["mkdir", "/to_export"], use_entrypoint=True)
            .with_exec(["cp", "-r", f"/dumps/{self.MITM_STREAM_FILE}", f"/to_export/{self.MITM_STREAM_FILE}"], use_entrypoint=True)
            .file(f"/to_export/{self.MITM_STREAM_FILE}")
        )

    async def clear_cache_volume(self) -> None:
        """Delete all files in the cache volume. This is useful to avoid caching sensitive information between tests."""
        await (
            self.dagger_client.container()
            .from_("alpine:latest")
            .with_mounted_cache("/to_clear", self.dump_cache_volume)
            .with_exec(["rm", "-rf", "/to_clear/*"], use_entrypoint=True)
            .sync()
        )
        logging.info(f"Cache volume {self.dump_cache_volume} cleared")
