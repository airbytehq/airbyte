set -e

cd $1

# Fail script on failing command
set -e

# Install dependencies
pip install -e .
pip install -e '.[main]'
pip install -e '.[tests]'

# Run the tests
python -m coverage run -m pytest unit_tests -c pytest.ini
python -m coverage run -m pytest integration_tests -c pytest.ini
