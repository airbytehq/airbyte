python main.py spec;
python main.py check --config secrets/config.json;
python main.py check --config secrets/config_auto_rk.json;
python main.py discover --config secrets/config.json;
python main.py discover --config secrets/config_auto_rk.json;
python main.py read --config secrets/config.json --catalog sample_files/configured_catalog.json;
python main.py read --config secrets/config_auto_rk.json --catalog sample_files/configured_catalog_auto_rk.json;
