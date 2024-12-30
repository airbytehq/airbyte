# Code formatting

## Tools

### 🐍 Python

We use [Ruff](https://docs.astral.sh) for Python code formatting and import sorting. Our Ruff configuration is in the [pyproject.toml](https://github.com/airbytehq/airbyte/blob/master/pyproject.toml) file.

Ruff is monorepo-friendly and supports nested inherited configuration; each sub-project can optionally override Ruff lint and formatting settings in their own `pyproject.toml` files, as needed per project.

Ruff [auto-detects the proper package classification](https://docs.astral.sh/ruff/faq/#how-does-ruff-determine-which-of-my-imports-are-first-party-third-party-etc) so that "local", "first party" and "third party" imports are sorted and grouped correctly, even within subprojects of the monorepo.

### ☕ Java

We format our Java code using [Spotless](https://github.com/diffplug/spotless).
Our configuration for Spotless is in the [spotless-maven-pom.xml](https://github.com/airbytehq/airbyte/blob/master/spotless-maven-pom.xml) file.

### Json and Yaml

We format our Json and Yaml files using [prettier](https://prettier.io/).

### Local Formatting


We wrapped our code formatting tools in [pre-commit](https://pre-commit.com). You can install this and other local dev tools by running `make tools.install`.

You can execute `pre-commit` to format modified files, or `pre-commit run --all-files` to format all the code your local `airbyte` repository.

## Pre-push Git Hooks

A pre-push git hook is available, which you can enable with:

```bash
make tools.git-hooks.install
```

You can also uninstall git hooks with:

```bash
make tools.git-hooks.clean
```

### CI Checks and `/format-fix` Slash Command

In the CI we run the `pre-commit run --all-files` command to check that all the code is formatted.
If it is not, CI will fail and you will have to run `pre-commit run --all-files` locally to fix the formatting issues. Alternatively, maintainers with write permissions can run the `/format-fix` GitHub slash command to auto-format the entire repo and commit the result back to the open PR.
