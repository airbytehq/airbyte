Module airbyte_cdk.utils.traced_exception
=========================================

Classes
-------

`AirbyteTracedException(internal_message: str = None, message: str = None, failure_type: airbyte_cdk.models.airbyte_protocol.FailureType = FailureType.system_error, exception: BaseException = None)`
:   An exception that should be emitted as an AirbyteTraceMessage
    
    :param internal_message: the internal error that caused the failure
    :param message: a user-friendly message that indicates the cause of the error
    :param failure_type: the type of error
    :param exception: the exception that caused the error, from which the stack trace should be retrieved

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException

    ### Static methods

    `from_exception(exc: Exception, *args, **kwargs) ‑> airbyte_cdk.utils.traced_exception.AirbyteTracedException`
    :   Helper to create an AirbyteTracedException from an existing exception
        :param exc: the exception that caused the error

    ### Methods

    `as_airbyte_message(self) ‑> airbyte_cdk.models.airbyte_protocol.AirbyteMessage`
    :   Builds an AirbyteTraceMessage from the exception

    `emit_message(self)`
    :   Prints the exception as an AirbyteTraceMessage.
        Note that this will be called automatically on uncaught exceptions when using the airbyte_cdk entrypoint.