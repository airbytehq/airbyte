package io.airbyte.integrations.destination.postgres.typing_deduping;

import static io.airbyte.integrations.destination.postgres.typing_deduping.PostgresSqlGenerator.JSONB_TYPE;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.cdk.integrations.standardtest.destination.typing_deduping.JdbcSqlGeneratorIntegrationTest;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.destination.postgres.PostgresDestination;
import io.airbyte.integrations.destination.postgres.PostgresSQLNameTransformer;
import io.airbyte.integrations.destination.postgres.PostgresTestDatabase;
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
        .withResolvedHostAndPort()
        .withCredentials()
        .withoutSsl()
        .build();

    databaseName = config.get(JdbcUtils.DATABASE_KEY).asText();
    final PostgresDestination postgresDestination = new PostgresDestination();
    final DataSource dataSource = postgresDestination.getDataSource(config);
    database = postgresDestination.getDatabase(dataSource);
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
    // TODO
  }
}
