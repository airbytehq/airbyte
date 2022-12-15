# SonarQube workflow

## Goals
&nbsp;The Airbyte monorepo receives contributions from a lot of developers, and there is no way around human errors while merging PRs.
Likely every language has different tools for testing and validation of source files. And while it's best practice to lint and validate code before pushing to git branches, it doesn't always happen.
But it is optional, and as rule as we detect possible problems after launch test/publish commands only. Therefore, using of automated CI code validation can  provided the following benefits:
* Problem/vulnerability reports available when the PR was created. And developers would fix bugs and remove smells before code reviews.
* Reviewers would be sure all standard checks were made and code changes satisfy the requirements.
* Set of tools and their options can be changed anytime globally.
* Progress of code changes are saved in SonarQube and this information helps to analyse quality of the product  integrally and also its separate parts.


## UML diagram 
![image](https://user-images.githubusercontent.com/11213273/149561440-0aceaa30-8f82-4e5b-9ee5-77bdcfd87695.png)


## Used tools
### Python
* [flake8](https://flake8.pycqa.org/en/stable/)
* [mypy](https://mypy.readthedocs.io/en/stable/)
* [isort](https://pycqa.github.io/isort/)
* [black](https://black.readthedocs.io/en/stable/)
* [coverage](https://coverage.readthedocs.io/en/6.2/)

All Python tools use the common [pyproject.toml](https://github.com/airbytehq/airbyte/blob/master/pyproject.toml) file.

### Common tools
* [SonarQube Scanner](https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/)

## Access to SonarQube
The Airbyte project uses a custom SonarQube instance. Access to it is explained [here](https://github.com/airbytehq/airbyte-cloud/wiki/IAP-tunnel-to-the-SonarQube-instance).

## SonarQube settings
The SonarQube server uses default settings. All customisations are implemented into the Github WorkFlows. More details are [here](https://github.com/airbytehq/airbyte/tree/master/.github/actions/ci-tests-runner/action.yml)