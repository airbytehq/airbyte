/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import static io.airbyte.integrations.destination.databricks.utils.DatabricksConstants.DATABRICKS_HTTP_PATH_KEY;
import static io.airbyte.integrations.destination.databricks.utils.DatabricksConstants.DATABRICKS_PERSONAL_ACCESS_TOKEN_KEY;
import static io.airbyte.integrations.destination.databricks.utils.DatabricksConstants.DATABRICKS_SERVER_HOSTNAME_KEY;
import static org.jooq.impl.DSL.asterisk;
import static org.jooq.impl.DSL.field;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopierFactory;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.nio.file.Path;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;
import org.jooq.DSLContext;

public class DatabricksManagedTablesDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final String SECRETS_CONFIG_JSON = "secrets/managed_tables_config.json";
  private final StandardNameTransformer nameTransformer = new DatabricksNameTransformer();
  private DatabricksDestinationConfig databricksConfig;
  JsonNode configJson;

  @Override
  protected String getImageName() {
    return "airbyte/destination-databricks:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return configJson;
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws SQLException {
    {
      final String catalogName = databricksConfig.catalog();
      final String tableName = nameTransformer.getRawTableName(streamName);
      final String schemaName = StreamCopierFactory.getSchema(namespace, databricksConfig.schema(), nameTransformer);

      List<JsonNode> result = new ArrayList<>();
      try (final DSLContext dslContext = DatabricksUtilTest.getDslContext(databricksConfig)) {
        final Database database = new Database(dslContext);
        List<JsonNode> query = database.query(ctx -> ctx.select(asterisk())
            .from(String.format("%s.%s.%s", catalogName, schemaName, tableName))
            .orderBy(field(JavaBaseConstants.COLUMN_NAME_EMITTED_AT).asc())
            .fetch().stream()
            .map(record -> Jsons.deserialize(record.get(JavaBaseConstants.COLUMN_NAME_DATA).toString()))
            .collect(Collectors.toList()));
        result.addAll(query);
      }
      return result;
    }
  }

  @Override
  protected JsonNode getFailCheckConfig() throws Exception {
    final JsonNode failCheckJson = Jsons.clone(configJson);
    ((ObjectNode) failCheckJson)
        .put(DATABRICKS_SERVER_HOSTNAME_KEY, "fake_host")
        .put(DATABRICKS_HTTP_PATH_KEY, "fake_http_path")
        .put(DATABRICKS_PERSONAL_ACCESS_TOKEN_KEY, "fake_token");
    return failCheckJson;
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) throws Exception {
    this.configJson = Jsons.deserialize(IOs.readFile(Path.of(SECRETS_CONFIG_JSON)));
    this.databricksConfig = DatabricksDestinationConfig.get(configJson);
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws SQLException {
    DatabricksUtilTest.cleanUpData(databricksConfig);
  }

}
