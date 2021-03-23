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

package io.airbyte.integrations.source.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.jdbc.PostgresJdbcStreamingQueryConfiguration;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresSource extends AbstractJdbcSource implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresSource.class);

  static final String DRIVER_CLASS = "org.postgresql.Driver";

  public PostgresSource() {
    super(DRIVER_CLASS, new PostgresJdbcStreamingQueryConfiguration());
  }

  @Override
  public JsonNode toJdbcConfig(JsonNode config) {
    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put("username", config.get("username").asText())
        .put("jdbc_url", String.format("jdbc:postgresql://%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("database").asText()));

    if (config.has("password")) {
      configBuilder.put("password", config.get("password").asText());
    }

    return Jsons.jsonNode(configBuilder.build());
  }

  @Override
  public Set<String> getExcludedInternalSchemas() {
    return Set.of("information_schema", "pg_catalog", "pg_internal", "catalog_history");
  }

  @Override
  public List<CheckedConsumer<JdbcDatabase, Exception>> getCheckOperations(JsonNode config) throws Exception {
    final List<CheckedConsumer<JdbcDatabase, Exception>> checkOperations = new ArrayList<>(super.getCheckOperations(config));

    if (!config.get("replication_method").isNull() && !config.get("replication_method").get("replication_slot").isNull()) {
      checkOperations.add(database -> database.query(connection -> {
        LOGGER.info("Attempting to find the named replication slot.");
        final String sql =
            String.format("SELECT slot_name, plugin, database FROM pg_replication_slots WHERE slot_name = %s AND plugin = %s AND database = %s",
                JdbcUtils.enquoteIdentifier(connection, config.get("replication_method").get("replication_slot").asText()),
                JdbcUtils.enquoteIdentifier(connection, "pgoutput"),
                JdbcUtils.enquoteIdentifier(connection, config.get("database").asText()));

        return connection.prepareStatement(sql);
      }, JdbcUtils::rowToJson));
    }

    return checkOperations;
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read(JsonNode config, ConfiguredAirbyteCatalog catalog, JsonNode state) throws Exception {
    if (config.get("replication_method").isNull() || config.get("replication_method").get("replication_slot").isNull()) {
      return super.read(config, catalog, state);
    } else {
      throw new RuntimeException("todo: implement cdc. Easy!");
    }
  }

  public static void main(String[] args) throws Exception {
    final Source source = new PostgresSource();
    LOGGER.info("starting source: {}", PostgresSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", PostgresSource.class);
  }

}
