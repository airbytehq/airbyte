Module airbyte_cdk.utils.airbyte_secrets_utils
==============================================

Functions
---------

    
`filter_secrets(string: str) ‑> str`
:   Filter secrets from a string by replacing them with ****

    
`get_secret_paths(spec: Mapping[str, Any]) ‑> List[List[str]]`
:   

    
`get_secrets(connection_specification: Mapping[str, Any], config: Mapping[str, Any]) ‑> List[Any]`
:   Get a list of secret values from the source config based on the source specification
    :type connection_specification: the connection_specification field of an AirbyteSpecification i.e the JSONSchema definition

    
`update_secrets(secrets: List[str])`
:   Update the list of secrets to be replaced