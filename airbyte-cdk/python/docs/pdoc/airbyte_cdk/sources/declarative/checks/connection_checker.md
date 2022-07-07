Module airbyte_cdk.sources.declarative.checks.connection_checker
================================================================

Classes
-------

`ConnectionChecker()`
:   Abstract base class for checking a connection

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * airbyte_cdk.sources.declarative.checks.check_stream.CheckStream

    ### Methods

    `check_connection(self, source: airbyte_cdk.sources.source.Source, logger: logging.Logger, config: Mapping[str, Any]) ‑> Tuple[bool, <built-in function any>]`
    :   :param source: source
        :param logger: source logger
        :param config: The user-provided configuration as specified by the source's spec.
          This usually contains information required to check connection e.g. tokens, secrets and keys etc.
        :return: A tuple of (boolean, error). If boolean is true, then the connection check is successful
          and we can connect to the underlying data source using the provided configuration.
          Otherwise, the input config cannot be used to connect to the underlying data source,
          and the "error" object should describe what went wrong.
          The error object will be cast to string to display the problem to the user.