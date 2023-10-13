/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.databricks;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.streaming.NoOpStreamingQueryConfig;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.integrations.source.databricks.utils.DatabricksConstants;
import io.airbyte.integrations.source.databricks.utils.DatabricksDatabaseUtil;
import io.airbyte.cdk.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.cdk.integrations.source.relationaldb.TableInfo;
import io.airbyte.protocol.models.CommonField;
import java.sql.JDBCType;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DatabricksSource extends AbstractJdbcSource<JDBCType> implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(DatabricksSource.class);
  private String schema = null;
  static final String DRIVER_CLASS = DatabricksConstants.DATABRICKS_DRIVER_CLASS;
  private static final int INTERMEDIATE_STATE_EMISSION_FREQUENCY = 10_000;


  public DatabricksSource() {
    super(DRIVER_CLASS, NoOpStreamingQueryConfig::new, new DatabricksSourceOperations());
  }

  // The config is based on spec.json
  @Override
  public JsonNode toDatabaseConfig(final JsonNode config) {
    DatabricksSourceConfig databricksSourceConfig = DatabricksSourceConfig.get(config);
    if (databricksSourceConfig.schema() != null && !databricksSourceConfig.schema().isBlank()){
      schema = databricksSourceConfig.schema();
    }
    final JsonNode configJson = DatabricksDatabaseUtil.buildJdbcConfig(config);
    LOGGER.info(configJson.toString());
    return configJson;
  }

  @Override
  public List<TableInfo<CommonField<JDBCType>>> discoverInternal(final JdbcDatabase database) throws Exception {
    if (schema != null && !schema.isBlank()) {
      // process explicitly selected (from UI) schemas
      final List<TableInfo<CommonField<JDBCType>>> internals = new ArrayList<>();
      internals.addAll(super.discoverInternal(database, schema));

      for (final TableInfo<CommonField<JDBCType>> info : internals) {
        LOGGER.debug("Found table (schema: {}): {}", info.getNameSpace(), info.getName());
      }
      return internals;
    } else {
      LOGGER.info("No schemas explicitly set on UI to process, so will process all of existing schemas in DB");
      return super.discoverInternal(database);
    }
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Set.of("system", "information_schema", "INFORMATION_SCHEMA");
  }

  @Override
  protected int getStateEmissionFrequency() {
    return INTERMEDIATE_STATE_EMISSION_FREQUENCY;
  }

  public static void main(final String[] args) throws Exception {
    final Source source = new DatabricksSource();
    LOGGER.info("starting source: {}", DatabricksSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", DatabricksSource.class);
  }

}
