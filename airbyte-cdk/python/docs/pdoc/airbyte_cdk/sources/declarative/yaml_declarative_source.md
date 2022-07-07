Module airbyte_cdk.sources.declarative.yaml_declarative_source
==============================================================

Classes
-------

`YamlDeclarativeSource(path_to_yaml)`
:   Base class for declarative Source. Concrete sources need to define the connection_checker to use

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.declarative.declarative_source.DeclarativeSource
    * airbyte_cdk.sources.abstract_source.AbstractSource
    * airbyte_cdk.sources.source.Source
    * airbyte_cdk.connector.DefaultConnectorMixin
    * airbyte_cdk.sources.source.BaseSource
    * airbyte_cdk.connector.BaseConnector
    * abc.ABC
    * typing.Generic

    ### Instance variables

    `connection_checker`
    :