/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.standardtest.destination.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.JdbcCompatibleSourceOperations;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.base.destination.typing_deduping.BaseTypingDedupingTest;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import java.util.List;
import javax.sql.DataSource;
import org.jooq.impl.DSL;

/**
 * This class is largely the same as
 * {@link io.airbyte.integrations.destination.snowflake.typing_deduping.AbstractSnowflakeTypingDedupingTest}.
 * But (a) it uses jooq to construct the sql statements, and (b) it doesn't need to upcase anything.
 * At some point we might (?) want to do a refactor to combine them.
 */
public abstract class JdbcTypingDedupingTest extends BaseTypingDedupingTest {

  private JdbcDatabase database;
  private DataSource dataSource;

  /**
   * Get the config as declared in GSM (or directly from the testcontainer). This class will do
   * further modification to the config to ensure test isolation.i
   */
  protected abstract ObjectNode getBaseConfig();

  protected abstract DataSource getDataSource(JsonNode config);

  /**
   * Subclasses may need to return a custom source operations if the default one does not handle
   * vendor-specific types correctly. For example, you most likely need to override this method to
   * deserialize JSON columns to JsonNode.
   */
  protected JdbcCompatibleSourceOperations<?> getSourceOperations() {
    return JdbcUtils.getDefaultSourceOperations();
  }

  /**
   * Subclasses using a config with a nonstandard raw table schema should override this method.
   */
  protected String getRawSchema() {
    return JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE;
  }

  /**
   * Subclasses using a config where the default schema is not in the {@code schema} key should
   * override this method and {@link #setDefaultSchema(JsonNode, String)}.
   */
  protected String getDefaultSchema(final JsonNode config) {
    return config.get("schema").asText();
  }

  /**
   * Subclasses using a config where the default schema is not in the {@code schema} key should
   * override this method and {@link #getDefaultSchema(JsonNode)}.
   */
  protected void setDefaultSchema(final JsonNode config, final String schema) {
    ((ObjectNode) config).put("schema", schema);
  }

  @Override
  protected JsonNode generateConfig() {
    final JsonNode config = getBaseConfig();
    setDefaultSchema(config, "typing_deduping_default_schema" + getUniqueSuffix());
    dataSource = getDataSource(config);
    database = new DefaultJdbcDatabase(dataSource, getSourceOperations());
    return config;
  }

  @Override
  protected List<JsonNode> dumpRawTableRecords(String streamNamespace, final String streamName) throws Exception {
    if (streamNamespace == null) {
      streamNamespace = getDefaultSchema(getConfig());
    }
    final String tableName = StreamId.concatenateRawTableName(streamNamespace, streamName);
    final String schema = getRawSchema();
    return database.queryJsons(DSL.selectFrom(DSL.name(schema, tableName)).getSQL());
  }

  @Override
  protected List<JsonNode> dumpFinalTableRecords(String streamNamespace, final String streamName) throws Exception {
    if (streamNamespace == null) {
      streamNamespace = getDefaultSchema(getConfig());
    }
    return database.queryJsons(DSL.selectFrom(DSL.name(streamNamespace, streamName)).getSQL());
  }

  @Override
  protected void teardownStreamAndNamespace(String streamNamespace, final String streamName) throws Exception {
    if (streamNamespace == null) {
      streamNamespace = getDefaultSchema(getConfig());
    }
    database.execute(DSL.dropTableIfExists(DSL.name(getRawSchema(), StreamId.concatenateRawTableName(streamNamespace, streamName))).getSQL());
    database.execute(DSL.dropSchemaIfExists(DSL.name(streamNamespace)).cascade().getSQL());
  }

  @Override
  protected void globalTeardown() throws Exception {
    DataSourceFactory.close(dataSource);
  }

}
