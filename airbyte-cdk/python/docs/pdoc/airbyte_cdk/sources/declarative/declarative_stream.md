Module airbyte_cdk.sources.declarative.declarative_stream
=========================================================

Classes
-------

`DeclarativeStream(name: str, primary_key, schema_loader: airbyte_cdk.sources.declarative.schema.schema_loader.SchemaLoader, retriever: airbyte_cdk.sources.declarative.retrievers.retriever.Retriever, cursor_field: Optional[List[str]] = None, checkpoint_interval: Optional[int] = None)`
:   DeclarativeStream is a Stream that delegates most of its logic to its schema_load and retriever

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.streams.core.Stream
    * abc.ABC

    ### Class variables

    `transformer: airbyte_cdk.sources.utils.transform.TypeTransformer`
    :

    ### Instance variables

    `state: MutableMapping[str, Any]`
    :