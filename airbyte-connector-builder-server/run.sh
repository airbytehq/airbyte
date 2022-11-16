# /tmp should be a parameter
cd /tmp
pip install -e .
pip install -e '.[main]'
pip install -e '.[tests]'
#python -m coverage run -m pytest unit_tests -c pytest.ini
#python -m coverage run -m pytest integration_tests -c pytest.ini
pip install 'mccabe==0.6.1'
pip install 'flake8==4.0.1'
pip install 'pyproject-flake8==0.0.1a2'
pip install 'black==22.3.0'
pip install 'mypy==0.930'
pip install 'isort==5.6.4'
pip install 'pytest==6.1.2'
pip install 'coverage[toml]==6.3.1'
python -m isort --settings-file=pyproject.toml ./
python -m isort --settings-file=pyproject.toml --diff --quiet ./
python -m black --config pyproject.toml ./
python -m black --config pyproject.toml ./ --diff --quiet
#python -m pflake8 ./
#python -m pflake8 ./ --diff --quiet