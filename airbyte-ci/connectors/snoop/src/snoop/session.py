from __future__ import annotations

import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from snoop.proxy import MitmProxy
from snoop import logger
from snoop.collectors import ConnectorHttpFlowsCollector

if TYPE_CHECKING:
    from snoop.collectors import ConnectorConfigCollector, ConnectorMessageCollector
    from snoop.runners import CommandRunner

class Session:

    PROXY_PORT = 8080
    REQUIRED_ENV_VARS = ["PATH_TO_METADATA", "AIRBYTE_ENTRYPOINT"]
    
    def __init__(self, airbyte_command: str, connector_metadata: dict, connector_command_runner: CommandRunner, config_collector: ConnectorConfigCollector, message_collector: ConnectorMessageCollector) -> None:
        self.airbyte_command = airbyte_command
        self.connector_metadata = connector_metadata
        self.connector_command_runner = connector_command_runner
        self.config_collector = config_collector
        self.message_collector = message_collector
        self.session_start_time = None
        self.session_end_time = None
        self.mitm_proxy = None


    @property
    def has_started(self) -> bool:
        return self.session_start_time is not None
    
    @property
    def session_id(self) -> str:
        if not self.has_started:
            raise ValueError("Session has not started yet")
        epoch_time = int(self.session_start_time.timestamp())
        docker_repository = self.connector_metadata["data"]["dockerRepository"]
        version = self.connector_metadata["data"]["dockerImageTag"]
        return f"{docker_repository}-{version}-{self.airbyte_command}-{epoch_time}"
    

    def __enter__(self) -> Session:
        self.session_start_time = datetime.datetime.now()
        logger.info(f"Starting session {self.session_id}")
        self.message_collector.snoop_session = self
        with MitmProxy(proxy_port=self.PROXY_PORT, har_dump_path=Path("/tmp/http_traffic.har")) as proxy:
            self.proxy = proxy
            self.exit_code = self.connector_command_runner.run()
            return self
    
    def __exit__(self, exc_type, exc, tb) -> None:
        self.session_end_time = datetime.datetime.now()
        http_flows_collector = ConnectorHttpFlowsCollector(self)
        http_flows_collector.collect()
        http_flows_collector.wait_for_all_publishes()
        self.message_collector.wait_for_all_publishes()
        # raw_artifact = create_artifact(
        #     session_id=self.session_id,
        #     start_time=self.session_start_time,
        #     end_time=self.session_end_time,
        #     connector_technical_name=self.connector_metadata["data"]["dockerRepository"].split("/")[-1],
        #     airbyte_command=self.airbyte_command,
        #     config_collector=self.config_collector,
        #     message_collector=self.message_collector,
        #     exit_code=self.exit_code,
        # )
        # logger.info(f"Session {self.session_id} ended")
        # publish_to_artifact_topic(
        #     "ab-connector-integration-test", 
        #     "snoop-connector-data", 
        #     raw_artifact
        # )