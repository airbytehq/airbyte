import pkgutil
import warnings

import python_jsonschema_objects as pjs
import yaml


def _load_classes(yaml_path: str):
    data = yaml.load(pkgutil.get_data(__name__, yaml_path), Loader=yaml.FullLoader)
    builder = pjs.ObjectBuilder(data)
    return builder.build_classes(standardize_names=False)


# hide json schema version warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=UserWarning)
    message_classes = _load_classes("yaml/airbyte_message.yaml")
    AirbyteMessage = message_classes.AirbyteMessage
    AirbyteLogMessage = message_classes.AirbyteLogMessage
    AirbyteRecordMessage = message_classes.AirbyteRecordMessage
    AirbyteStateMessage = message_classes.AirbyteStateMessage

    catalog_classes = _load_classes("yaml/airbyte_catalog.yaml")
    AirbyteCatalog = catalog_classes.AirbyteCatalog
    AirbyteStream = catalog_classes.AirbyteStream
