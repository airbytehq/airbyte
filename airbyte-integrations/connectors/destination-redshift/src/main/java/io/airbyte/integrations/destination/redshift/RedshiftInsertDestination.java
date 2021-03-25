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

package io.airbyte.integrations.destination.redshift;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RedshiftInsertDestination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftDestination.class);

  public static final String DRIVER_CLASS = "com.amazon.redshift.jdbc.Driver";

  public RedshiftInsertDestination() {
    super(DRIVER_CLASS, new RedshiftSQLNameTransformer(), new RedshiftSqlOperations());
  }

  @Override
  public JsonNode toJdbcConfig(JsonNode redshiftConfig) {
    return getJdbcConfig(redshiftConfig);
  }

  public static JsonNode getJdbcConfig(JsonNode redshiftConfig) {
    final String schema = Optional.ofNullable(redshiftConfig.get("schema")).map(JsonNode::asText).orElse("public");

    return Jsons.jsonNode(ImmutableMap.builder()
        .put("username", redshiftConfig.get("username").asText())
        .put("password", redshiftConfig.get("password").asText())
        .put("jdbc_url", String.format("jdbc:redshift://%s:%s/%s",
            redshiftConfig.get("host").asText(),
            redshiftConfig.get("port").asText(),
            redshiftConfig.get("database").asText()))
        .put("schema", schema)
        .build());
  }

}
