# Contributing to AirbyteLib

Learn how you can become a contributor to AirbyteLib.

## Development

- Make sure [Poetry is installed](https://python-poetry.org/docs/#).
- Run `poetry install`
- For examples, check out the `examples` folder. They can be run via `poetry run python examples/<example file>`
- Unit tests and type checks can be run via `poetry run pytest`

## Documentation

Regular documentation lives in the `/docs` folder. Based on the doc strings of public methods, we generate API documentation using [pdoc](https://pdoc.dev).

To generate the documentation, run:

```console
poetry run generate-docs
```

The `generate-docs` CLI command is mapped to the `run()` function of `docs.py` in the root `airbyte-lib` directory.

Documentation pages will be generated in the `docs/generated` folder. The `test_docs.py` test in pytest will automatically update generated content. This updates must be manually committed before docs tests will pass.

## Release

- In your PR:
  - Bump the version in `pyproject.toml`
  - Add a changelog entry to the table below
- Once the PR is merged, go to Github and trigger the `Publish AirbyteLib Manually` workflow. This will publish the new version to PyPI.

## Versioning

Versioning follows [Semantic Versioning](https://semver.org/). For new features, bump the minor version. For bug fixes, bump the patch version. For pre-releases, append `dev.N` to the version. For example, `0.1.0dev.1` is the first pre-release of the `0.1.0` version.
