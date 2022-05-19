#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.lcc.YamlConfigurableSource import YamlConfigurableSource


class SendgridSource(YamlConfigurableSource):
    """
    This is a sample low-code connector.
    It still uses the existing spec.yaml file
    """

    def __init__(self):
        super().__init__(**{"path_to_yaml": "./source_sendgrid/sendgrid.yaml"})
