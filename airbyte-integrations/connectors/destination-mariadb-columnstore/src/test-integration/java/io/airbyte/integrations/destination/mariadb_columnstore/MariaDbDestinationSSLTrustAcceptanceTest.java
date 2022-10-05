package io.airbyte.integrations.destination.mariadb_columnstore;

import static io.airbyte.integrations.destination.mariadb_columnstore.MariaDbColumnstoreSslUtils.CONNECTION_PARAM_SSL_MODE;
import static io.airbyte.integrations.destination.mariadb_columnstore.MariaDbColumnstoreSslUtils.PARAM_MODE;
import static io.airbyte.integrations.destination.mariadb_columnstore.MariaDbColumnstoreSslUtils.PARAM_SSL_MODE;
import static io.airbyte.integrations.destination.mariadb_columnstore.MariaDbColumnstoreSslUtils.TRUST;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import java.util.Map;

public class MariaDbDestinationSSLTrustAcceptanceTest extends AbstractMariaDbDestinationSSLAcceptanceTest {

  @Override
  protected String getSslMode() {
    return TRUST;
  }

  @Override
  protected JsonNode getConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, db.getHost())
        .put(JdbcUtils.PORT_KEY, getContainerPortById(db.getContainerId()))
        .put(JdbcUtils.DATABASE_KEY, db.getDatabaseName())
        .put(JdbcUtils.USERNAME_KEY, db.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, db.getPassword())
        .put(PARAM_SSL_MODE, ImmutableMap.builder()
            .put(PARAM_MODE, getSslMode()).build())
        .build());
  }

  @Override
  protected JdbcDatabase getDatabase(final JsonNode config) {
    return new DefaultJdbcDatabase(
        DataSourceFactory.create(
            config.get(JdbcUtils.USERNAME_KEY).asText(),
            config.has(JdbcUtils.PASSWORD_KEY) ? config.get(JdbcUtils.PASSWORD_KEY).asText() : null,
            MariadbColumnstoreDestination.DRIVER_CLASS,
            String.format(DatabaseDriver.MARIADB.getUrlFormatString(),
                config.get(JdbcUtils.HOST_KEY).asText(),
                config.get(JdbcUtils.PORT_KEY).asInt(),
                config.get(JdbcUtils.DATABASE_KEY).asText()),
            Map.of(CONNECTION_PARAM_SSL_MODE, config.get(PARAM_SSL_MODE).get(PARAM_MODE).asText())));
  }
}
