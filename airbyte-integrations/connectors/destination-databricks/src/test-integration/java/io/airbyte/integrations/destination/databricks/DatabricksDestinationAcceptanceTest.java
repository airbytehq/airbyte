/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import static org.jooq.impl.DSL.asterisk;
import static org.jooq.impl.DSL.field;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopierFactory;
import io.airbyte.integrations.destination.s3.avro.JsonFieldNameUpdater;
import io.airbyte.integrations.destination.s3.util.AvroRecordHelper;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.sql.SQLException;
import java.util.List;
import java.util.stream.Collectors;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class DatabricksDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(DatabricksDestinationAcceptanceTest.class);

  private final ExtendedNameTransformer nameTransformer = new DatabricksNameTransformer();
  protected JsonNode configJson;
  protected DatabricksDestinationConfig databricksConfig;

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
    final String tableName = nameTransformer.getIdentifier(streamName);
    final String schemaName = StreamCopierFactory.getSchema(namespace, databricksConfig.getDatabaseSchema(), nameTransformer);
    final JsonFieldNameUpdater nameUpdater = AvroRecordHelper.getFieldNameUpdater(streamName, namespace, streamSchema);

    try (final DSLContext dslContext = getDslContext(databricksConfig)) {
      final Database database = new Database(dslContext);
      return database.query(ctx -> ctx.select(asterisk())
          .from(String.format("%s.%s", schemaName, tableName))
          .orderBy(field(JavaBaseConstants.COLUMN_NAME_EMITTED_AT).asc())
          .fetch().stream()
          .map(record -> {
            final JsonNode json = Jsons.deserialize(record.formatJSON(JdbcUtils.getDefaultJSONFormat()));
            final JsonNode jsonWithOriginalFields = nameUpdater.getJsonWithOriginalFieldNames(json);
            return AvroRecordHelper.pruneAirbyteJson(jsonWithOriginalFields);
          })
          .collect(Collectors.toList()));
    }
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws SQLException {
    // clean up database
    LOGGER.info("Dropping database schema {}", databricksConfig.getDatabaseSchema());
    try (final DSLContext dslContext = getDslContext(databricksConfig)) {
      final Database database = new Database(dslContext);
      // we cannot use jooq dropSchemaIfExists method here because there is no proper dialect for
      // Databricks, and it incorrectly quotes the schema name
      database.query(ctx -> ctx.execute(String.format("DROP SCHEMA IF EXISTS %s CASCADE;", databricksConfig.getDatabaseSchema())));
    } catch (final Exception e) {
      throw new SQLException(e);
    }
  }

  protected static DSLContext getDslContext(final DatabricksDestinationConfig databricksConfig) {
    return DSLContextFactory.create(DatabricksConstants.DATABRICKS_USERNAME,
        databricksConfig.getDatabricksPersonalAccessToken(), DatabricksConstants.DATABRICKS_DRIVER_CLASS,
        DatabricksBaseDestination.getDatabricksConnectionString(databricksConfig), SQLDialect.DEFAULT);
  }

}
