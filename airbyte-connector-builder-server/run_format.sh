set -e

cd $1

# Fail script on failing command
set -e

# Pasted from https://github.com/airbytehq/airbyte/blob/master/buildSrc/src/main/groovy/airbyte-python.gradle#L85-L96
pip install 'mccabe==0.6.1'
pip install 'flake8==4.0.1'
pip install 'pyproject-flake8==0.0.1a2'
pip install 'black==22.3.0'
pip install 'mypy==0.930'
pip install 'isort==5.6.4'
pip install 'pytest==6.1.2'
pip install 'coverage[toml]==6.3.1'

# Format and static analysis
# FIXME: isort formats python files differently from gradlew format
python -m isort --settings-file=pyproject.toml ./
python -m isort --settings-file=pyproject.toml --diff --quiet ./
python -m black --config pyproject.toml ./
python -m black --config pyproject.toml ./ --diff --quiet
python -m pflake8 --config pyproject.toml ./
python -m pflake8 --config pyproject.toml ./ --diff --quiet
python -m mypy --config pyproject.toml ./
