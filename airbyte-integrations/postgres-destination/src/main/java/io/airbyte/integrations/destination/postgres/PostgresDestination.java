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

package io.airbyte.integrations.destination.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.DestinationConnectionSpecification;
import io.airbyte.config.Schema;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardCheckConnectionOutput.Status;
import io.airbyte.config.StandardDiscoverSchemaOutput;
import io.airbyte.db.DatabaseHelper;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.DestinationConsumer;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.singer.SingerMessage;
import java.io.IOException;
import org.apache.commons.dbcp2.BasicDataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresDestination.class);

  @Override
  public DestinationConnectionSpecification spec() throws IOException {
    // return a jsonschema representation of the spec for the integration.
    final String resourceString = MoreResources.readResource("spec.json");
    return Jsons.deserialize(resourceString, DestinationConnectionSpecification.class);
  }

  // fixme - implement this method such that it checks whether it can connect to the destination.
  // this should return a StandardCheckConnectionOutput with the status field set to true if the
  // connection succeeds and false if it does not. if false consider adding a message in the message
  // field to help the user figure out what they need to do differently so that the connection will
  // succeed.
  @Override
  public StandardCheckConnectionOutput check(JsonNode config) {
    try {
      final BasicDataSource connectionPool = DatabaseHelper.getConnectionPool(
          config.get("username").asText(),
          config.get("password").asText(),
          String.format("jdbc:postgresql://%s:%s/%s", config.get("host").asText(), config.get("port").asText(), config.get("database").asText()));

      DatabaseHelper.query(connectionPool, ctx -> ctx.execute(
          "SELECT *\n"
              + "FROM pg_catalog.pg_tables\n"
              + "WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';"));

      connectionPool.close();
    } catch (Exception e) {
      // todo (cgardens) - better error messaging.
      return new StandardCheckConnectionOutput().withStatus(Status.FAILURE).withMessage(e.getMessage());
    }

    return new StandardCheckConnectionOutput().withStatus(Status.SUCCESS);
  }

  // fixme - implement this method such that it returns the current schema found in the destination.
  @Override
  public StandardDiscoverSchemaOutput discover(JsonNode config) {
    throw new RuntimeException("Not Implemented");
  }

  // fixme - implement this method such that it returns a consumer that can push messages to the
  // destination.
  @Override
  public DestinationConsumer<SingerMessage> write(JsonNode config, Schema schema) throws IOException {
    return new RecordConsumer();
  }

  public static class RecordConsumer implements DestinationConsumer<SingerMessage> {

    @Override
    public void accept(SingerMessage singerMessage) throws Exception {
      // fixme - implement how to write a message to the destination
      throw new RuntimeException("Not Implemented");
    }

    @Override
    public void close() throws Exception {
      // fixme - implement hot to close the connection to the destination.
      throw new RuntimeException("Not Implemented");
    }

  }

  public static void main(String[] args) throws Exception {
    // fixme - instantiate your implementation of the Destination interface and pass it to
    // IntegrationRunner.
    final Destination destination = new PostgresDestination();
    // this is airbyte's entrypoint into the integration. do not remove this line!
    LOGGER.info("starting destination: {}", PostgresDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", PostgresDestination.class);
  }

}
