Module airbyte_cdk.sources.config
=================================

Classes
-------

`BaseConfig(**data: Any)`
:   Base class for connector spec, adds the following behaviour:
    
    - resolve $ref and replace it with definition
    - replace all occurrences of anyOf with oneOf
    - drop description
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

    ### Static methods

    `schema(*args, **kwargs) ‑> Dict[str, Any]`
    :   We're overriding the schema classmethod to enable some post-processing