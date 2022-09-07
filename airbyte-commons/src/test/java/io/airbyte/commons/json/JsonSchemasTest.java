/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.json;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.JsonSchemas.FieldNameOrList;
import io.airbyte.commons.resources.MoreResources;
import java.io.IOException;
import java.util.Collections;
import java.util.List;
import java.util.function.BiConsumer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.mockito.InOrder;
import org.mockito.Mockito;

@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class JsonSchemasTest {

  private static final String UNCHECKED = "unchecked";
  private static final String NAME = "name";
  private static final String PROPERTIES = "properties";
  private static final String PETS = "pets";
  private static final String COMPANY = "company";
  private static final String ITEMS = "items";
  private static final String USER = "user";

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

  @SuppressWarnings(UNCHECKED)
  @Test
  void testTraverse() throws IOException {
    final JsonNode jsonWithAllTypes = Jsons.deserialize(MoreResources.readResource("json_schemas/json_with_all_types.json"));
    final BiConsumer<JsonNode, List<FieldNameOrList>> mock = mock(BiConsumer.class);

    JsonSchemas.traverseJsonSchema(jsonWithAllTypes, mock);
    final InOrder inOrder = Mockito.inOrder(mock);
    inOrder.verify(mock).accept(jsonWithAllTypes, Collections.emptyList());
    inOrder.verify(mock).accept(jsonWithAllTypes.get(PROPERTIES).get(NAME), List.of(FieldNameOrList.fieldName(NAME)));
    inOrder.verify(mock).accept(jsonWithAllTypes.get(PROPERTIES).get(NAME).get(PROPERTIES).get("first"),
        List.of(FieldNameOrList.fieldName(NAME), FieldNameOrList.fieldName("first")));
    inOrder.verify(mock).accept(jsonWithAllTypes.get(PROPERTIES).get(NAME).get(PROPERTIES).get("last"),
        List.of(FieldNameOrList.fieldName(NAME), FieldNameOrList.fieldName("last")));
    inOrder.verify(mock).accept(jsonWithAllTypes.get(PROPERTIES).get(COMPANY), List.of(FieldNameOrList.fieldName(COMPANY)));
    inOrder.verify(mock).accept(jsonWithAllTypes.get(PROPERTIES).get(PETS), List.of(FieldNameOrList.fieldName(PETS)));
    inOrder.verify(mock).accept(jsonWithAllTypes.get(PROPERTIES).get(PETS).get(ITEMS),
        List.of(FieldNameOrList.fieldName(PETS), FieldNameOrList.list()));
    inOrder.verify(mock).accept(jsonWithAllTypes.get(PROPERTIES).get(PETS).get(ITEMS).get(PROPERTIES).get("type"),
        List.of(FieldNameOrList.fieldName(PETS), FieldNameOrList.list(), FieldNameOrList.fieldName("type")));
    inOrder.verify(mock).accept(jsonWithAllTypes.get(PROPERTIES).get(PETS).get(ITEMS).get(PROPERTIES).get("number"),
        List.of(FieldNameOrList.fieldName(PETS), FieldNameOrList.list(), FieldNameOrList.fieldName("number")));
    inOrder.verifyNoMoreInteractions();
  }

  @SuppressWarnings(UNCHECKED)
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
    final BiConsumer<JsonNode, List<FieldNameOrList>> mock = mock(BiConsumer.class);

    JsonSchemas.traverseJsonSchema(jsonWithAllTypes, mock);

    final InOrder inOrder = Mockito.inOrder(mock);
    inOrder.verify(mock).accept(jsonWithAllTypes, Collections.emptyList());
    inOrder.verify(mock).accept(jsonWithAllTypes.get(compositeKeyword).get(0), Collections.emptyList());
    inOrder.verify(mock).accept(jsonWithAllTypes.get(compositeKeyword).get(1), Collections.emptyList());
    inOrder.verify(mock).accept(jsonWithAllTypes.get(compositeKeyword).get(1).get(PROPERTIES).get("prop1"),
        List.of(FieldNameOrList.fieldName("prop1")));
    inOrder.verify(mock).accept(jsonWithAllTypes.get(compositeKeyword).get(2), Collections.emptyList());
    inOrder.verify(mock).accept(jsonWithAllTypes.get(compositeKeyword).get(2).get(ITEMS), List.of(FieldNameOrList.list()));
    inOrder.verify(mock).accept(jsonWithAllTypes.get(compositeKeyword).get(3).get(compositeKeyword).get(0), Collections.emptyList());
    inOrder.verify(mock).accept(jsonWithAllTypes.get(compositeKeyword).get(3).get(compositeKeyword).get(1), Collections.emptyList());
    inOrder.verify(mock).accept(jsonWithAllTypes.get(compositeKeyword).get(3).get(compositeKeyword).get(1).get(ITEMS),
        List.of(FieldNameOrList.list()));
    inOrder.verifyNoMoreInteractions();
  }

  @SuppressWarnings(UNCHECKED)
  @Test
  void testTraverseMultiType() throws IOException {
    final JsonNode jsonWithAllTypes = Jsons.deserialize(MoreResources.readResource("json_schemas/json_with_array_type_fields.json"));
    final BiConsumer<JsonNode, List<FieldNameOrList>> mock = mock(BiConsumer.class);

    JsonSchemas.traverseJsonSchema(jsonWithAllTypes, mock);
    final InOrder inOrder = Mockito.inOrder(mock);
    inOrder.verify(mock).accept(jsonWithAllTypes, Collections.emptyList());
    inOrder.verify(mock).accept(jsonWithAllTypes.get(PROPERTIES).get(COMPANY), List.of(FieldNameOrList.fieldName(COMPANY)));
    inOrder.verify(mock).accept(jsonWithAllTypes.get(ITEMS), List.of(FieldNameOrList.list()));
    inOrder.verify(mock).accept(jsonWithAllTypes.get(ITEMS).get(PROPERTIES).get(USER),
        List.of(FieldNameOrList.list(), FieldNameOrList.fieldName(USER)));
    inOrder.verifyNoMoreInteractions();
  }

  @SuppressWarnings(UNCHECKED)
  @Test
  void testTraverseMultiTypeComposite() throws IOException {
    final String compositeKeyword = "anyOf";
    final JsonNode jsonWithAllTypes = Jsons.deserialize(MoreResources.readResource("json_schemas/json_with_array_type_fields_with_composites.json"));
    final BiConsumer<JsonNode, List<FieldNameOrList>> mock = mock(BiConsumer.class);

    JsonSchemas.traverseJsonSchema(jsonWithAllTypes, mock);

    final InOrder inOrder = Mockito.inOrder(mock);
    inOrder.verify(mock).accept(jsonWithAllTypes, Collections.emptyList());
    inOrder.verify(mock).accept(jsonWithAllTypes.get(compositeKeyword).get(0).get(PROPERTIES).get(COMPANY),
        List.of(FieldNameOrList.fieldName(COMPANY)));
    inOrder.verify(mock).accept(jsonWithAllTypes.get(compositeKeyword).get(1).get(PROPERTIES).get("organization"),
        List.of(FieldNameOrList.fieldName("organization")));
    inOrder.verify(mock).accept(jsonWithAllTypes.get(ITEMS), List.of(FieldNameOrList.list()));
    inOrder.verify(mock).accept(jsonWithAllTypes.get(ITEMS).get(PROPERTIES).get(USER),
        List.of(FieldNameOrList.list(), FieldNameOrList.fieldName("user")));
    inOrder.verifyNoMoreInteractions();
  }

  @SuppressWarnings(UNCHECKED)
  @Test
  void testTraverseArrayTypeWithNoItemsDoNotThrowsException() throws IOException {
    final JsonNode jsonWithAllTypes = Jsons.deserialize(MoreResources.readResource("json_schemas/json_with_array_type_fields_no_items.json"));
    final BiConsumer<JsonNode, List<FieldNameOrList>> mock = mock(BiConsumer.class);

    JsonSchemas.traverseJsonSchema(jsonWithAllTypes, mock);
  }

}
