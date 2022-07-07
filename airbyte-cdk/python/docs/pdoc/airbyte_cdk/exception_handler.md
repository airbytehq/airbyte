Module airbyte_cdk.exception_handler
====================================

Functions
---------

    
`init_uncaught_exception_handler(logger: logging.Logger) ‑> None`
:   Handles uncaught exceptions by emitting an AirbyteTraceMessage and making sure they are not
    printed to the console without having secrets removed.