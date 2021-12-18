/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.json;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json_path.JsonPath;
import io.airbyte.commons.json_path.JsonPath.JsonPathBuilder;
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
    final BiConsumer<JsonNode, JsonPath> mock = mock(BiConsumer.class);

    JsonSchemas.traverseJsonSchema(jsonWithAllTypes, mock);
    final InOrder inOrder = Mockito.inOrder(mock);
    inOrder.verify(mock).accept(jsonWithAllTypes, JsonPath.empty());
    inOrder.verify(mock).accept(jsonWithAllTypes.get("properties").get("name"), JsonPathBuilder.builder().addField("name").build());
    inOrder.verify(mock).accept(jsonWithAllTypes.get("properties").get("name").get("properties").get("first"),
        JsonPathBuilder.builder().addField("name").addField("first").build());
    inOrder.verify(mock).accept(jsonWithAllTypes.get("properties").get("name").get("properties").get("last"),
        JsonPathBuilder.builder().addField("name").addField("last").build());
    inOrder.verify(mock).accept(jsonWithAllTypes.get("properties").get("company"), JsonPathBuilder.builder().addField("company").build());
    inOrder.verify(mock).accept(jsonWithAllTypes.get("properties").get("pets"), JsonPathBuilder.builder().addField("pets").build());
    inOrder.verify(mock).accept(jsonWithAllTypes.get("properties").get("pets").get("items"),
        JsonPathBuilder.builder().addField("pets").addListItemWildcard().build());
    inOrder.verify(mock).accept(jsonWithAllTypes.get("properties").get("pets").get("items").get("properties").get("type"),
        JsonPathBuilder.builder().addField("pets").addListItemWildcard().addField("type").build());
    inOrder.verify(mock).accept(jsonWithAllTypes.get("properties").get("pets").get("items").get("properties").get("number"),
        JsonPathBuilder.builder().addField("pets").addListItemWildcard().addField("number").build());
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
    final BiConsumer<JsonNode, JsonPath> mock = mock(BiConsumer.class);

    JsonSchemas.traverseJsonSchema(jsonWithAllTypes, mock);

    final InOrder inOrder = Mockito.inOrder(mock);
    inOrder.verify(mock).accept(jsonWithAllTypes, JsonPath.empty());
    inOrder.verify(mock).accept(jsonWithAllTypes.get(compositeKeyword).get(0), JsonPath.empty());
    inOrder.verify(mock).accept(jsonWithAllTypes.get(compositeKeyword).get(1), JsonPath.empty());
    inOrder.verify(mock).accept(jsonWithAllTypes.get(compositeKeyword).get(1).get("properties").get("prop1"),
        JsonPathBuilder.builder().addField("prop1").build());
    inOrder.verify(mock).accept(jsonWithAllTypes.get(compositeKeyword).get(2), JsonPath.empty());
    inOrder.verify(mock).accept(jsonWithAllTypes.get(compositeKeyword).get(2).get("items"), JsonPathBuilder.builder().addListItemWildcard().build());
    inOrder.verify(mock).accept(jsonWithAllTypes.get(compositeKeyword).get(3).get(compositeKeyword).get(0), JsonPath.empty());
    inOrder.verify(mock).accept(jsonWithAllTypes.get(compositeKeyword).get(3).get(compositeKeyword).get(1), JsonPath.empty());
    inOrder.verify(mock).accept(jsonWithAllTypes.get(compositeKeyword).get(3).get(compositeKeyword).get(1).get("items"),
        JsonPathBuilder.builder().addListItemWildcard().build());
    inOrder.verifyNoMoreInteractions();
  }

  @SuppressWarnings("unchecked")
  @Test
  void testTraverseMultiType() throws IOException {
    final JsonNode jsonWithAllTypes = Jsons.deserialize(MoreResources.readResource("json_schemas/json_with_array_type_fields.json"));
    final BiConsumer<JsonNode, JsonPath> mock = mock(BiConsumer.class);

    JsonSchemas.traverseJsonSchema(jsonWithAllTypes, mock);
    final InOrder inOrder = Mockito.inOrder(mock);
    inOrder.verify(mock).accept(jsonWithAllTypes, JsonPath.empty());
    inOrder.verify(mock).accept(jsonWithAllTypes.get("properties").get("company"), JsonPathBuilder.builder().addField("company").build());
    inOrder.verify(mock).accept(jsonWithAllTypes.get("items"), JsonPathBuilder.builder().addListItemWildcard().build());
    inOrder.verify(mock).accept(jsonWithAllTypes.get("items").get("properties").get("user"),
        JsonPathBuilder.builder().addListItemWildcard().addField("user").build());
    inOrder.verifyNoMoreInteractions();
  }

  @SuppressWarnings("unchecked")
  @Test
  void testTraverseMultiTypeComposite() throws IOException {
    final String compositeKeyword = "anyOf";
    final JsonNode jsonWithAllTypes = Jsons.deserialize(MoreResources.readResource("json_schemas/json_with_array_type_fields_with_composites.json"));
    final BiConsumer<JsonNode, JsonPath> mock = mock(BiConsumer.class);

    JsonSchemas.traverseJsonSchema(jsonWithAllTypes, mock);

    final InOrder inOrder = Mockito.inOrder(mock);
    inOrder.verify(mock).accept(jsonWithAllTypes, JsonPath.empty());
    inOrder.verify(mock).accept(jsonWithAllTypes.get(compositeKeyword).get(0).get("properties").get("company"),
        JsonPathBuilder.builder().addField("company").build());
    inOrder.verify(mock).accept(jsonWithAllTypes.get(compositeKeyword).get(1).get("properties").get("organization"),
        JsonPathBuilder.builder().addField("organization").build());
    inOrder.verify(mock).accept(jsonWithAllTypes.get("items"), JsonPathBuilder.builder().addListItemWildcard().build());
    inOrder.verify(mock).accept(jsonWithAllTypes.get("items").get("properties").get("user"),
        JsonPathBuilder.builder().addListItemWildcard().addField("user").build());
    inOrder.verifyNoMoreInteractions();
  }

}
