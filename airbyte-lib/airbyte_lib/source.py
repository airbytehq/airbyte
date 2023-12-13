

from airbyte_lib.registry import ConnectorMetadata, get_connector_metadata
import jsonschema
from functools import lru_cache
import json
from pathlib import Path
import subprocess
from typing import Any, Dict, Iterable, List, Optional, IO
from airbyte_cdk.models import AirbyteMessage, AirbyteCatalog, Type, AirbyteRecordMessage, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, SyncMode, DestinationSyncMode, Status, ConnectorSpecification
import tempfile
from abc import ABC, abstractmethod
from contextlib import contextmanager


@contextmanager
def as_temp_files(files: List[Any]):
    temp_files: List[Any] = []
    try:
        for content in files:
            temp_file = tempfile.NamedTemporaryFile(mode='w+t', delete=True)
            temp_file.write(json.dumps(content) if isinstance(content, dict) else content)
            temp_file.flush()
            temp_files.append(temp_file)
        yield [file.name for file in temp_files]
    finally:
        for temp_file in temp_files:
            try:
                temp_file.close()
            except:
                pass


from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
import subprocess
from typing import List, IO


class Executor(ABC):
    def __init__(self, metadata: ConnectorMetadata):
        self.metadata = metadata

    @abstractmethod
    @contextmanager
    def execute(self, args: List[str]) -> IO[str]:
        pass

class VenvExecutor(Executor):
    def __init__(self, metadata: ConnectorMetadata):
        super().__init__(metadata)

    @contextmanager
    def execute(self, args: List[str]) -> IO[str]:
        venv_name = f".venv-{self.metadata.name}"
        venv_path = Path(venv_name)
        if not venv_path.exists():
            raise Exception(f"Could not find venv {venv_name}")

        connector_path = Path(venv_path, "bin", self.metadata.name)
        if not connector_path.exists():
            raise Exception(f"Could not find connector {self.metadata.name} in venv {venv_name}")

        process = subprocess.Popen(
            [str(connector_path)] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        try:
            yield process.stdout
        finally:
            exit_code = process.wait()
            if exit_code != 0:
                raise Exception(f"Process exited with code {exit_code}")


class Source:
    """This class is representing a source that can be called"""

    def __init__(self, executor: Executor, name: str, version: str = "latest", config: Optional[Dict[str, Any]] = None, streams: Optional[List[str]] = None):
        self.executor = executor
        self.name = name
        self.version = version
        if not config is None:
            self.set_config(config)
        if not streams is None:
            self.set_streams(streams)
    
    def set_streams(self, streams: List[str]):
        available_streams = self.get_available_streams()
        for stream in streams:
            if stream not in available_streams:
                raise Exception(f"Stream {stream} is not available for connector {self.name}, choose from {available_streams}")
        self.streams = streams
    
    def set_config(self, config: Dict[str, Any]):
        self._validate_config(config)
        self.config = config
    
    def discover(self) -> AirbyteCatalog:
        """
        Call discover on the connector.

        This involves the following steps:
        * Write the config to a temporary file
        * execute the connector with discover --config <config_file>
        * Listen to the messages and return the first AirbyteCatalog that comes along.
        * Make sure the subprocess is killed when the function returns.
        """
        with as_temp_files([self.config]) as [config_file]:
            for msg in self._execute(["discover", "--config", config_file]):
                if msg.type == Type.CATALOG and msg.catalog:
                    return msg.catalog
            raise Exception("Connector did not return a catalog")
        
    def _validate_config(self, config: Dict[str, any]) -> None:
        """
        Validate the config against the spec.
        """
        spec = self._spec()
        jsonschema.validate(config, spec.connectionSpecification)
    
    def get_available_streams(self) -> List[str]:
        """
        Get the available streams from the spec.
        """
        return [s.name for s in self.discover().streams]
    
    @lru_cache(maxsize=1)
    def _spec(self) -> ConnectorSpecification:
        """
        Call spec on the connector.

        This involves the following steps:
        * execute the connector with spec
        * Listen to the messages and return the first AirbyteCatalog that comes along.
        * Make sure the subprocess is killed when the function returns.
        """
        for msg in self._execute(["spec"]):
            if msg.type == Type.SPEC and msg.spec:
                return msg.spec
        raise Exception("Connector did not return a spec")

    def check(self):
        """
        Call check on the connector.

        This involves the following steps:
        * Write the config to a temporary file
        * execute the connector with check --config <config_file>
        * Listen to the messages and return the first AirbyteCatalog that comes along.
        * Make sure the subprocess is killed when the function returns.
        """
        with as_temp_files([self.config]) as [config_file]:
            for msg in self._execute(["check", "--config", config_file]):
                if msg.type == Type.CONNECTION_STATUS and msg.connectionStatus:
                    if msg.connectionStatus.status == Status.FAILED:
                        raise Exception(f"Connector returned failed status: {msg.connectionStatus.message}")
                    else:
                        return
            raise Exception("Connector did not return check status")
    
    def read(self) -> Iterable[AirbyteRecordMessage]:
        """
        Call read on the connector.

        This involves the following steps:
        * Call discover to get the catalog
        * Generate a configured catalog that syncs all streams in full_refresh mode
        * Write the configured catalog and the config to a temporary file
        * execute the connector with read --config <config_file> --catalog <catalog_file>
        * Listen to the messages and return the AirbyteRecordMessages that come along.
        """
        catalog = self.discover()
        configured_catalog = ConfiguredAirbyteCatalog(streams=[ConfiguredAirbyteStream(stream=s, sync_mode=SyncMode.full_refresh, destination_sync_mode=DestinationSyncMode.overwrite) for s in catalog.streams if s.name in self.streams or self.streams is None])
        with as_temp_files([self.config, configured_catalog.json()]) as [config_file, catalog_file]:
            for msg in self._execute(["read", "--config", config_file, "--catalog", catalog_file]):
                if msg.type == Type.RECORD:
                    yield msg.record

    
    def _execute(self, args: List[str]) -> Iterable[AirbyteMessage]:
        """
        Execute the connector with the given arguments.

        This involves the following steps:
        * Locate the right venv. It is called ".venv-<connector_name>"
        * Spawn a subprocess with .venv-<connector_name>/bin/<connector-name> <args>
        * Read the output line by line of the subprocess and serialize them AirbyteMessage objects. Drop if not valid.
        """

        last_log_messages = []
        try:
            with self.executor.execute(args) as output:
                for line in output:
                    try:
                        message = AirbyteMessage.parse_raw(line)
                        yield message
                        if message.type == Type.LOG:
                            last_log_messages.append(message.log.message)
                            if len(last_log_messages) > 10:
                                last_log_messages.pop(0)
                    except Exception:
                        # line is probably a log message, add it to the last log messages
                        last_log_messages.append(line)
                        if len(last_log_messages) > 10:
                            last_log_messages.pop(0)
        except Exception as e:
            raise Exception(f"{str(e)}. Last logs: {last_log_messages}")
        

def get_connector(name: str, version: str = "latest", config: Optional[Dict[str, Any]] = None):
    """Get a connector by name and version."""
    metadata = get_connector_metadata(name)
    return Source(VenvExecutor(metadata), name, version, config)