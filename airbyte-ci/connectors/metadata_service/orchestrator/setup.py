# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['orchestrator',
 'orchestrator.assets',
 'orchestrator.jobs',
 'orchestrator.models',
 'orchestrator.resources',
 'orchestrator.resources.file_managers',
 'orchestrator.sensors',
 'orchestrator.templates',
 'orchestrator.utils']

package_data = \
{'': ['*']}

install_requires = \
['dagit>=1.1.21,<2.0.0',
 'dagster-cloud>=1.2.6,<2.0.0',
 'dagster-gcp>=0.18.6,<0.19.0',
 'dagster>=1.1.21,<2.0.0',
 'deepdiff>=6.3.0,<7.0.0',
 'google>=3.0.0,<4.0.0',
 'grpcio>=1.47.0,<2.0.0',
 'jinja2>=3.1.2,<4.0.0',
 'mergedeep>=1.3.4,<2.0.0',
 'metadata-service @ '
 'file:///Users/ben/Development/repos/airbyte/airbyte-ci/connectors/metadata_service/lib',
 'pandas>=1.5.3,<2.0.0',
 'pydash>=6.0.2,<7.0.0',
 'pygithub>=1.58.0,<2.0.0']

setup_kwargs = {
    'name': 'orchestrator',
    'version': '0.1.0',
    'description': '',
    'long_description': "# Connector Orchestrator (WIP)\nThis is the Orchestrator for Airbyte metadata built on Dagster.\n\n\n# Setup\n\n## Prerequisites\n\n#### Poetry\n\nBefore you can start working on this project, you will need to have Poetry installed on your system. Please follow the instructions below to install Poetry:\n\n1. Open your terminal or command prompt.\n2. Install Poetry using the recommended installation method:\n\n```bash\ncurl -sSL https://install.python-poetry.org | python3 -\n```\n\nAlternatively, you can use `pip` to install Poetry:\n\n```bash\npip install --user poetry\n```\n\n3. After the installation is complete, close and reopen your terminal to ensure the newly installed `poetry` command is available in your system's PATH.\n\nFor more detailed instructions and alternative installation methods, please refer to the official Poetry documentation: https://python-poetry.org/docs/#installation\n\n### Using Poetry in the Project\n\nOnce Poetry is installed, you can use it to manage the project's dependencies and virtual environment. To get started, navigate to the project's root directory in your terminal and follow these steps:\n\n\n## Installation\n```bash\npoetry install\ncp .env.template .env\n```\n\n## Create a GCP Service Account and Dev Bucket\nDeveloping against the orchestrator requires a development bucket in GCP.\n\nThe orchestrator will use this bucket to:\n- store important output files. (e.g. Reports)\n- watch for changes to the `catalog` directory in the bucket.\n\nHowever all tmp files will be stored in a local directory.\n\nTo create a development bucket:\n1. Create a GCP Service Account with the following permissions:\n    - Storage Admin\n    - Storage Object Admin\n    - Storage Object Creator\n    - Storage Object Viewer\n2. Create a GCS bucket\n3. Add the service account as a member of the bucket with the following permissions:\n    - Storage Admin\n    - Storage Object Admin\n    - Storage Object Creator\n    - Storage Object Viewer\n4. Add the following environment variables to your `.env` file:\n    - `METADATA_BUCKET`\n    - `GCS_CREDENTIALS`\n\nNote that the `GCS_CREDENTIALS` should be the raw json string of the service account credentials.\n\nHere is an example of how to import the service account credentials into your environment:\n```bash\nexport GCS_CREDENTIALS=`cat /path/to/credentials.json`\n```\n\n## The Orchestrator\n\nThe orchestrator (built using Dagster) is responsible for orchestrating various the metadata processes.\n\nDagster has a number of concepts that are important to understand before working on the orchestrator.\n1. Assets\n2. Resources\n3. Schedules\n4. Sensors\n5. Ops\n\nRefer to the [Dagster documentation](https://docs.dagster.io/concepts) for more information on these concepts.\n\n### Starting the Dagster Daemons\nStart the orchestrator with the following command:\n```bash\npoetry run dagster dev -m orchestrator\n```\n\nThen you can access the Dagster UI at http://localhost:3000\n\nNote its important to use `dagster dev` instead of `dagit` because `dagster dev` start additional services that are required for the orchestrator to run. Namely the sensor service.\n\n### Materializing Assets with the UI\nWhen you navigate to the orchestrator in the UI, you will see a list of assets that are available to be materialized.\n\nFrom here you have the following options\n1. Materialize all assets\n2. Select a subset of assets to materialize\n3. Enable a sensor to automatically materialize assets\n\n### Materializing Assets without the UI\n\nIn some cases you may want to run the orchestrator without the UI. To learn more about Dagster's CLI commands, see the [Dagster CLI documentation](https://docs.dagster.io/_apidocs/cli).\n\n## Running Tests\n```bash\npoetry run pytest\n```\n\n",
    'author': 'Ben Church',
    'author_email': 'ben@airbyte.io',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)

