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

package io.airbyte.integrations.base;

import com.fasterxml.jackson.databind.JsonNode;
import java.text.Normalizer;
import java.time.Instant;

public class StandardSQLNaming implements SQLNamingResolvable {

  public static String SCHEMA_FROM_SOURCE = "allowSchemaFromSource";

  @Override
  public String getRawSchemaName(JsonNode config, String schemaName, String streamName) {
    final boolean allowsSchemaOverride = getSchemaFromSourceConfig(config);
    final int schemaIndex = streamName.indexOf(".");
    if (allowsSchemaOverride && schemaIndex > -1) {
      return convertStreamName(extractSchemaPart(streamName));
    } else {
      return convertStreamName(schemaName);
    }
  }

  protected boolean getSchemaFromSourceConfig(JsonNode config) {
    if (config.has(SCHEMA_FROM_SOURCE)) {
      return config.get(SCHEMA_FROM_SOURCE).asBoolean();
    } else {
      return true;
    }
  }

  @Override
  public String getRawTableName(JsonNode config, String streamName) {
    if (getSchemaFromSourceConfig(config)) {
      return convertStreamName(removeSchemaPart(streamName) + "_raw");
    } else {
      return convertStreamName(streamName + "_raw");
    }
  }

  @Override
  public String getTmpTableName(JsonNode config, String streamName) {
    if (getSchemaFromSourceConfig(config)) {
      return convertStreamName(removeSchemaPart(streamName) + "_" + Instant.now().toEpochMilli());
    } else {
      return convertStreamName(streamName + "_" + Instant.now().toEpochMilli());
    }
  }

  static private String extractSchemaPart(String streamName) {
    final int schemaIndex = streamName.indexOf(".");
    if (schemaIndex > -1) {
      return streamName.substring(0, schemaIndex);
    } else {
      return streamName;
    }
  }

  static private String removeSchemaPart(String streamName) {
    final int schemaIndex = streamName.indexOf(".");
    if (schemaIndex > -1) {
      return streamName.substring(schemaIndex + 1);
    } else {
      return streamName;
    }
  }

  protected String convertStreamName(String input) {
    final String value = Normalizer.normalize(input, Normalizer.Form.NFD);
    return value
        .replaceAll("\\s+", "_")
        .replaceAll(getNonValidCharacterPattern(), "_");
  }

  protected String getNonValidCharacterPattern() {
    return "[^\\p{ASCII}]";
  }

}
