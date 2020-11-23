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
import java.time.Instant;

public class StandardSQLNaming implements SQLNamingResolvable {

  @Override
  public String getRawSchemaName(JsonNode config, String schemaName, String streamName) {
    // FIXME based on config, allow schema override from stream name or not
    extractSchemaPart(streamName);
    return schemaName;
  }

  @Override
  public String getRawTableName(JsonNode config, String streamName) {
    return convertStreamName(removeSchemaPart(streamName)) + "_raw";
  }

  @Override
  public String getTmpTableName(JsonNode config, String streamName) {
    return convertStreamName(removeSchemaPart(streamName)) + "_" + Instant.now().toEpochMilli();
  }

  protected String extractSchemaPart(String streamName) {
    // FIXME return substring before '.'
    return streamName;
  }

  protected String removeSchemaPart(String streamName) {
    // FIXME remove substring before '.'
    return streamName;
  }

  protected String convertStreamName(String streamName) {
    // FIXME replace invalid characters by '_'
    return streamName;
  }

}
