/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bytehouse;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;

import java.util.Collections;
import java.util.List;
import java.util.Map;

import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.sql.DataSource;

public class BytehouseDestination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(BytehouseDestination.class);
  public static final String HTTPS_PROTOCOL = "https";
  public static final String HTTP_PROTOCOL = "http";

  static final List<String> SSL_PARAMETERS = ImmutableList.of("socket_timeout=3000000", "sslmode=NONE");
  static final List<String> DEFAULT_PARAMETERS = ImmutableList.of("socket_timeout=3000000");

  public static final String DRIVER_CLASS = DatabaseDriver.BYTEHOUSE.getDriverClassName();

  public BytehouseDestination() {
    super(DRIVER_CLASS, new BytehouseSQLNameTransformer(), new BytehouseSqlOperations());
  }

  public static void main(String[] args) throws Exception {
    LOGGER.info("starting destination: {}", BytehouseDestination.class);
    new IntegrationRunner(new BytehouseDestination()).run(args);
    LOGGER.info("completed destination: {}", BytehouseDestination.class);
  }

  private void log(Object obj) {
    LOGGER.info(obj.toString(), BytehouseDestination.class);
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    DataSource dataSource;
    try {
      dataSource = getDataSource(config);
    } catch (Exception e) {
      return new AirbyteConnectionStatus()
              .withStatus(AirbyteConnectionStatus.Status.FAILED)
              .withMessage("Could not getDataSource: " + e.getMessage());
    }
    try {
      final JdbcDatabase database = getDatabase(dataSource);
      final NamingConventionTransformer namingResolver = getNamingResolver();
      final String outputSchema = namingResolver.getIdentifier(config.get(JdbcUtils.DATABASE_KEY).asText());
      attemptTableOperations(outputSchema, database, namingResolver, getSqlOperations(), true);
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
    } catch (final Exception e) {
      return new AirbyteConnectionStatus()
              .withStatus(AirbyteConnectionStatus.Status.FAILED)
              .withMessage("Could not connect with provided configuration. \n" + e.getMessage());
    } finally {
      try {
        DataSourceFactory.close(dataSource);
      } catch (final Exception e) {
        LOGGER.warn("Unable to close data source.", e);
      }
    }
  }

  @Override
  protected Map<String, String> getDefaultConnectionProperties(JsonNode config) {
    return Collections.emptyMap();
  }

  @Override
  public JsonNode toJdbcConfig(JsonNode config) {
//    final boolean isSsl = JdbcUtils.useSsl(config);
//    final String jdbcUrl = DatabaseDriver.BYTEHOUSE.getUrlFormatString();

    final StringBuilder jdbcUrl = new StringBuilder(
            String.format(DatabaseDriver.BYTEHOUSE.getUrlFormatString(),
                    config.get(JdbcUtils.HOST_KEY).asText(),
                    config.get(JdbcUtils.PORT_KEY).asInt()
            ));

//    LOGGER.info("url: " + jdbcUrl);

//    if (isSsl) {
//      jdbcUrl.append("?").append(String.join("&", SSL_PARAMETERS));
//    } else {
//      jdbcUrl.append("?").append(String.join("&", DEFAULT_PARAMETERS));
//    }

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
            .put(JdbcUtils.USERNAME_KEY, config.get(JdbcUtils.USERNAME_KEY).asText())
            .put(JdbcUtils.JDBC_URL_KEY, jdbcUrl);

    if (config.has(JdbcUtils.PASSWORD_KEY)) {
      configBuilder.put(JdbcUtils.PASSWORD_KEY, config.get(JdbcUtils.PASSWORD_KEY).asText());
    }

    if (config.has(JdbcUtils.JDBC_URL_PARAMS_KEY)) {
      configBuilder.put(JdbcUtils.JDBC_URL_PARAMS_KEY, config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText());
    }

    return Jsons.jsonNode(configBuilder.build());
  }

//  @Override
//  public AirbyteMessageConsumer getConsumer(JsonNode config, io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog catalog, Consumer<io.airbyte.protocol.models.v0.AirbyteMessage> outputRecordCollector) {
//    //TODO
//    return null;
//  }

}
