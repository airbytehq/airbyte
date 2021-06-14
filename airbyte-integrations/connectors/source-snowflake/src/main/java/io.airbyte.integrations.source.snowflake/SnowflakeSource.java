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

package io.airbyte.integrations.source.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeSource extends AbstractJdbcSource implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeSource.class);
  public static final String DRIVER_CLASS = "net.snowflake.client.jdbc.SnowflakeDriver";

  public SnowflakeSource() {
    super(DRIVER_CLASS, new SnowflakeJdbcStreamingQueryConfiguration());
  }

  public static void main(String[] args) throws Exception {
    final Source source = new SnowflakeSource();
    LOGGER.info("starting source: {}", SnowflakeSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", SnowflakeSource.class);
  }

  @Override
  public JsonNode toJdbcConfig(JsonNode config) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("jdbc_url", String.format("jdbc:snowflake://%s/",
            config.get("host").asText()))
        .put("host", config.get("host").asText())
        .put("username", config.get("username").asText())
        .put("password", config.get("password").asText())
        .put("connection_properties", String.format("role=%s;warehouse=%s;database=%s;schema=%s",
            config.get("role").asText(),
            config.get("warehouse").asText(),
            config.get("database").asText(),
            config.get("schema").asText()))
        .build());
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Set.of(
        "INFORMATION_SCHEMA");
  }

}
