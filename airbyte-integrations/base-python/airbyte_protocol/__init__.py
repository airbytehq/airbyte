from typing import Generator
import yaml
import json
import pkgutil
import warnings
import python_jsonschema_objects as pjs
from dataclasses import dataclass


def _load_classes(yaml_path: str):
    data = yaml.load(pkgutil.get_data(__name__, yaml_path), Loader=yaml.FullLoader)
    builder = pjs.ObjectBuilder(data)
    return builder.build_classes(standardize_names=False)


# hide json schema version warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=UserWarning)
    message_classes = _load_classes("models/airbyte_message.yaml")
    AirbyteMessage = message_classes.AirbyteMessage
    AirbyteLogMessage = message_classes.AirbyteLogMessage
    AirbyteRecordMessage = message_classes.AirbyteRecordMessage
    AirbyteStateMessage = message_classes.AirbyteStateMessage

    catalog_classes = _load_classes("models/airbyte_catalog.yaml")
    AirbyteCatalog = catalog_classes.AirbyteCatalog
    AirbyteStream = catalog_classes.AirbyteStream


class AirbyteSpec(object):
    def __init__(self, spec_string):
        self.spec_string = spec_string


class AirbyteCheckResponse(object):
    def __init__(self, successful, field_to_error):
        self.successful = successful
        self.field_to_error = field_to_error


class Integration(object):
    def __init__(self):
        pass

    def spec(self) -> AirbyteSpec:
        raise Exception("Not Implemented")

    def read_config(self, config_path):
        with open(config_path, 'r') as file:
            contents = file.read()
        return json.loads(contents)

    # can be overridden to change an input file config
    def transform_config(self, raw_config):
        return raw_config

    def write_config(self, config_object, path):
        with open(path, 'w') as fh:
            fh.write(json.dumps(config_object))

    def check(self, logger, config_container) -> AirbyteCheckResponse:
        raise Exception("Not Implemented")

    def discover(self, logger, config_container) -> AirbyteCatalog:
        raise Exception("Not Implemented")


class Source(Integration):
    def __init__(self):
        pass

    # Iterator<AirbyteMessage>
    def read(self, logger, config_container, catalog_path, state=None) -> Generator[AirbyteMessage, None, None]:
        raise Exception("Not Implemented")


class Destination(Integration):
    def __init__(self):
        pass


class AirbyteLogger:
    def __init__(self):
        self.valid_log_types = ["FATAL", "ERROR", "WARN", "INFO", "DEBUG", "TRACE"]

    def log_by_prefix(self, message, default_level):
        split_line = message.split()
        first_word = next(iter(split_line), None)
        if first_word in self.valid_log_types:
            log_level = first_word
            rendered_message = " ".join(split_line[1:])
        else:
            log_level = default_level
            rendered_message = message
        self.log(log_level, rendered_message)

    def log(self, level, message):
        log_record = AirbyteLogMessage(level=level, message=message)
        log_message = AirbyteMessage(type="LOG", log=log_record)
        print(log_message.serialize())

    def fatal(self, message):
        self.log("FATAL", message)

    def error(self, message):
        self.log("ERROR", message)

    def warn(self, message):
        self.log("WARN", message)

    def info(self, message):
        self.log("INFO", message)

    def debug(self, message):
        self.log("DEBUG", message)

    def trace(self, message):
        self.log("TRACE", message)

@dataclass
class ConfigContainer:
    raw_config: object
    rendered_config: object
    raw_config_path: str
    rendered_config_path: str
