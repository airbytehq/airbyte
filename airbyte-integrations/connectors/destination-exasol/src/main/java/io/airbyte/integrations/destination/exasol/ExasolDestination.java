/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.exasol;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Collections;
import java.util.Map;
import java.util.function.Consumer;

public class ExasolDestination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(ExasolDestination.class);

  public static final String DRIVER_CLASS = "com.exasol.jdbc.EXADriver";

  public ExasolDestination() {
    super(DRIVER_CLASS, null, null);
  }


  public static void main(String[] args) throws Exception {
    new IntegrationRunner(new ExasolDestination()).run(args);
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    // TODO
    return null;
  }

  @Override
  public JsonNode toJdbcConfig(final JsonNode config) {

    final StringBuilder jdbcUrl = new StringBuilder(
            String.format("jdbc:exa:%s",
                    config.get("connectionstring").asText())
    );

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


  @Override
  public AirbyteMessageConsumer getConsumer(JsonNode config,
                                            ConfiguredAirbyteCatalog configuredCatalog,
                                            Consumer<AirbyteMessage> outputRecordCollector) {
    // TODO
    return null;
  }

  @Override
  protected Map<String, String> getDefaultConnectionProperties(final JsonNode config) {
    return Collections.emptyMap();
  }

}
