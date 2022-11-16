cd /tmp
pip install -e .
pip install -e '.[main]'
pip install -e '.[tests]'
python -m coverage run -m pytest unit_tests -c pytest.ini
python -m coverage run -m pytest integration_tests -c pytest.ini
