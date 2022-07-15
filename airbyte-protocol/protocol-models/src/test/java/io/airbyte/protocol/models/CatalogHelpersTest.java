/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Sets;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.transform_models.FieldTransform;
import io.airbyte.protocol.models.transform_models.StreamTransform;
import io.airbyte.protocol.models.transform_models.UpdateFieldSchemaTransform;
import io.airbyte.protocol.models.transform_models.UpdateStreamTransform;
import java.io.IOException;
import java.util.Comparator;
import java.util.List;
import java.util.Set;
import java.util.stream.Stream;
import org.junit.jupiter.api.Test;

class CatalogHelpersTest {

  // handy for debugging test only.
  private static final Comparator<StreamTransform> STREAM_TRANSFORM_COMPARATOR =
      Comparator.comparing(StreamTransform::getTransformType);

  @Test
  void testFieldToJsonSchema() {
    final String expected = """
                                {
                                  "type": "object",
                                  "properties": {
                                    "name": {
                                      "type": "string"
                                    },
                                    "test_object": {
                                      "type": "object",
                                      "properties": {
                                        "thirdLevelObject": {
                                          "type": "object",
                                          "properties": {
                                            "data": {
                                              "type": "string"
                                            },
                                            "intData": {
                                              "type": "number"
                                            }
                                          }
                                        },
                                        "name": {
                                          "type": "string"
                                        }
                                      }
                                    }
                                  }
                                }
                            """;
    final JsonNode actual = CatalogHelpers.fieldsToJsonSchema(Field.of("name", JsonSchemaType.STRING),
        Field.of("test_object", JsonSchemaType.OBJECT, List.of(
            Field.of("name", JsonSchemaType.STRING),
            Field.of("thirdLevelObject", JsonSchemaType.OBJECT, List.of(
                Field.of("data", JsonSchemaType.STRING),
                Field.of("intData", JsonSchemaType.NUMBER))))));

    assertEquals(Jsons.deserialize(expected), actual);
  }

  @Test
  void testGetTopLevelFieldNames() {
    final String json = "{ \"type\": \"object\", \"properties\": { \"name\": { \"type\": \"string\" } } } ";
    final Set<String> actualFieldNames =
        CatalogHelpers.getTopLevelFieldNames(new ConfiguredAirbyteStream().withStream(new AirbyteStream().withJsonSchema(Jsons.deserialize(json))));

    assertEquals(Sets.newHashSet("name"), actualFieldNames);
  }

  @Test
  void testGetFieldNames() throws IOException {
    final JsonNode node = Jsons.deserialize(MoreResources.readResource("valid_schema.json"));
    final Set<String> actualFieldNames = CatalogHelpers.getAllFieldNames(node);
    final List<String> expectedFieldNames =
        List.of("CAD", "DKK", "HKD", "HUF", "ISK", "PHP", "date", "nestedkey", "somekey", "something", "something2", "文");

    // sort so that the diff is easier to read.
    assertEquals(expectedFieldNames.stream().sorted().toList(), actualFieldNames.stream().sorted().toList());
  }

  @Test
  void testGetCatalogDiff() throws IOException {
    final JsonNode schema1 = Jsons.deserialize(MoreResources.readResource("valid_schema.json"));
    final JsonNode schema2 = Jsons.deserialize(MoreResources.readResource("valid_schema2.json"));
    final AirbyteCatalog catalog1 = new AirbyteCatalog().withStreams(List.of(
        new AirbyteStream().withName("users").withJsonSchema(schema1),
        new AirbyteStream().withName("accounts").withJsonSchema(Jsons.emptyObject())));
    final AirbyteCatalog catalog2 = new AirbyteCatalog().withStreams(List.of(
        new AirbyteStream().withName("users").withJsonSchema(schema2),
        new AirbyteStream().withName("sales").withJsonSchema(Jsons.emptyObject())));

    final Set<StreamTransform> actualDiff = CatalogHelpers.getCatalogDiff(catalog1, catalog2);
    final List<StreamTransform> expectedDiff = Stream.of(
        StreamTransform.createAddStreamTransform(new StreamDescriptor().withName("sales")),
        StreamTransform.createRemoveStreamTransform(new StreamDescriptor().withName("accounts")),
        StreamTransform.createUpdateStreamTransform(new StreamDescriptor().withName("users"), new UpdateStreamTransform(Set.of(
            FieldTransform.createAddFieldTransform(List.of("COD"), schema2.get("properties").get("COD")),
            FieldTransform.createRemoveFieldTransform(List.of("something2"), schema1.get("properties").get("something2")),
            FieldTransform.createRemoveFieldTransform(List.of("HKD"), schema1.get("properties").get("HKD")),
            FieldTransform.createUpdateFieldTransform(List.of("CAD"), new UpdateFieldSchemaTransform(
                schema1.get("properties").get("CAD"),
                schema2.get("properties").get("CAD")))))))
        .sorted(STREAM_TRANSFORM_COMPARATOR)
        .toList();
    assertEquals(expectedDiff, actualDiff.stream().sorted(STREAM_TRANSFORM_COMPARATOR).toList());
  }

}
