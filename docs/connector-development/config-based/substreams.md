# Substreams

#### FIXME: Conceptually, this is about nested lists. TODO: Move lists stream slicers to this section

Substreams are streams that depend on the records on another stream

We might for instance want to read all the commits for a given repository (parent stream).

## Substream slicer

Substreams are implemented by defining their stream slicer as a`SubstreamSlicer`.

`SubstreamSlicer` iterates over the parent's stream slices.
We might for instance want to read all the commits for a given repository (parent resource).

- what the parent stream is
- what is the key of the records in the parent stream
- what is the field defining the stream slice representing the parent record
- how to specify that information on an outgoing HTTP request

Schema:

```yaml
  SubstreamSlicer:
    type: object
    required:
      - parent_stream_configs
    additionalProperties: false
    properties:
      "$options":
        "$ref": "#/definitions/$options"
      parent_stream_configs:
        type: array
        items:
          "$ref": "#/definitions/ParentStreamConfig"
  ParentStreamConfig:
    type: object
    required:
      - stream
      - parent_key
      - stream_slice_field
    additionalProperties: false
    properties:
      "$options":
        "$ref": "#/definitions/$options"
      stream:
        "$ref": "#/definitions/Stream"
      parent_key:
        type: string
      stream_slice_field:
        type: string
      request_option:
        "$ref": "#/definitions/RequestOption"
```

=======
> > > > > > > master
> > > > > > > Assuming the commits for a given repository can be read by specifying the repository as a request_parameter, this could be defined as

```yaml
stream_slicer:
  type: "SubstreamSlicer"
  parent_streams_configs:
    - stream: "*ref(repositories_stream)"
      parent_key: "id"
      stream_slice_field: "repository"
      request_option:
        field_name: "repository"
        inject_into: "request_parameter"
```

REST APIs often nest sub-resources in the URL path.
If the URL to fetch commits was "/repositories/:id/commits", then the `Requester`'s path would need to refer to the stream slice's value and no `request_option` would be set:

```yaml
retriever:
  <...>
  requester:
    <...>
    path: "/respositories/{{ stream_slice.repository }}/commits"
  stream_slicer:
    type: "SubstreamSlicer"
parent_streams_configs:
  - stream: "*ref(repositories_stream)"
    parent_key: "id"
    stream_slice_field: "repository"
```

## More readings

- [$options](./yaml-structure.md#options)
- [Stream slicers](./stream-slicers.md)
