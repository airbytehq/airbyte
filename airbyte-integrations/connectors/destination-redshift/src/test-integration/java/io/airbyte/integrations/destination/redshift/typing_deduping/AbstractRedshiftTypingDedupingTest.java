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
import java.nio.file.Path;
import java.util.List;
import javax.sql.DataSource;
import org.jooq.impl.DSL;

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
    database = insertDestination.getDatabase(dataSource);
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
    database.execute(
        String.format(
            """
            DROP TABLE IF EXISTS "%s"."%s";
            DROP SCHEMA IF EXISTS "%s" CASCADE
            """,
            getRawSchema(),
            // Raw table is still lowercase.
            StreamId.concatenateRawTableName(streamNamespace, streamName),
            streamNamespace.toUpperCase()));
  }

  @Override
  protected void globalTeardown() throws Exception {
    DataSourceFactory.close(dataSource);
  }

  @Override
  protected SqlGenerator<?> getSqlGenerator() {
    return new RedshiftSqlGenerator(new RedshiftSQLNameTransformer());
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
