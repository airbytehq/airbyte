# Contributing to the Python CDK

Learn how you can become a contributor to the Airbyte Python CDK.

## Development

- Make sure [Poetry is installed](https://python-poetry.org/docs/#).
- Run `poetry install`
- For examples, check out the `examples` folder. They can be run via `poetry run python examples/<example file>`
- Unit tests and type checks can be run via `poetry run pytest`

## Documentation

Documentation auto-gen code lives in the `/docs` folder. Based on the doc strings of public methods, we generate API documentation using [pdoc](https://pdoc.dev).

To generate the documentation, run:

```console
poe docs-generate
```

Or to build and open the docs preview in one step:

```console
poe docs-preview
```

or `poetry run poe docs-preview` if you don't have [Poe](https://poethepoet.natn.io/index.html) installed yet.

The `docs-generate` Poe task is mapped to the `run()` function of `docs/generate.py`.

Documentation pages will be generated in the `docs/generated` folder. The `test_docs.py` test in pytest will automatically update generated content. This updates must be manually committed before docs tests will pass.
