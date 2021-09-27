/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeSource extends AbstractJdbcSource implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeSource.class);
  public static final String DRIVER_CLASS = "net.snowflake.client.jdbc.SnowflakeDriver";

  public SnowflakeSource() {
    super(DRIVER_CLASS, new SnowflakeJdbcStreamingQueryConfiguration());
  }

  public static void main(String[] args) throws Exception {
    final Source source = new SnowflakeSource();
    LOGGER.info("starting source: {}", SnowflakeSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", SnowflakeSource.class);
  }

  @Override
  public JsonNode toDatabaseConfig(JsonNode config) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("jdbc_url", String.format("jdbc:snowflake://%s/",
            config.get("host").asText()))
        .put("host", config.get("host").asText())
        .put("username", config.get("username").asText())
        .put("password", config.get("password").asText())
        .put("connection_properties", String.format("role=%s;warehouse=%s;database=%s;schema=%s",
            config.get("role").asText(),
            config.get("warehouse").asText(),
            config.get("database").asText(),
            config.get("schema").asText()))
        .build());
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Set.of(
        "INFORMATION_SCHEMA");
  }

}
