/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.BaseTypingDedupingTest;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.destination.redshift.RedshiftInsertDestination;
import io.airbyte.integrations.destination.redshift.RedshiftSQLNameTransformer;
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftSqlGeneratorIntegrationTest.RedshiftSourceOperations;
import java.nio.file.Path;
import java.util.List;
import javax.sql.DataSource;
import org.jooq.DSLContext;
import org.jooq.conf.Settings;
import org.jooq.impl.DSL;

/**
 * This class is basically the same as
 * {@link io.airbyte.integrations.destination.snowflake.typing_deduping.AbstractSnowflakeTypingDedupingTest}.
 * But (a) it uses jooq to construct the sql statements, and (b) it doesn't need to upcase anything.
 * At some point we might (?) want to do a refactor to combine them. At the very least, this class
 * is probably useful for other JDBC destination implementations.
 */
public abstract class AbstractRedshiftTypingDedupingTest extends BaseTypingDedupingTest {

  private JdbcDatabase database;
  private DataSource dataSource;

  protected abstract String getConfigPath();

  @Override
  protected String getImageName() {
    return "airbyte/destination-redshift:dev";
  }

  @Override
  protected JsonNode generateConfig() {
    final JsonNode config = Jsons.deserialize(IOs.readFile(Path.of(getConfigPath())));
    ((ObjectNode) config).put("schema", "typing_deduping_default_schema" + getUniqueSuffix());
    final RedshiftInsertDestination insertDestination = new RedshiftInsertDestination();
    dataSource = insertDestination.getDataSource(config);
    database = insertDestination.getDatabase(dataSource, new RedshiftSourceOperations());
    return config;
  }

  @Override
  protected List<JsonNode> dumpRawTableRecords(String streamNamespace, final String streamName) throws Exception {
    if (streamNamespace == null) {
      streamNamespace = getDefaultSchema();
    }
    final String tableName = StreamId.concatenateRawTableName(streamNamespace, streamName);
    final String schema = getRawSchema();
    return database.queryJsons(DSL.selectFrom(DSL.name(schema, tableName)).getSQL());
  }

  @Override
  protected List<JsonNode> dumpFinalTableRecords(String streamNamespace, final String streamName) throws Exception {
    if (streamNamespace == null) {
      streamNamespace = getDefaultSchema();
    }
    return database.queryJsons(DSL.selectFrom(DSL.name(streamNamespace, streamName)).getSQL());
  }

  @Override
  protected void teardownStreamAndNamespace(String streamNamespace, final String streamName) throws Exception {
    if (streamNamespace == null) {
      streamNamespace = getDefaultSchema();
    }
    database.execute(DSL.dropTableIfExists(DSL.name(getRawSchema(), StreamId.concatenateRawTableName(streamNamespace, streamName))).getSQL());
    database.execute(DSL.dropSchemaIfExists(DSL.name(streamNamespace)).cascade().getSQL());
  }

  @Override
  protected void globalTeardown() throws Exception {
    DataSourceFactory.close(dataSource);
  }

  @Override
  protected SqlGenerator<?> getSqlGenerator() {
    return new RedshiftSqlGenerator(new RedshiftSQLNameTransformer()) {

      // Override only for tests to print formatted SQL. The actual implementation should use unformatted
      // to save bytes.
      @Override
      protected DSLContext getDslContext() {
        return DSL.using(getDialect(), new Settings().withRenderFormatted(true));
      }

    };
  }

  /**
   * Subclasses using a config with a nonstandard raw table schema should override this method.
   */
  protected String getRawSchema() {
    return JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE;
  }

  private String getDefaultSchema() {
    return getConfig().get("schema").asText();
  }

}
