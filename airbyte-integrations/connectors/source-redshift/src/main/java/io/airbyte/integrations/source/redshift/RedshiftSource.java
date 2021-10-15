/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.redshift;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RedshiftSource extends AbstractJdbcSource implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftSource.class);
  public static final String DRIVER_CLASS = "com.amazon.redshift.jdbc.Driver";

  // todo (cgardens) - clean up passing the dialect as null versus explicitly adding the case to the
  // constructor.
  public RedshiftSource() {
    super(DRIVER_CLASS, new RedshiftJdbcStreamingQueryConfiguration());
  }

  @Override
  public JsonNode toDatabaseConfig(JsonNode redshiftConfig) {
    List<String> additionalProperties = new ArrayList<>();
    ImmutableMap.Builder<Object, Object> builder = ImmutableMap.builder()
        .put("username", redshiftConfig.get("username").asText())
        .put("password", redshiftConfig.get("password").asText())
        .put("jdbc_url", String.format("jdbc:redshift://%s:%s/%s",
            redshiftConfig.get("host").asText(),
            redshiftConfig.get("port").asText(),
            redshiftConfig.get("database").asText()));
    readSsl(redshiftConfig, additionalProperties);

    if (!additionalProperties.isEmpty()) {
      String connectionParams = String.join(";", additionalProperties);
      builder.put("connection_properties", connectionParams);
    }
    return Jsons.jsonNode(builder
        .build());
  }

  private void readSsl(JsonNode redshiftConfig, List<String> additionalProperties) {
    boolean tls = redshiftConfig.has("tls") && redshiftConfig.get("tls").asBoolean(); // for backward compatibility
    if (!tls) {
      additionalProperties.add("ssl=false");
    } else {
      additionalProperties.add("ssl=true");
      additionalProperties.add("sslfactory=com.amazon.redshift.ssl.NonValidatingFactory");
    }
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Set.of("information_schema", "pg_catalog", "pg_internal", "catalog_history");
  }

  public static void main(String[] args) throws Exception {
    final Source source = new RedshiftSource();
    LOGGER.info("starting source: {}", RedshiftSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", RedshiftSource.class);
  }

}
