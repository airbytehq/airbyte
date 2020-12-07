/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.destination.jdbc;

import static org.jooq.impl.DSL.currentSchema;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.CloseableQueue;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.DestinationConsumer;
import io.airbyte.integrations.destination.DestinationConsumerFactory;
import io.airbyte.integrations.destination.IdentifierNamingResolvable;
import io.airbyte.integrations.destination.SqlDestinationOperations;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.io.IOException;
import java.sql.SQLException;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(AbstractJdbcDestination.class);
  protected static final String COLUMN_NAME = "data";

  private final String driverClass;
  private final SQLDialect dialect;
  private final IdentifierNamingResolvable namingResolver;

  public AbstractJdbcDestination(final String driverClass, final SQLDialect dialect, final IdentifierNamingResolvable namingResolver) {
    this.driverClass = driverClass;
    this.dialect = dialect;
    this.namingResolver = namingResolver;
  }

  @Override
  public ConnectorSpecification spec() throws IOException {
    // return a JsonSchema representation of the spec for the integration.
    final String resourceString = MoreResources.readResource("spec.json");
    return Jsons.deserialize(resourceString, ConnectorSpecification.class);
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    try (final Database database = getDatabase(config)) {
      // attempt to get current schema. this is a cheap query to sanity check that we can connect to the
      // database. `currentSchema()` is a jooq method that will run the appropriate query based on which
      // database it is connected to.
      database.query(this::getCurrentDatabaseName);

      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (Exception e) {
      LOGGER.debug("Exception while checking connection: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage("Can't connect with provided configuration.");
    }
  }

  protected Database getDatabase(JsonNode config) {
    final JsonNode jdbcConfig = toJdbcConfig(config);

    return Databases.createDatabase(
        jdbcConfig.get("username").asText(),
        jdbcConfig.has("password") ? jdbcConfig.get("password").asText() : null,
        jdbcConfig.get("jdbc_url").asText(),
        driverClass,
        dialect);
  }

  public abstract JsonNode toJdbcConfig(JsonNode config);

  private String getCurrentDatabaseName(DSLContext ctx) {
    return ctx.select(currentSchema()).fetch().get(0).getValue(0, String.class);
  }

  @Override
  public IdentifierNamingResolvable getNamingResolver() {
    return namingResolver;
  }

  @Override
  public DestinationConsumer<AirbyteMessage> write(JsonNode config, ConfiguredAirbyteCatalog catalog) throws Exception {
    final DestinationImpl destination = new DestinationImpl(getDatabase(config));
    return DestinationConsumerFactory.build(destination, getNamingResolver(), config, catalog);
  }

  protected String getDefaultSchemaName(JsonNode config) {
    if (config.has("schema")) {
      return config.get("schema").asText();
    } else {
      return "public";
    }
  }

  protected String createSchemaQuery(String schemaName) {
    return String.format("CREATE SCHEMA IF NOT EXISTS %s;\n", schemaName);
  }

  protected abstract String createDestinationTableQuery(String schemaName, String tableName);

  protected String dropDestinationTableQuery(String schemaName, String tableName) {
    return String.format("DROP TABLE IF EXISTS %s.%s;\n", schemaName, tableName);
  }

  protected abstract String insertBufferedRecordsQuery(int batchSize, CloseableQueue<byte[]> writeBuffer, String schemaName, String tableName);

  private class DestinationImpl implements SqlDestinationOperations {

    private final Database database;

    public DestinationImpl(Database database) {
      this.database = database;
    }

    @Override
    public void createSchema(String schemaName) throws Exception {
      database.query(ctx -> ctx.execute(createSchemaQuery(schemaName)));
    }

    @Override
    public void createDestinationTable(String schemaName, String tableName) throws SQLException {
      database.query(ctx -> ctx.execute(createDestinationTableQuery(schemaName, tableName)));
    }

    @Override
    public void insertBufferedRecords(int batchSize, CloseableQueue<byte[]> writeBuffer, String schemaName, String tableName) throws Exception {
      database.query(ctx -> ctx.execute(insertBufferedRecordsQuery(batchSize, writeBuffer, schemaName, tableName)));
    }

    @Override
    public String truncateTableQuery(String schemaName, String tableName) {
      return String.format("TRUNCATE TABLE %s.%s;\n", schemaName, tableName);
    }

    @Override
    public String insertIntoFromSelectQuery(String schemaName, String srcTableName, String dstTableName) {
      return String.format("INSERT INTO %s.%s SELECT * FROM %s.%s;\n", schemaName, dstTableName, schemaName, srcTableName);
    }

    @Override
    public void executeTransaction(String queries) throws Exception {
      database.transaction(ctx -> ctx.execute(queries));
    }

    @Override
    public void dropDestinationTable(String schemaName, String tableName) throws SQLException {
      database.query(ctx -> ctx.execute(dropDestinationTableQuery(schemaName, tableName)));
    }

  }

}
