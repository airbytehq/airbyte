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
import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.table;
import static org.jooq.impl.DSL.unquotedName;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Charsets;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.CloseableQueue;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.base.AbstractDestination;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.SQLNamingResolvable;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.io.IOException;
import java.sql.SQLException;
import java.time.LocalDateTime;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.UUID;
import org.jooq.DSLContext;
import org.jooq.InsertValuesStep3;
import org.jooq.JSONB;
import org.jooq.Record;
import org.jooq.SQLDialect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class AbstractJdbcDestination extends AbstractDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(AbstractJdbcDestination.class);
  protected static final String COLUMN_NAME = "data";

  private final String driverClass;
  private final SQLDialect dialect;
  private final SQLNamingResolvable namingResolver;
  private Database databaseConnection = null;

  public AbstractJdbcDestination(final String driverClass, final SQLDialect dialect, final SQLNamingResolvable namingResolver) {
    super();
    this.driverClass = driverClass;
    this.dialect = dialect;
    this.namingResolver = namingResolver;
  }

  public abstract JsonNode toJdbcConfig(JsonNode config);

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

  protected String getCurrentDatabaseName(DSLContext ctx) {
    return ctx.select(currentSchema()).fetch().get(0).getValue(0, String.class);
  }

  @Override
  public SQLNamingResolvable getNamingResolver() {
    return namingResolver;
  }

  /**
   * Return the default schema where to data in the destination if the catalog doesn't specify any
   * location
   *
   * @param config The destination configuration
   * @return default schema name where to save data
   */
  protected String getDefaultSchemaName(JsonNode config) {
    if (config.has("schema")) {
      return config.get("schema").asText();
    } else {
      return "public";
    }
  }

  @Override
  protected void connectDatabase(JsonNode config) {
    databaseConnection = getDatabase(config);
  }

  protected Database getDatabaseConnection() {
    return databaseConnection;
  }

  @Override
  public void queryDatabase(String query) throws SQLException {
    getDatabaseConnection().query(ctx -> ctx.execute(query));
  }

  @Override
  public void queryDatabaseInTransaction(String queries) throws Exception {
    getDatabaseConnection().transaction(ctx -> ctx.execute(queries));
  }

  @Override
  public String createRawTableQuery(String schemaName, String streamName) {
    return String.format(
        "CREATE TABLE IF NOT EXISTS %s.%s ( \n"
            + "ab_id VARCHAR PRIMARY KEY,\n"
            + "%s JSONB,\n"
            + "emitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP\n"
            + ");\n",
        schemaName, streamName, COLUMN_NAME);
  }

  @Override
  public void writeBufferedRecords(int batchSize, CloseableQueue<byte[]> writeBuffer, String schemaName, String tmpTableName) {
    try {
      getDatabaseConnection().query(ctx -> buildWriteQuery(ctx, batchSize, writeBuffer, schemaName, tmpTableName).execute());
    } catch (SQLException e) {
      throw new RuntimeException(e);
    }
  }

  // build the following query:
  // INSERT INTO <schemaName>.<tableName>(data)
  // VALUES
  // ({ "my": "data" }),
  // ({ "my": "data" });
  private static InsertValuesStep3<Record, String, JSONB, OffsetDateTime> buildWriteQuery(DSLContext ctx,
                                                                                          int batchSize,
                                                                                          CloseableQueue<byte[]> writeBuffer,
                                                                                          String schemaName,
                                                                                          String tmpTableName) {
    InsertValuesStep3<Record, String, JSONB, OffsetDateTime> step =
        ctx.insertInto(table(unquotedName(schemaName, tmpTableName)), field("ab_id", String.class),
            field(COLUMN_NAME, JSONB.class), field("emitted_at", OffsetDateTime.class));

    for (int i = 0; i < batchSize; i++) {
      final byte[] record = writeBuffer.poll();
      if (record == null) {
        break;
      }
      final AirbyteRecordMessage message = Jsons.deserialize(new String(record, Charsets.UTF_8), AirbyteRecordMessage.class);

      step = step.values(UUID.randomUUID().toString(), JSONB.valueOf(Jsons.serialize(message.getData())),
          OffsetDateTime.of(LocalDateTime.ofEpochSecond(message.getEmittedAt() / 1000, 0, ZoneOffset.UTC), ZoneOffset.UTC));
    }

    return step;
  }

}
