CURRENT_DIR="$PWD"
DIR=$(basename "$PWD")
echo $DIR
cd $CURRENT_DIR
#docker build --no-cache . -t airbyte/$DIR:dev
cd ~/code/airbyte
#docker build --no-cache . -t airbyte/$DIR:test -f airbyte-integrations/connectors/$DIR/test/Dockerfile
docker build --no-cache . -t airbyte/$DIR:dev -f airbyte-integrations/connectors/$DIR/Dockerfile
cd $CURRENT_DIR
python3 -m pytest integration_tests -p integration_tests.acceptance
