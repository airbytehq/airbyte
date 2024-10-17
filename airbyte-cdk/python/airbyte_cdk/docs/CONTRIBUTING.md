# Contributing to PyAirbyte

Learn how you can become a contributor to PyAirbyte.

## Development

- Make sure [Poetry is installed](https://python-poetry.org/docs/#).
- Run `poetry install`
- For examples, check out the `examples` folder. They can be run via `poetry run python examples/<example file>`
- Unit tests and type checks can be run via `poetry run pytest`

## Documentation

Regular documentation lives in the `/docs` folder. Based on the doc strings of public methods, we generate API documentation using [pdoc](https://pdoc.dev).

To generate the documentation, run:

```console
poe docs-generate
```

Or to build and open in one step:


```console
poe docs-preview
```


or `poetry run poe docs-preview` if you don't have [Poe](https://poethepoet.natn.io/index.html) installed.

The `docs-generate` Poe task is mapped to the `run()` function of `docs/generate.py`.

Documentation pages will be generated in the `docs/generated` folder. The `test_docs.py` test in pytest will automatically update generated content. This updates must be manually committed before docs tests will pass.

## Release

Releases are published automatically to PyPi in response to a "published" event on a GitHub Release Tag.

To publish to PyPi, simply [create a GitHub Release](https://github.com/airbytehq/PyAirbyte/releases/new) with the correct version. Once you publish the release on GitHub it will automatically trigger a PyPi publish workflow in GitHub actions.

> **Warning**
>
> Be careful - "Cmd+Enter" will not 'save' but will instead 'publish'. (If you want to save a draft, use the mouse. 😅)

> **Note**
>
> There is no version to bump. Version is calculated during build and publish, using the [poetry-dynamic-versioning](https://github.com/mtkennerly/poetry-dynamic-versioning) plugin.

## Coverage

To run a coverage report, run:

```console
poetry run poe coverage-html
```

This will generate a coverage report in the `htmlcov` folder.

Note: If you have pre-installed [Poe](https://poethepoet.natn.io/index.html)
(`pipx install poethepoet`), then you can omit the `poetry run` prefix.

## Versioning

Versioning follows [Semantic Versioning](https://semver.org/). For new features, bump the minor version. For bug fixes, bump the patch version. For pre-releases, append `dev.N` to the version. For example, `0.1.0dev.1` is the first pre-release of the `0.1.0` version.
