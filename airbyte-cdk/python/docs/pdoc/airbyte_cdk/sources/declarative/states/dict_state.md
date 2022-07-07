Module airbyte_cdk.sources.declarative.states.dict_state
========================================================

Classes
-------

`DictState(initial_mapping: Mapping[str, str] = None, config=None)`
:   Helper class that provides a standard way to create an ABC using
    inheritance.

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.declarative.states.state.State
    * abc.ABC

    ### Class variables

    `stream_state_field`
    :

    ### Methods

    `get_state(self, state_field)`
    :

    `get_stream_state(self)`
    :

    `set_state(self, state)`
    :

    `update_state(self, **kwargs)`
    :

`StateType(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   An enumeration.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `INT`
    :

    `STR`
    :