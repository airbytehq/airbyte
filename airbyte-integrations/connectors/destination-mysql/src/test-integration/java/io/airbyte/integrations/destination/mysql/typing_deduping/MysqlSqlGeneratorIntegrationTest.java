package io.airbyte.integrations.destination.mysql.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.cdk.integrations.standardtest.destination.typing_deduping.JdbcSqlGeneratorIntegrationTest;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.destination.mysql.MySQLDestination;
import io.airbyte.integrations.destination.mysql.MySQLDestinationAcceptanceTest;
import io.airbyte.integrations.destination.mysql.MySQLNameTransformer;
import java.util.List;
import javax.sql.DataSource;
import org.jooq.DataType;
import org.jooq.Field;
import org.jooq.Name;
import org.jooq.SQLDialect;
import org.jooq.impl.DSL;
import org.jooq.impl.DefaultDataType;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MySQLContainer;

public class MysqlSqlGeneratorIntegrationTest extends JdbcSqlGeneratorIntegrationTest {

  private static MySQLContainer<?> testContainer;
  private static String databaseName;
  private static JdbcDatabase database;

  @BeforeAll
  public static void setupMysql() {
    testContainer = new MySQLContainer<>("mysql:8.0");
    testContainer.start();
    MySQLDestinationAcceptanceTest.configureTestContainer(testContainer);

    final JsonNode config = MySQLDestinationAcceptanceTest.getConfigFromTestContainer(testContainer);

    // TODO move this into JdbcSqlGeneratorIntegrationTest?
    // This code was largely copied from RedshiftSqlGeneratorIntegrationTest
    // TODO: Existing in AbstractJdbcDestination, pull out to a util file
    databaseName = config.get(JdbcUtils.DATABASE_KEY).asText();
    // TODO: Its sad to instantiate unneeded dependency to construct database and datsources. pull it to
    // static methods.
    final MySQLDestination insertDestination = new MySQLDestination();
    final DataSource dataSource = insertDestination.getDataSource(config);
    database = insertDestination.getDatabase(dataSource);
  }

  @AfterAll
  public static void teardownMysql() {
    testContainer.stop();
    testContainer.close();
  }

  @Override
  protected JdbcSqlGenerator getSqlGenerator() {
    return new MysqlSqlGenerator(new MySQLNameTransformer());
  }

  @Override
  protected DestinationHandler<TableDefinition> getDestinationHandler() {
    return new MysqlDestinationHandler(databaseName, database);
  }

  @Test
  @Override
  public void testCreateTableIncremental() throws Exception {
    // TODO
  }

  @Override
  protected JdbcDatabase getDatabase() {
    return database;
  }

  @Override
  protected DataType<?> getStructType() {
    return new DefaultDataType<>(null, String.class, "json");
  }

  @Override
  protected SQLDialect getSqlDialect() {
    return SQLDialect.MYSQL;
  }

  @Override
  protected Field<?> toJsonValue(final String valueAsString) {
    // mysql lets you just insert json strings directly into json columns
    return DSL.val(valueAsString);
  }
}
