/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.OracleJdbcStreamingQueryConfiguration;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.ssh.SshWrappedSource;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.relationaldb.TableInfo;
import io.airbyte.protocol.models.CommonField;
import java.sql.JDBCType;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class OracleSource extends AbstractJdbcSource implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(OracleSource.class);

  static final String DRIVER_CLASS = "oracle.jdbc.OracleDriver";

  private List<String> schemas;

  public OracleSource() {
    super(DRIVER_CLASS, new OracleJdbcStreamingQueryConfiguration());
  }

  @Override
  public JsonNode toDatabaseConfig(JsonNode config) {
    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put("username", config.get("username").asText())
        .put("jdbc_url", String.format("jdbc:oracle:thin:@//%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("sid").asText()));

    if (config.has("password")) {
      configBuilder.put("password", config.get("password").asText());
    }

    // Use the upper-cased username by default.
    schemas = List.of(config.get("username").asText().toUpperCase(Locale.ROOT));
    if (config.has("schemas") && config.get("schemas").isArray()) {
      schemas = new ArrayList<>();
      for (final JsonNode schema : config.get("schemas")) {
        schemas.add(schema.asText());
      }
    }

    return Jsons.jsonNode(configBuilder.build());
  }

  @Override
  public List<TableInfo<CommonField<JDBCType>>> discoverInternal(JdbcDatabase database) throws Exception {
    List<TableInfo<CommonField<JDBCType>>> internals = new ArrayList<>();
    for (String schema : schemas) {
      LOGGER.debug("Discovering schema: {}", schema);
      internals.addAll(super.discoverInternal(database, schema));
    }

    for (TableInfo<CommonField<JDBCType>> info : internals) {
      LOGGER.debug("Found table: {}", info.getName());
    }

    return internals;
  }

  /**
   * Since the Oracle connector allows a user to specify schemas, and picks a default schemas
   * otherwise, system tables are never included, and do not need to be excluded by default.
   */
  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Set.of();
  }

  public static void main(String[] args) throws Exception {
    final Source source = new SshWrappedSource(new OracleSource(), List.of("host"), List.of("port"));
    LOGGER.info("starting source: {}", OracleSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", OracleSource.class);
  }

}
