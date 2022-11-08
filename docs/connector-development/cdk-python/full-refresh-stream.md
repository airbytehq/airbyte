# Full Refresh Streams

As mentioned in the [Basic Concepts Overview](basic-concepts.md), a `Stream` is the atomic unit for reading data from a Source. A stream can read data from anywhere: a relational database, an API, or even scrape a web page! \(although that might be stretching the limits of what a connector should do\).

To implement a stream, there are two minimum requirements: 1. Define the stream's schema 2. Implement the logic for reading records from the underlying data source

## Defining the stream's schema

Your connector must describe the schema of each stream it can output using [JSONSchema](https://json-schema.org).

The simplest way to do this is to describe the schema of your streams using one `.json` file per stream. You can also dynamically generate the schema of your stream in code, or you can combine both approaches: start with a `.json` file and dynamically add properties to it.

The schema of a stream is the return value of `Stream.get_json_schema`.

### Static schemas

By default, `Stream.get_json_schema` reads a `.json` file in the `schemas/` directory whose name is equal to the value of the `Stream.name` property. In turn `Stream.name` by default returns the name of the class in snake case. Therefore, if you have a class `class EmployeeBenefits(HttpStream)` the default behavior will look for a file called `schemas/employee_benefits.json`. You can override any of these behaviors as you need.

Important note: any objects referenced via `$ref` should be placed in the `shared/` directory in their own `.json` files.

### Dynamic schemas

If you'd rather define your schema in code, override `Stream.get_json_schema` in your stream class to return a `dict` describing the schema using [JSONSchema](https://json-schema.org).

### Dynamically modifying static schemas

Place a `.json` file in the `schemas` folder containing the basic schema like described in the static schemas section. Then, override `Stream.get_json_schema` to run the default behavior, edit the returned value, then return the edited value:

```text
def get_json_schema(self):
    schema = super().get_json_schema()
    schema['dynamically_determined_property'] = "property"
    return schema
```

## Reading records from the data source

If custom functionality is required for reading a stream, you may need to override `Stream.read_records`. Given some information about how the stream should be read, this method should output an iterable object containing records from the data source. We recommend using generators as they are very efficient with regards to memory requirements.

## Incremental Streams

We highly recommend implementing Incremental when feasible. See the [incremental streams page](incremental-stream.md) for more information.

