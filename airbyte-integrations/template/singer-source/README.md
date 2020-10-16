# Quick & Dirty manual

Prepare development environment:
```
cd airbyte-integrations/template/singer-source

# create & activate virtualenv
virtualenv build/venv
source build/venv/bin/activate

# install necessary dependencies
pip install -r requirements.txt
```

Test locally:
```
python main_dev.py spec
python main_dev.py check --config sample_files/test_config.json
python main_dev.py discover --config sample_files/test_config.json
python main_dev.py read --config sample_files/test_config.json --catalog sample_files/test_catalog.json
```

Test image:
```
# in airbyte root directory
./gradlew :airbyte-integrations:template:singer-source:buildImage
docker run --rm -v $(pwd)/airbyte-integrations/template/singer-source/sample_files:/sample_files airbyte/source-template-python:dev spec
docker run --rm -v $(pwd)/airbyte-integrations/template/singer-source/sample_files:/sample_files airbyte/source-template-python:dev check --config /sample_files/test_config.json
docker run --rm -v $(pwd)/airbyte-integrations/template/singer-source/sample_files:/sample_files airbyte/source-template-python:dev discover --config /sample_files/test_config.json
docker run --rm -v $(pwd)/airbyte-integrations/template/singer-source/sample_files:/sample_files airbyte/source-template-python:dev read --config /sample_files/test_config.json --catalog /sample_files/test_catalog.json
```

