package io.airbyte.integrations.destination.postgres.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.JdbcCompatibleSourceOperations;
import io.airbyte.cdk.integrations.standardtest.destination.typing_deduping.JdbcTypingDedupingTest;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.destination.postgres.PostgresDestination;
import io.airbyte.integrations.destination.postgres.PostgresSQLNameTransformer;
import io.airbyte.integrations.destination.postgres.PostgresTestDatabase;
import javax.sql.DataSource;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;

public class PostgresTypingDedupingTest extends JdbcTypingDedupingTest {
  private static PostgresTestDatabase testContainer;

  @BeforeAll
  public static void setupPostgres() {
    testContainer = PostgresTestDatabase.in(PostgresTestDatabase.BaseImage.POSTGRES_13);
  }

  @AfterAll
  public static void teardownPostgres() {
    testContainer.close();
  }

  @Override
  protected JsonNode getBaseConfig() {
    final ObjectNode config = (ObjectNode) testContainer.configBuilder()
        .with("schema", "public")
        .withDatabase()
        .withResolvedHostAndPort()
        .withCredentials()
        .withoutSsl()
        .build();
    return config.put("use_1s1t_format", true);
  }

  @Override
  protected DataSource getDataSource(final JsonNode config) {
    return new PostgresDestination().getDataSource(config);
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-postgres:dev";
  }

  @Override
  protected SqlGenerator<?> getSqlGenerator() {
    return new PostgresSqlGenerator(new PostgresSQLNameTransformer());
  }

  @Override
  protected JdbcCompatibleSourceOperations<?> getSourceOperations() {
    return new PostgresSqlGeneratorIntegrationTest.PostgresSourceOperations();
  }
}
