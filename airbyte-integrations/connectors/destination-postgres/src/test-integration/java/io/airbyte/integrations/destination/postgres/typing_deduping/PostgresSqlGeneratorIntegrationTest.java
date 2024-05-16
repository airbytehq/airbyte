/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.typing_deduping;

import static io.airbyte.integrations.destination.postgres.typing_deduping.PostgresSqlGenerator.JSONB_TYPE;
import static org.jooq.impl.DSL.createView;
import static org.jooq.impl.DSL.quotedName;
import static org.jooq.impl.DSL.select;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.cdk.integrations.standardtest.destination.typing_deduping.JdbcSqlGeneratorIntegrationTest;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus;
import io.airbyte.integrations.base.destination.typing_deduping.Sql;
import io.airbyte.integrations.destination.postgres.PostgresDestination;
import io.airbyte.integrations.destination.postgres.PostgresSQLNameTransformer;
import io.airbyte.integrations.destination.postgres.PostgresTestDatabase;
import java.util.List;
import javax.sql.DataSource;
import org.jooq.DataType;
import org.jooq.Field;
import org.jooq.SQLDialect;
import org.jooq.conf.ParamType;
import org.jooq.impl.DSL;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

public class PostgresSqlGeneratorIntegrationTest extends JdbcSqlGeneratorIntegrationTest<PostgresState> {

  private static PostgresTestDatabase testContainer;
  private static String databaseName;
  private static JdbcDatabase database;

  @Override
  protected boolean getSupportsSafeCast() {
    return true;
  }

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
    return new PostgresSqlGenerator(new PostgresSQLNameTransformer(), false);
  }

  @Override
  protected DestinationHandler<PostgresState> getDestinationHandler() {
    return new PostgresDestinationHandler(databaseName, database, getNamespace());
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
    final Sql sql = getGenerator().createTable(getIncrementalDedupStream(), "", false);
    getDestinationHandler().execute(sql);

    List<DestinationInitialStatus<PostgresState>> initialStatuses = getDestinationHandler().gatherInitialState(List.of(getIncrementalDedupStream()));
    assertEquals(1, initialStatuses.size());
    final DestinationInitialStatus<PostgresState> initialStatus = initialStatuses.getFirst();
    assertTrue(initialStatus.isFinalTablePresent());
    assertFalse(initialStatus.isSchemaMismatch());
  }

  /**
   * Verify that we correctly DROP...CASCADE the final table when cascadeDrop is enabled.
   */
  @Test
  public void testCascadeDrop() throws Exception {
    // Explicitly create a sqlgenerator with cascadeDrop=true
    final PostgresSqlGenerator generator = new PostgresSqlGenerator(new PostgresSQLNameTransformer(), true);
    // Create a table, then create a view referencing it
    getDestinationHandler().execute(generator.createTable(getIncrementalAppendStream(), "", false));
    database.execute(createView(quotedName(getIncrementalAppendStream().getId().getFinalNamespace(), "example_view"))
        .as(select().from(quotedName(getIncrementalAppendStream().getId().getFinalNamespace(), getIncrementalAppendStream().getId().getFinalName())))
        .getSQL(ParamType.INLINED));
    // Create a "soft reset" table
    getDestinationHandler().execute(generator.createTable(getIncrementalDedupStream(), "_soft_reset", false));

    // Overwriting the first table with the second table should succeed.
    assertDoesNotThrow(() -> getDestinationHandler().execute(generator.overwriteFinalTable(getIncrementalDedupStream().getId(), "_soft_reset")));
  }

}
