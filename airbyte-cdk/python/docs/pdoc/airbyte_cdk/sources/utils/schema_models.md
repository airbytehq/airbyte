Module airbyte_cdk.sources.utils.schema_models
==============================================

Classes
-------

`AllOptional(*args, **kwargs)`
:   Metaclass for marking all Pydantic model fields as Optional
    Here is example of declaring model using this metaclass like:
    '''
            class MyModel(BaseModel, metaclass=AllOptional):
                a: str
                b: str
    '''
    it is an equivalent of:
    '''
            class MyModel(BaseModel):
                a: Optional[str]
                b: Optional[str]
    '''
    It would make code more clear and eliminate a lot of manual work.

    ### Ancestors (in MRO)

    * pydantic.main.ModelMetaclass
    * abc.ABCMeta
    * builtins.type

`BaseSchemaModel(**data: Any)`
:   Base class for all schema models. It has some extra schema postprocessing.
    Can be used in combination with AllOptional metaclass
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

    ### Class variables

    `Config`
    :

    ### Static methods

    `schema(*args, **kwargs) ‑> Dict[str, Any]`
    :   We're overriding the schema classmethod to enable some post-processing