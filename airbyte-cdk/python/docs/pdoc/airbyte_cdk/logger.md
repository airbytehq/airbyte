Module airbyte_cdk.logger
=========================

Functions
---------

    
`init_logger(name: str = None)`
:   Initial set up of logger

    
`log_by_prefix(msg: str, default_level: str) ‑> Tuple[int, str]`
:   Custom method, which takes log level from first word of message

Classes
-------

`AirbyteLogFormatter(fmt=None, datefmt=None, style='%', validate=True)`
:   Output log records using AirbyteMessage
    
    Initialize the formatter with specified format strings.
    
    Initialize the formatter either with the specified format string, or a
    default as described above. Allow for specialized date formatting with
    the optional datefmt argument. If datefmt is omitted, you get an
    ISO8601-like (or RFC 3339-like) format.
    
    Use a style parameter of '%', '{' or '$' to specify that you want to
    use one of %-formatting, :meth:`str.format` (``{}``) formatting or
    :class:`string.Template` formatting in your format string.
    
    .. versionchanged:: 3.2
       Added the ``style`` parameter.

    ### Ancestors (in MRO)

    * logging.Formatter

    ### Class variables

    `level_mapping`
    :

    ### Methods

    `format(self, record: logging.LogRecord) ‑> str`
    :   Return a JSON representation of the log message

`AirbyteLogger(*args, **kwargs)`
:   

    ### Methods

    `debug(self, message)`
    :

    `error(self, message)`
    :

    `exception(self, message)`
    :

    `fatal(self, message)`
    :

    `info(self, message)`
    :

    `log(self, level, message)`
    :

    `trace(self, message)`
    :

    `warn(self, message)`
    :