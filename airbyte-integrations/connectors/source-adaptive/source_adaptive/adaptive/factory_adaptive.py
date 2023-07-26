import json
from source_adaptive.adaptive.base import get_config_as_dict

from source_adaptive.adaptive.exportAccounts import AdaptiveExportAccounts
from source_adaptive.adaptive.exportAttributes import AdaptiveExportAttributes
from source_adaptive.adaptive.exportData import AdaptiveExportData
from source_adaptive.adaptive.exportVersions import AdaptiveExportVersions

from airbyte_cdk.logger import AirbyteLogger


def generate_adaptive_method(logger: AirbyteLogger, config: json):
    """
    A factory method to serve all methods implemented as abstract as possible
    """
    method = get_config_as_dict(config)["method_obj"]["method"]

    # a dictionary mapper that maps a string method to the respective class that will handle that
    method_class_mapper = {
        "exportAccounts": AdaptiveExportAccounts,
        "exportAttributes": AdaptiveExportAttributes,
        "exportData": AdaptiveExportData,
        "exportVersions": AdaptiveExportVersions,
    }

    if method not in method_class_mapper.keys():
        return None

    adaptive_action = method_class_mapper[method](logger=logger, config=config)
    return adaptive_action
