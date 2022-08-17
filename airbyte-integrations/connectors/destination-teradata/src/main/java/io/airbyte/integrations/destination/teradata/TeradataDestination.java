/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.Collections;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import io.airbyte.integrations.destination.ExtendedNameTransformer;

public class TeradataDestination extends AbstractJdbcDestination  implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(TeradataDestination.class);
  public static final String DRIVER_CLASS = "com.teradata.jdbc.TeraDriver";
  public static final String DATABASE_KEY = "database";
  public static final String JDBC_URL_KEY = "jdbc_url";
  public static final String JDBC_URL_PARAMS_KEY = "jdbc_url_params";
  public static final String PASSWORD_KEY = "password";
  public static final String USERNAME_KEY = "username";
  public static final String SCHEMA_KEY = "schema";


  public static void main(String[] args) throws Exception {
    new IntegrationRunner(new TeradataDestination()).run(args);
  }

  public TeradataDestination() {
    super(DRIVER_CLASS, new ExtendedNameTransformer(), new TeradataSqlOperations());
  }

  @Override
  protected Map<String, String> getDefaultConnectionProperties(final JsonNode config) {   
      return Collections.emptyMap();
  }
  @Override
  public JsonNode toJdbcConfig(final JsonNode config) {
    final String schema = Optional.ofNullable(config.get("schema")).map(JsonNode::asText).orElse("public");

    final String jdbcUrl = String.format("jdbc:teradata://%s?",
        config.get("host").asText());

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(USERNAME_KEY, config.get(USERNAME_KEY).asText())
        .put(JDBC_URL_KEY, jdbcUrl)
        .put(SCHEMA_KEY, schema);

    if (config.has(PASSWORD_KEY)) {
      configBuilder.put(PASSWORD_KEY, config.get(PASSWORD_KEY).asText());
    }

    if (config.has(JDBC_URL_PARAMS_KEY)) {
      configBuilder.put(JDBC_URL_PARAMS_KEY, config.get(JDBC_URL_PARAMS_KEY).asText());
    }

    return Jsons.jsonNode(configBuilder.build());
  }
}
