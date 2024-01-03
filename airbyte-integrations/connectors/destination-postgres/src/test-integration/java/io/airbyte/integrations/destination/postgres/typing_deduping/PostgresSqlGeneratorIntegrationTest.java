package io.airbyte.integrations.destination.postgres.typing_deduping;

import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.cdk.integrations.standardtest.destination.typing_deduping.JdbcSqlGeneratorIntegrationTest;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import org.jooq.DataType;
import org.jooq.Field;
import org.jooq.SQLDialect;

public class PostgresSqlGeneratorIntegrationTest extends JdbcSqlGeneratorIntegrationTest {
  @Override
  protected JdbcDatabase getDatabase() {
    return null;
  }

  @Override
  protected DataType<?> getStructType() {
    return null;
  }

  @Override
  protected JdbcSqlGenerator getSqlGenerator() {
    return null;
  }

  @Override
  protected DestinationHandler<TableDefinition> getDestinationHandler() {
    return null;
  }

  @Override
  public void testCreateTableIncremental() throws Exception {

  }

  @Override
  protected SQLDialect getSqlDialect() {
    return null;
  }

  @Override
  protected Field<?> toJsonValue(final String valueAsString) {
    return null;
  }
}
