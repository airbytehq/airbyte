package io.airbyte.db.database;

import static io.airbyte.db.database.AirbyteConfigsTable.AIRBYTE_CONFIGS;
import static io.airbyte.db.database.AirbyteConfigsTable.CONFIG_BLOB;
import static io.airbyte.db.database.AirbyteConfigsTable.CONFIG_ID;
import static io.airbyte.db.database.AirbyteConfigsTable.CONFIG_TYPE;
import static io.airbyte.db.database.AirbyteConfigsTable.CREATED_AT;
import static io.airbyte.db.database.AirbyteConfigsTable.UPDATED_AT;
import static org.jooq.impl.DSL.select;
import static org.junit.jupiter.api.Assertions.assertThrows;

import io.airbyte.db.Database;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.UUID;
import org.jooq.JSONB;
import org.jooq.exception.DataAccessException;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;

class ConfigsDatabaseInstanceTest {

  private static PostgreSQLContainer<?> container;

  @BeforeAll
  public static void dbSetup() {
    container = new PostgreSQLContainer<>("postgres:13-alpine")
        .withDatabaseName("airbyte")
        .withUsername("docker")
        .withPassword("docker");
    container.start();
  }

  @AfterAll
  public static void dbDown() {
    container.close();
  }

  private Database database;

  @BeforeEach
  public void setup() throws Exception {
    database = new ConfigsDatabaseInstance(container.getUsername(), container.getPassword(), container.getJdbcUrl()).getAndInitialize();

    Timestamp timestamp = Timestamp.from(Instant.ofEpochMilli(System.currentTimeMillis()));
    database.transaction(ctx -> ctx.insertInto(AIRBYTE_CONFIGS)
        .set(CONFIG_ID, UUID.randomUUID().toString())
        .set(CONFIG_TYPE, "STANDARD_SOURCE_DEFINITION")
        .set(CONFIG_BLOB, JSONB.valueOf("{}"))
        .set(CREATED_AT, timestamp)
        .set(UPDATED_AT, timestamp)
        .execute());
  }

  @AfterEach
  void tearDown() throws Exception {
    database.close();
  }

  @Test
  public void testGet() throws Exception {
    // when the database has been initialized and loaded with data (in setup method), the get method should return the database
    database = new ConfigsDatabaseInstance(container.getUsername(), container.getPassword(), container.getJdbcUrl()).get();
    // check table
    database.query(ctx -> ctx.fetchExists(select().from(AIRBYTE_CONFIGS)));
  }

  @Test
  public void testGetAndInitialize() throws Exception {
    // check table
    database.query(ctx -> ctx.fetchExists(select().from(AIRBYTE_CONFIGS)));

    // check columns (if any of the column does not exist, the query will throw exception)
    database.query(ctx -> ctx.fetchExists(select().from(AIRBYTE_CONFIGS).where(CONFIG_ID.eq("ID"))));
    database.query(ctx -> ctx.fetchExists(select().from(AIRBYTE_CONFIGS).where(CONFIG_TYPE.eq("TYPE"))));
    database.query(ctx -> ctx.fetchExists(select().from(AIRBYTE_CONFIGS).where(CONFIG_BLOB.eq(JSONB.valueOf("{}")))));
    Timestamp timestamp = Timestamp.from(Instant.ofEpochMilli(System.currentTimeMillis()));
    database.query(ctx -> ctx.fetchExists(select().from(AIRBYTE_CONFIGS).where(CREATED_AT.eq(timestamp))));
    database.query(ctx -> ctx.fetchExists(select().from(AIRBYTE_CONFIGS).where(UPDATED_AT.eq(timestamp))));

    // when the configs database has been initialized, calling getAndInitialize again will not change anything
    String testSchema = "CREATE TABLE IF NOT EXISTS airbyte_test_configs(id BIGINT PRIMARY KEY);";
    database = new ConfigsDatabaseInstance(container.getUsername(), container.getPassword(), container.getJdbcUrl(), testSchema).getAndInitialize();
    // the airbyte_test_configs table does not exist
    assertThrows(DataAccessException.class, () -> database.query(ctx -> ctx.fetchExists(select().from("airbyte_test_configs"))));
  }

}
