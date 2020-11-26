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

import com.google.common.base.Charsets;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import java.nio.ByteBuffer;

public class IncrementalUtils {

  public static String getCursorField(ConfiguredAirbyteStream stream) {
    if (stream.getCursorField().size() == 0) {
      throw new IllegalStateException("No cursor field specified for stream attempting to do incremental.");
    } else if (stream.getCursorField().size() > 1) {
      throw new IllegalStateException("JdbcSource does not support composite cursor fields.");
    } else {
      return stream.getCursorField().get(0);
    }
  }

  public static JsonSchemaPrimitive getCursorType(ConfiguredAirbyteStream stream, String cursorField) {
    if (stream.getStream().getJsonSchema().get("properties") == null) {
      throw new IllegalStateException(String.format("No properties found in stream: %s.", stream.getStream().getName()));
    }

    if (stream.getStream().getJsonSchema().get("properties").get(cursorField) == null) {
      throw new IllegalStateException(
          String.format("Could not find cursor field: %s in schema for stream: %s.", cursorField, stream.getStream().getName()));
    }

    if (stream.getStream().getJsonSchema().get("properties").get(cursorField).get("type") == null) {
      throw new IllegalStateException(
          String.format("Could not find cursor type for field: %s in schema for stream: %s.", cursorField, stream.getStream().getName()));
    }

    return JsonSchemaPrimitive.valueOf(stream.getStream().getJsonSchema().get("properties").get(cursorField).get("type").asText().toUpperCase());
  }

  // x < 0 mean replace original
  // x == 0 means keep original
  // x > 0 means keep original
  public static int compareCursors(String original, String candidate, JsonSchemaPrimitive type) {
    if (original == null && candidate == null) {
      return 0;
    }

    if (candidate == null) {
      return 1;
    }

    if (original == null) {
      return -1;
    }

    switch (type) {
      case STRING -> {
         return original.compareTo(candidate);
      }
      case NUMBER -> {
        // todo (cgardens) - handle big decimal. this is currently an overflow risk.
        return Double.compare(Double.parseDouble(original), Double.parseDouble(candidate));
      }
      case BOOLEAN -> {
        return Boolean.compare(Boolean.parseBoolean(original), Boolean.parseBoolean(candidate));
      }
      // includes OBJECT, ARRAY, NULL
      default -> throw new IllegalStateException(String.format("Cannot use field of type %s as a comparable", type));
    }
  }

}
