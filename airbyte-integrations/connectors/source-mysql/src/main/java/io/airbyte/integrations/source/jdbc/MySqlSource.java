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

package io.airbyte.integrations.source.jdbc;

import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.table;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.concurrency.VoidCallable;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.io.IOException;
import java.util.stream.Stream;
import org.jooq.SQLDialect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MySqlSource implements Source{
  private static final Logger LOGGER = LoggerFactory.getLogger(MySqlSource.class);
  private final JdbcSource jdbcSource;

  public MySqlSource() {
    jdbcSource = new JdbcSource("com.mysql.cj.jdbc.Driver", SQLDialect.MYSQL);
  }

  @Override
  public ConnectorSpecification spec() throws IOException {
    return jdbcSource.spec();
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    // convert config

    return jdbcSource.check(toJdbcConfig(config));
  }
  @Override
  public AirbyteCatalog discover(JsonNode config) throws Exception {
    // convert config
    return jdbcSource.discover(toJdbcConfig(config));
  }

  @Override
  public Stream<AirbyteMessage> read(JsonNode config, AirbyteCatalog catalog, JsonNode state) throws Exception {
    // convert config
    return jdbcSource.read(toJdbcConfig(config), catalog, state);
  }

  public static JsonNode toJdbcConfig(JsonNode mySqlConfig) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("username", mySqlConfig.get("user").asText())
        .put("password", mySqlConfig.get("password").asText())
        .put("jdbc_url", String.format("jdbc:mysql://%s:%s/%s",
            mySqlConfig.get("host").asText(),
            mySqlConfig.get("port").asText(),
            mySqlConfig.get("database").asText()))
        .build());
  }

  public static void main(String[] args) throws Exception {
    final Source source = new MySqlSource();
    LOGGER.info("starting source: {}", MySqlSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", MySqlSource.class);
  }
}
