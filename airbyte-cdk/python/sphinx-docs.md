# Sphinx Docs

We're using the [Sphinx](https://www.sphinx-doc.org/) library in order
to automatically generate the docs for the [airbyte-cdk](https://pypi.org/project/airbyte-cdk/).

## Updating the docs structure (manually)

Documentation structure is set in `airbyte-cdk/python/reference_docs/_source`, using the `.rst` files.

See [reStructuredText docs](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
for the key concepts.

Note that `index.rst` is the main index file, where we do define the layout of the main
docs page and relation to other sections.

Each time a new module added to `airbyte-cdk/python/airbyte_cdk` module you'll need to update the Sphinx rst schema.

Let's dive into using an example:

- Assuming we're going to add a new package `airbyte_cdk/new_package`;
- Let this file contain a few modules: `airbyte_cdk/new_package/module1.py` and `airbyte_cdk/new_package/module2.py`;
- The above structure should be in `rst` config as:
  - Add this block directly into `index.rst`:

    ```
    .. toctree::
      :maxdepth: 2
      :caption: New Package

    api/airbyte_cdk.new_package
    ```

  - Add a new file `api/airbyte_cdk.new_package.rst` with the following content:

    ```
    Submodules
    ----------

    airbyte\_cdk.new\_package.module1 module
    --------------------------------------------

    .. automodule:: airbyte_cdk.new_package.module1
       :members:
       :undoc-members:
       :show-inheritance:

    .. automodule:: airbyte_cdk.new_package.module2
       :members:
       :undoc-members:
       :show-inheritance:

    Module contents
    ---------------

    .. automodule:: airbyte_cdk.models
       :members:
       :undoc-members:
       :show-inheritance:
    ```

For more examples see `airbyte-cdk/python/reference_docs/_source`
and read the [docs](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html).

## Updating the docs structure (automatically)

It's also possible to generate `.rst` files automatically using `generate_rst_schema.py` script.

You should also update this script in order to change the docs appearance or structure.

To generate the docs,
run `python generate_rst_schema.py -o _source/api ../../python/airbyte_cdk -f -t _source/templates`
from the `airbyte-cdk/python/reference_docs` root.

## Building the docs locally

After the `rst` files created to correctly represent current project structure you may build the docs locally.
This build could be useful on each `airbyte-cdk` update, especially if the package structure was changed.

- Install Sphinx deps with `pip install ".[sphinx-docs]"`;
- Run `make html` from the `airbyte-cdk/python/reference_docs` root;
- Check out the `airbyte-cdk/python/reference_docs/_build` for the new documentation built.

## Publishing to Read the Docs

Our current sphinx docs setup is meant to be published to [readthedocs](https://readthedocs.org/).
So it may be useful to check our docs published at https://airbyte-cdk.readthedocs.io/en/latest/
for the last build in case if the airbyte-cdk package was updated.

Publishing process is automatic and implemented via the GitHub incoming webhook.
See https://docs.readthedocs.io/en/stable/webhooks.html.

To check build logs and state, check the https://readthedocs.org/projects/airbyte-cdk/builds/.
You may also run build manually here if needed.

Publishing configuration is placed to `.readthedocs.yaml`.
See https://docs.readthedocs.io/en/stable/config-file/v2.html for the config description.
