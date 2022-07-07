Module airbyte_cdk.sources.declarative.parsers.factory
======================================================

Classes
-------

`DeclarativeComponentFactory()`
:   

    ### Static methods

    `get_default_type(parameter_name, parent_class)`
    :

    `is_object_definition_with_class_name(definition)`
    :

    `is_object_definition_with_type(definition)`
    :

    ### Methods

    `build(self, class_or_class_name: Union[str, Type], config, **kwargs)`
    :

    `create_component(self, component_definition: Mapping[str, Any], config: Config)`
    :   :param component_definition: mapping defining the object to create. It should have at least one field: `class_name`
        :param config: Connector's config
        :return: the object to create