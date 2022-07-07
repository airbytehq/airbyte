Module airbyte_cdk.utils.event_timing
=====================================

Functions
---------

    
`create_timer(name)`
:   Creates a new EventTimer as a context manager to improve code readability.

Classes
-------

`Event(name: str, start: float = <factory>, end: Optional[float] = None)`
:   Event(name: str, start: float = <factory>, end: Optional[float] = None)

    ### Class variables

    `end: Optional[float]`
    :

    `name: str`
    :

    `start: float`
    :

    ### Instance variables

    `duration: float`
    :   Returns the elapsed time in seconds or positive infinity if event was never finished

    ### Methods

    `finish(self)`
    :

`EventTimer(name)`
:   Simple nanosecond resolution event timer for debugging, initially intended to be used to record streams execution
    time for a source.
       Event nesting follows a LIFO pattern, so finish will apply to the last started event.

    ### Methods

    `finish_event(self)`
    :   Finish the current event and pop it from the stack.

    `report(self, order_by='name')`
    :   :param order_by: 'name' or 'duration'

    `start_event(self, name)`
    :   Start a new event and push it to the stack.