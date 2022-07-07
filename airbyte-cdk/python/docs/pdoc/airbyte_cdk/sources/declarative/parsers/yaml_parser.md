Module airbyte_cdk.sources.declarative.parsers.yaml_parser
==========================================================

Classes
-------

`YamlParser()`
:   Helper class that provides a standard way to create an ABC using
    inheritance.

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.declarative.parsers.config_parser.ConfigParser
    * abc.ABC

    ### Class variables

    `ref_tag`
    :

    ### Methods

    `get_ref_key(self, s: str) ‑> str`
    :

    `parse(self, config_str: str) ‑> Mapping[str, Any]`
    :   Parses a yaml file and dereferences string in the form "*ref({reference)"
        to {reference}
        :param config_str: yaml string to parse
        :return:

    `preprocess(self, value, evaluated_config, path)`
    :

    `preprocess_dict(self, input_mapping, evaluated_mapping, path)`
    :   :param input_mapping: mapping produced by parsing yaml
        :param evaluated_mapping: mapping produced by dereferencing the content of input_mapping
        :param path: curent path in configuration traversal
        :return:

    `resolve_value(self, value, path)`
    :