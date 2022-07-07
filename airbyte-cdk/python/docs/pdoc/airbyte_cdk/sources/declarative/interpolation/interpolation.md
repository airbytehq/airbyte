Module airbyte_cdk.sources.declarative.interpolation.interpolation
==================================================================

Classes
-------

`Interpolation()`
:   Helper class that provides a standard way to create an ABC using
    inheritance.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * airbyte_cdk.sources.declarative.interpolation.jinja.JinjaInterpolation

    ### Methods

    `eval(self, input_str: str, config: Mapping[str, Any], **kwargs) ‑> str`
    :