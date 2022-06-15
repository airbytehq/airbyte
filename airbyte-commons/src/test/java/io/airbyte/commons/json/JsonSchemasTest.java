/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.json;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.resources.MoreResources;
import java.io.IOException;
import java.util.function.BiConsumer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.mockito.InOrder;
import org.mockito.Mockito;

class JsonSchemasTest {

  @Test
  void testMutateTypeToArrayStandard() {
    final JsonNode expectedWithoutType = Jsons.deserialize("{\"test\":\"abc\"}");
    final JsonNode actualWithoutType = Jsons.clone(expectedWithoutType);
    JsonSchemas.mutateTypeToArrayStandard(expectedWithoutType);
    assertEquals(expectedWithoutType, actualWithoutType);

    final JsonNode expectedWithArrayType = Jsons.deserialize("{\"test\":\"abc\", \"type\":[\"object\"]}");
    final JsonNode actualWithArrayType = Jsons.clone(expectedWithArrayType);
    JsonSchemas.mutateTypeToArrayStandard(actualWithArrayType);
    assertEquals(expectedWithoutType, actualWithoutType);

    final JsonNode expectedWithoutArrayType = Jsons.deserialize("{\"test\":\"abc\", \"type\":[\"object\"]}");
    final JsonNode actualWithStringType = Jsons.deserialize("{\"test\":\"abc\", \"type\":\"object\"}");
    JsonSchemas.mutateTypeToArrayStandard(actualWithStringType);
    assertEquals(expectedWithoutArrayType, actualWithStringType);
  }

  @SuppressWarnings("unchecked")
  @Test
  void testTraverse() throws IOException {
    final JsonNode jsonWithAllTypes = Jsons.deserialize(MoreResources.readResource("json_schemas/json_with_all_types.json"));
    final BiConsumer<JsonNode, String> mock = mock(BiConsumer.class);

    JsonSchemas.traverseJsonSchema(jsonWithAllTypes, mock);
    final InOrder inOrder = Mockito.inOrder(mock);
    inOrder.verify(mock).accept(jsonWithAllTypes, JsonPaths.empty());
    inOrder.verify(mock).accept(jsonWithAllTypes.get("properties").get("name"), "$.name");
    inOrder.verify(mock).accept(jsonWithAllTypes.get("properties").get("name").get("properties").get("first"), "$.name.first");
    inOrder.verify(mock).accept(jsonWithAllTypes.get("properties").get("name").get("properties").get("last"), "$.name.last");
    inOrder.verify(mock).accept(jsonWithAllTypes.get("properties").get("company"), "$.company");
    inOrder.verify(mock).accept(jsonWithAllTypes.get("properties").get("pets"), "$.pets");
    inOrder.verify(mock).accept(jsonWithAllTypes.get("properties").get("pets").get("items"), "$.pets[*]");
    inOrder.verify(mock).accept(jsonWithAllTypes.get("properties").get("pets").get("items").get("properties").get("type"), "$.pets[*].type");
    inOrder.verify(mock).accept(jsonWithAllTypes.get("properties").get("pets").get("items").get("properties").get("number"), "$.pets[*].number");
    inOrder.verifyNoMoreInteractions();
  }

  @SuppressWarnings("unchecked")
  @ValueSource(strings = {
    "anyOf",
    "oneOf",
    "allOf"
  })
  @ParameterizedTest
  void testTraverseComposite(final String compositeKeyword) throws IOException {
    final String jsonSchemaString = MoreResources.readResource("json_schemas/composite_json_schema.json")
        .replaceAll("<composite-placeholder>", compositeKeyword);
    final JsonNode jsonWithAllTypes = Jsons.deserialize(jsonSchemaString);
    final BiConsumer<JsonNode, String> mock = mock(BiConsumer.class);

    JsonSchemas.traverseJsonSchema(jsonWithAllTypes, mock);

    final InOrder inOrder = Mockito.inOrder(mock);
    inOrder.verify(mock).accept(jsonWithAllTypes, JsonPaths.empty());
    inOrder.verify(mock).accept(jsonWithAllTypes.get(compositeKeyword).get(0), JsonPaths.empty());
    inOrder.verify(mock).accept(jsonWithAllTypes.get(compositeKeyword).get(1), JsonPaths.empty());
    inOrder.verify(mock).accept(jsonWithAllTypes.get(compositeKeyword).get(1).get("properties").get("prop1"), "$.prop1");
    inOrder.verify(mock).accept(jsonWithAllTypes.get(compositeKeyword).get(2), JsonPaths.empty());
    inOrder.verify(mock).accept(jsonWithAllTypes.get(compositeKeyword).get(2).get("items"), "$[*]");
    inOrder.verify(mock).accept(jsonWithAllTypes.get(compositeKeyword).get(3).get(compositeKeyword).get(0), JsonPaths.empty());
    inOrder.verify(mock).accept(jsonWithAllTypes.get(compositeKeyword).get(3).get(compositeKeyword).get(1), JsonPaths.empty());
    inOrder.verify(mock).accept(jsonWithAllTypes.get(compositeKeyword).get(3).get(compositeKeyword).get(1).get("items"), "$[*]");
    inOrder.verifyNoMoreInteractions();
  }

  @SuppressWarnings("unchecked")
  @Test
  void testTraverseMultiType() throws IOException {
    final JsonNode jsonWithAllTypes = Jsons.deserialize(MoreResources.readResource("json_schemas/json_with_array_type_fields.json"));
    final BiConsumer<JsonNode, String> mock = mock(BiConsumer.class);

    JsonSchemas.traverseJsonSchema(jsonWithAllTypes, mock);
    final InOrder inOrder = Mockito.inOrder(mock);
    inOrder.verify(mock).accept(jsonWithAllTypes, JsonPaths.empty());
    inOrder.verify(mock).accept(jsonWithAllTypes.get("properties").get("company"), "$.company");
    inOrder.verify(mock).accept(jsonWithAllTypes.get("items"), "$[*]");
    inOrder.verify(mock).accept(jsonWithAllTypes.get("items").get("properties").get("user"), "$[*].user");
    inOrder.verifyNoMoreInteractions();
  }

  @SuppressWarnings("unchecked")
  @Test
  void testTraverseMultiTypeComposite() throws IOException {
    final String compositeKeyword = "anyOf";
    final JsonNode jsonWithAllTypes = Jsons.deserialize(MoreResources.readResource("json_schemas/json_with_array_type_fields_with_composites.json"));
    final BiConsumer<JsonNode, String> mock = mock(BiConsumer.class);

    JsonSchemas.traverseJsonSchema(jsonWithAllTypes, mock);

    final InOrder inOrder = Mockito.inOrder(mock);
    inOrder.verify(mock).accept(jsonWithAllTypes, JsonPaths.empty());
    inOrder.verify(mock).accept(jsonWithAllTypes.get(compositeKeyword).get(0).get("properties").get("company"), "$.company");
    inOrder.verify(mock).accept(jsonWithAllTypes.get(compositeKeyword).get(1).get("properties").get("organization"), "$.organization");
    inOrder.verify(mock).accept(jsonWithAllTypes.get("items"), "$[*]");
    inOrder.verify(mock).accept(jsonWithAllTypes.get("items").get("properties").get("user"), "$[*].user");
    inOrder.verifyNoMoreInteractions();
  }

}
