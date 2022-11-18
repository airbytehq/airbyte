cd $1

# Install dependencies
pip install -e .
pip install -e '.[main]'
pip install -e '.[tests]'

# Run the tests
python -m coverage run -m pytest unit_tests -c pytest.ini
python -m coverage run -m pytest integration_tests -c pytest.ini
