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

package io.airbyte.protocol.models;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

public class CatalogHelpers {

  public static AirbyteCatalog createAirbyteCatalog(String streamName, Field... fields) {
    return new AirbyteCatalog().withStreams(Lists.newArrayList(createAirbyteStream(streamName, fields)));
  }

  public static AirbyteStream createAirbyteStream(String streamName, Field... fields) {
    return createAirbyteStream(streamName, Arrays.asList(fields));
  }

  public static AirbyteStream createAirbyteStream(String streamName, List<Field> fields) {
    return new AirbyteStream().withName(streamName).withJsonSchema(fieldsToJsonSchema(fields));
  }

  public static JsonNode fieldsToJsonSchema(Field... fields) {
    return fieldsToJsonSchema(Arrays.asList(fields));
  }

  public static JsonNode fieldsToJsonSchema(List<Field> fields) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("type", "object")
        .put("properties", fields
            .stream()
            .collect(Collectors.toMap(
                Field::getName,
                field -> ImmutableMap.of("type", field.getTypeAsJsonSchemaString()))))
        .build());
  }

  /**
   * Gets the keys from the top-level properties object in the json schema.
   *
   * @param stream - airbyte stream
   * @return field names
   */
  @SuppressWarnings("unchecked")
  public static Set<String> getTopLevelFieldNames(final AirbyteStream stream) {
    // it is json, so the key has to be a string.
    final Map<String, Object> object = Jsons.object(stream.getJsonSchema().get("properties"), Map.class);
    return object.keySet();
  }

}
