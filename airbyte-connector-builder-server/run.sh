cd /tmp
pip install -e .
pip install -e '.[main]'
pip install -e '.[tests]'
#python -m pytest unit_tests
python -m coverage run -m pytest unit_tests -c pytest.ini