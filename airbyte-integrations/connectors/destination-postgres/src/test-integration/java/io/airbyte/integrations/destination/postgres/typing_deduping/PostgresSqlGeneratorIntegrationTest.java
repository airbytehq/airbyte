/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.typing_deduping;

import static io.airbyte.integrations.destination.postgres.typing_deduping.PostgresSqlGenerator.JSONB_TYPE;
import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.cdk.integrations.standardtest.destination.typing_deduping.JdbcSqlGeneratorIntegrationTest;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.Sql;
import io.airbyte.integrations.destination.postgres.PostgresDestination;
import io.airbyte.integrations.destination.postgres.PostgresSQLNameTransformer;
import io.airbyte.integrations.destination.postgres.PostgresTestDatabase;
import java.util.Optional;
import javax.sql.DataSource;
import org.jooq.DataType;
import org.jooq.Field;
import org.jooq.SQLDialect;
import org.jooq.impl.DSL;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

public class PostgresSqlGeneratorIntegrationTest extends JdbcSqlGeneratorIntegrationTest {

  private static PostgresTestDatabase testContainer;
  private static String databaseName;
  private static JdbcDatabase database;

  @BeforeAll
  public static void setupPostgres() {
    testContainer = PostgresTestDatabase.in(PostgresTestDatabase.BaseImage.POSTGRES_13);
    final JsonNode config = testContainer.configBuilder()
        .with("schema", "public")
        .withDatabase()
        .withHostAndPort()
        .withCredentials()
        .withoutSsl()
        .build();

    databaseName = config.get(JdbcUtils.DATABASE_KEY).asText();
    final PostgresDestination postgresDestination = new PostgresDestination();
    final DataSource dataSource = postgresDestination.getDataSource(config);
    database = new DefaultJdbcDatabase(dataSource, new PostgresSourceOperations());
  }

  @AfterAll
  public static void teardownPostgres() {
    testContainer.close();
  }

  @Override
  protected JdbcDatabase getDatabase() {
    return database;
  }

  @Override
  protected DataType<?> getStructType() {
    return JSONB_TYPE;
  }

  @Override
  protected JdbcSqlGenerator getSqlGenerator() {
    return new PostgresSqlGenerator(new PostgresSQLNameTransformer());
  }

  @Override
  protected DestinationHandler<TableDefinition> getDestinationHandler() {
    return new JdbcDestinationHandler(databaseName, database);
  }

  @Override
  protected SQLDialect getSqlDialect() {
    return SQLDialect.POSTGRES;
  }

  @Override
  protected Field<?> toJsonValue(final String valueAsString) {
    return DSL.cast(DSL.val(valueAsString), JSONB_TYPE);
  }

  @Test
  @Override
  public void testCreateTableIncremental() throws Exception {
    final Sql sql = generator.createTable(incrementalDedupStream, "", false);
    destinationHandler.execute(sql);

    final Optional<TableDefinition> existingTable = destinationHandler.findExistingTable(incrementalDedupStream.id());

    assertTrue(existingTable.isPresent());
    assertAll(
        () -> assertEquals("varchar", existingTable.get().columns().get("_airbyte_raw_id").type()),
        () -> assertEquals("timestamptz", existingTable.get().columns().get("_airbyte_extracted_at").type()),
        () -> assertEquals("jsonb", existingTable.get().columns().get("_airbyte_meta").type()),
        () -> assertEquals("int8", existingTable.get().columns().get("id1").type()),
        () -> assertEquals("int8", existingTable.get().columns().get("id2").type()),
        () -> assertEquals("timestamptz", existingTable.get().columns().get("updated_at").type()),
        () -> assertEquals("jsonb", existingTable.get().columns().get("struct").type()),
        () -> assertEquals("jsonb", existingTable.get().columns().get("array").type()),
        () -> assertEquals("varchar", existingTable.get().columns().get("string").type()),
        () -> assertEquals("numeric", existingTable.get().columns().get("number").type()),
        () -> assertEquals("int8", existingTable.get().columns().get("integer").type()),
        () -> assertEquals("bool", existingTable.get().columns().get("boolean").type()),
        () -> assertEquals("timestamptz", existingTable.get().columns().get("timestamp_with_timezone").type()),
        () -> assertEquals("timestamp", existingTable.get().columns().get("timestamp_without_timezone").type()),
        () -> assertEquals("timetz", existingTable.get().columns().get("time_with_timezone").type()),
        () -> assertEquals("time", existingTable.get().columns().get("time_without_timezone").type()),
        () -> assertEquals("date", existingTable.get().columns().get("date").type()),
        () -> assertEquals("jsonb", existingTable.get().columns().get("unknown").type()));
    // TODO assert on table indexing, etc.
  }

}
