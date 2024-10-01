# Clickhouse Strict Encrypt Test Configuration

In order to test the Clickhouse destination, you need to have the up and running Clickhouse database that has SSL enabled.

This connector inherits the Clickhouse source, but support SSL connections only.

# Integration tests

For ssl test custom image is used. To push it run this command under the tools\integration-tests-ssl dir:
_docker build -t your_user/clickhouse-with-ssl:dev -f Clickhouse.Dockerfile ._
