Module airbyte_cdk.sources.declarative.decoders.decoder
=======================================================

Classes
-------

`Decoder()`
:   Helper class that provides a standard way to create an ABC using
    inheritance.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * airbyte_cdk.sources.declarative.decoders.json_decoder.JsonDecoder

    ### Methods

    `decode(self, response: requests.models.Response) ‑> Mapping[str, Any]`
    :