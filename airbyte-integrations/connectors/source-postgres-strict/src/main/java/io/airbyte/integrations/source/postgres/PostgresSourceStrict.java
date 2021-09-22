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

import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_DELETED_AT;
import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_UPDATED_AT;
import static java.util.stream.Collectors.toList;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcSourceOperations;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.jdbc.PostgresJdbcStreamingQueryConfiguration;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.ssh.SshWrappedSource;
import io.airbyte.integrations.debezium.AirbyteDebeziumHandler;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.relationaldb.StateManager;
import io.airbyte.integrations.source.relationaldb.TableInfo;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.SyncMode;
import java.sql.JDBCType;
import java.sql.PreparedStatement;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresSourceStrict implements Source {
  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresSourceStrict.class);

  private final Source source;

  PostgresSourceStrict() {
    this(PostgresSource.sshWrappedSource());
  }
  PostgresSourceStrict(final Source source) {
    this.source = source;
  }

  @Override
  public ConnectorSpecification spec() throws Exception {
    final String resourceString = MoreResources.readResource("strict_spec.json");
    return Jsons.deserialize(resourceString, ConnectorSpecification.class);
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) throws Exception {
    return source.check(config);
  }

  @Override
  public AirbyteCatalog discover(final JsonNode config) throws Exception {
    return source.discover(config);
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read(final JsonNode config, final ConfiguredAirbyteCatalog catalog, final JsonNode state)
      throws Exception {
    return source.read(config, catalog, state);
  }

  public static void main(final String[] args) throws Exception {
    final Source source = new SshWrappedSource(new PostgresSourceStrict(), List.of("host"), List.of("port"));
    LOGGER.info("starting source: {}", PostgresSourceStrict.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", PostgresSourceStrict.class);
  }
}
