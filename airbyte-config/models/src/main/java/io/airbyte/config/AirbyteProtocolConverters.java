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
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.SyncMode;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map.Entry;
import java.util.Spliterators;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;

// todo (cgardens) - hack, remove after we've gotten rid of Schema object.
public class AirbyteProtocolConverters {

  public static ConfiguredAirbyteCatalog toConfiguredCatalog(Schema schema) {
    final List<ConfiguredAirbyteStream> airbyteStreams = schema.getStreams().stream()
        .filter(s -> s.getSelected() != null && s.getSelected())
        .map(s -> new ConfiguredAirbyteStream()
            // immutable
            // todo (cgardens) - not great that we just trust the API to not mutate these.
            .withStream(new AirbyteStream()
                .withName(s.getName())
                .withJsonSchema(toJson(s.getFields()))
                .withSupportedSyncModes(s.getSupportedSyncModes()
                    .stream()
                    .map(e -> Enums.convertTo(e, SyncMode.class))
                    .collect(Collectors.toList()))
                .withSourceDefinedCursor(s.getSourceDefinedCursor())
                .withDefaultCursorField(s.getDefaultCursorField()))
            // configurable
            .withSyncMode(Enums.convertTo(s.getSyncMode(), SyncMode.class))
            .withCursorField(s.getCursorField()))
        .collect(Collectors.toList());
    return new ConfiguredAirbyteCatalog().withStreams(airbyteStreams);
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
            .collect(Collectors.toMap(
                Field::getName,
                field -> ImmutableMap.of("type", field.getDataType().toString().toLowerCase()))))
        .build());
  }

  public static Schema toSchema(AirbyteCatalog catalog) {
    return new Schema().withStreams(catalog.getStreams()
        .stream()
        .map(airbyteStream -> new Stream()
            // immutable
            .withName(airbyteStream.getName())
            .withFields(toFields(airbyteStream.getJsonSchema().get("properties")))
            .withSupportedSyncModes(airbyteStream.getSupportedSyncModes()
                .stream()
                .map(e -> Enums.convertTo(e, StandardSync.SyncMode.class))
                .collect(Collectors.toList()))
            .withSourceDefinedCursor(airbyteStream.getSourceDefinedCursor())
            .withDefaultCursorField(airbyteStream.getDefaultCursorField())
            .withSelected(true)) // by default all discovered streams are treated as default.
        // configurable fields syncMode and cursorField are not set since they will never be defined in an
        // AirbyteCatalog.
        .collect(Collectors.toList()));
  }

  private static List<Field> toFields(JsonNode jsonSchemaPropertiesObject) {
    final List<Entry<String, JsonNode>> list = new ArrayList<>();
    // todo (cgardens) - assumes it is json schema type object with properties. not a stellar
    // assumption.
    final Iterator<Entry<String, JsonNode>> iterator = jsonSchemaPropertiesObject.fields();
    while (iterator.hasNext()) {
      list.add(iterator.next());
    }

    return list
        .stream()
        .map(item -> new Field()
            .withName(item.getKey())
            .withDataType(getDataType(item.getValue())))
        .collect(Collectors.toList());
  }

  // todo (cgardens) - add more robust handling for jsonschema types.

  /**
   * JsonSchema tends to have 2 types for fields one of which is null. The null is pretty irrelevant,
   * so look at types and find the first non-null one and use that.
   *
   * @param node - list of types from jsonschema.
   * @return reduce down to one type which best matches the field's data type
   */
  private static DataType jsonSchemaTypesToDataType(JsonNode node) {
    if (node.isTextual()) {
      return DataType.valueOf(convertToNumberIfInteger(node.asText().toUpperCase()));
    } else if (node.isArray()) {
      return StreamSupport.stream(Spliterators.spliteratorUnknownSize(node.elements(), 0), false)
          .filter(typeString -> !typeString.asText().toUpperCase().equals("NULL"))
          .map(typeString -> DataType.valueOf(convertToNumberIfInteger(typeString.asText().toUpperCase())))
          .findFirst()
          // todo (cgardens) - or throw?
          .orElse(DataType.STRING);
    } else {
      throw new IllegalArgumentException("Unknown jsonschema type:" + Jsons.serialize(node));
    }
  }

  // TODO HACK (jrhizor): this defaults to OBJECT in the case of anyOf. May fail with anyOf: [int or
  // string],
  // for example.
  private static DataType getDataType(JsonNode node) {
    final JsonNode type = node.get("type");

    if (type == null) {
      return DataType.OBJECT;
    } else {
      return jsonSchemaTypesToDataType(type);
    }
  }

  // TODO HACK (jrhizor): convert Integer to Number until we have a more solid typing system
  private static String convertToNumberIfInteger(String type) {
    if (type.toUpperCase().equals("INTEGER")) {
      return "NUMBER";
    } else {
      return type;
    }
  }

}
