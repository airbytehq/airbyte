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

package io.airbyte.config;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteStream;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map.Entry;
import java.util.stream.Collectors;

// todo (cgardens) - hack, remove after we've gotten rid of Schema object.
public class AirbyteProtocolConverters {

  public static AirbyteCatalog toCatalog(Schema schema) {
    return new AirbyteCatalog()
        .withStreams(schema.getStreams().stream().map(s -> new AirbyteStream()
            .withName(s.getName())
            .withJsonSchema(toJson(s.getFields()))).collect(Collectors.toList()));
  }

  // todo (cgardens) - this will only work with table / column schemas. it's hack to get us through
  // migration.
  public static JsonNode toJson(List<Field> fields) {
    // assumes this shape.
    // type: object,
    // property: {
    // <fieldName>: {
    // "type" : <fieldType>
    // }
    // }
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("type", "object")
        .put("properties", fields
            .stream()
            .filter(Field::getSelected)
            .collect(Collectors.toMap(
                Field::getName,
                field -> ImmutableMap.of("type", field.getDataType().toString().toLowerCase()))))
        .build());
  }

  public static Schema toSchema(AirbyteCatalog catalog) {
    return new Schema().withStreams(catalog.getStreams().stream().map(airbyteStream -> {
      final List<Entry<String, JsonNode>> list = new ArrayList<>();
      final Iterator<Entry<String, JsonNode>> iterator = airbyteStream.getSchema().get("properties").fields();
      while (iterator.hasNext()) {
        list.add(iterator.next());
      }
      return new Stream().withName(airbyteStream.getName())
          .withFields(list.stream().map(item -> new Field()
              .withName(item.getKey())
              .withDataType(DataType.valueOf(item.getValue().get("type").asText().toUpperCase()))
              .withSelected(true)).collect(Collectors.toList()));
    }).collect(Collectors.toList()));
  }

}
