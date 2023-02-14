set -e

cd $1

# Fail script on failing command
set -e

# Install dependencies
pip install -r requirements-tests.txt

# Run the tests
python -m coverage run -m pytest -p no:logging --disable-warnings unit_tests -c pytest.ini
python -m coverage run -m pytest -p no:logging --disable-warnings integration_tests -c pytest.ini
