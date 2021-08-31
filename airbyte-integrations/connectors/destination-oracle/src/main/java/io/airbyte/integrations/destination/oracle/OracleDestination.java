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

package io.airbyte.integrations.destination.oracle;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class OracleDestination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(OracleDestination.class);

  public static final String DRIVER_CLASS = "oracle.jdbc.OracleDriver";

  public static final String COLUMN_NAME_AB_ID = "\"" + JavaBaseConstants.COLUMN_NAME_AB_ID.toUpperCase() + "\"";
  public static final String COLUMN_NAME_DATA = "\"" + JavaBaseConstants.COLUMN_NAME_DATA.toUpperCase() + "\"";
  public static final String COLUMN_NAME_EMITTED_AT = "\"" + JavaBaseConstants.COLUMN_NAME_EMITTED_AT.toUpperCase() + "\"";

  public OracleDestination() {
    super(DRIVER_CLASS, new OracleNameTransformer(), new OracleOperations("users"));
    System.setProperty("oracle.jdbc.timezoneAsRegion", "false");
  }

  @Override
  public JsonNode toJdbcConfig(JsonNode config) {
    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put("username", config.get("username").asText())
        .put("jdbc_url", String.format("jdbc:oracle:thin:@//%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("sid").asText()));

    if (config.has("password")) {
      configBuilder.put("password", config.get("password").asText());
    }

    return Jsons.jsonNode(configBuilder.build());
  }

  public static void main(String[] args) throws Exception {
    final Destination destination = new OracleDestination();
    LOGGER.info("starting destination: {}", OracleDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", OracleDestination.class);
  }

}
