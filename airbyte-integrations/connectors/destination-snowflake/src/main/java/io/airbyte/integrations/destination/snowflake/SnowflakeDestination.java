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

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.DestinationConsumer;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.SQLNamingResolvable;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.queue.BigQueue;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.function.Supplier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeDestination.class);

  protected static final String COLUMN_NAME = "data";

  private final SQLNamingResolvable namingResolver;

  public SnowflakeDestination() {
    namingResolver = new SnowflakeSQLNaming();
  }

  @Override
  public ConnectorSpecification spec() throws IOException {
    final String resourceString = MoreResources.readResource("spec.json");
    return Jsons.deserialize(resourceString, ConnectorSpecification.class);
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    try {
      final Supplier<Connection> connectionFactory = SnowflakeDatabase.getConnectionFactory(config);
      SnowflakeDatabase.executeSync(connectionFactory, "SELECT 1;");
      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (Exception e) {
      return new AirbyteConnectionStatus().withStatus(Status.FAILED).withMessage(e.getMessage());
    }
  }

  @Override
  public SQLNamingResolvable getNamingResolver() {
    return namingResolver;
  }

  /**
   * Strategy:
   * <p>
   * 1. Create a temporary table for each stream
   * </p>
   * <p>
   * 2. Accumulate records in a buffer. One buffer per stream.
   * </p>
   * <p>
   * 3. As records accumulate write them in batch to the database. We set a minimum numbers of records
   * before writing to avoid wasteful record-wise writes.
   * </p>
   * <p>
   * 4. Once all records have been written to buffer, flush the buffer and write any remaining records
   * to the database (regardless of how few are left).
   * </p>
   * <p>
   * 5. In a single transaction, delete the target tables if they exist and rename the temp tables to
   * the final table name.
   * </p>
   *
   * @param config - Snowflake-specific configuration object as json.
   * @param catalog - schema of the incoming messages.
   * @return consumer that writes singer messages to the database.
   * @throws Exception - anything could happen!
   */
  @Override
  public DestinationConsumer<AirbyteMessage> write(JsonNode config, ConfiguredAirbyteCatalog catalog) throws Exception {
    // connect to snowflake
    final Supplier<Connection> connectionFactory = SnowflakeDatabase.getConnectionFactory(config);
    Map<String, SnowflakeWriteContext> writeBuffers = new HashMap<>();
    Set<String> schemaSet = new HashSet<>();

    // create temporary tables if they do not exist
    // we don't use temporary/transient since we want to control the lifecycle
    for (final ConfiguredAirbyteStream stream : catalog.getStreams()) {
      final String streamName = stream.getStream().getName();
      final String schemaName = getNamingResolver().getIdentifier(config.get("schema").asText());
      final String tableName = getNamingResolver().getRawTableName(streamName);
      final String tmpTableName = getNamingResolver().getTmpTableName(streamName);
      if (!schemaSet.contains(schemaName)) {
        final String query = String.format("CREATE SCHEMA IF NOT EXISTS %s;", schemaName);

        SnowflakeDatabase.executeSync(connectionFactory, query);
        schemaSet.add(schemaName);
      }
      final String query = String.format(
          "CREATE TABLE IF NOT EXISTS %s.%s ( \n"
              + "ab_id VARCHAR PRIMARY KEY,\n"
              + "%s VARIANT,\n"
              + "emitted_at TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp()\n"
              + ") data_retention_time_in_days = 0;",
          schemaName, tmpTableName, COLUMN_NAME);

      SnowflakeDatabase.executeSync(connectionFactory, query);

      final Path queueRoot = Files.createTempDirectory("queues");
      final BigQueue writeBuffer = new BigQueue(queueRoot.resolve(stream.getStream().getName()), stream.getStream().getName());
      writeBuffers.put(stream.getStream().getName(), new SnowflakeWriteContext(schemaName, tableName, tmpTableName, writeBuffer));
    }

    // write to transient tables
    // if success copy delete main table if exists. rename transient tables to real tables.
    return new SnowflakeRecordConsumer(connectionFactory, writeBuffers, catalog);
  }

  public static void main(String[] args) throws Exception {
    final Destination destination = new SnowflakeDestination();
    LOGGER.info("starting destination: {}", SnowflakeDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", SnowflakeDestination.class);
  }

}
