/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.json

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.commons.resources.MoreResources
import java.io.IOException
import java.util.function.BiConsumer
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource
import org.mockito.Mockito
import org.mockito.kotlin.mock

internal class JsonSchemasTest {
    @Test
    fun testMutateTypeToArrayStandard() {
        val expectedWithoutType = Jsons.deserialize("{\"test\":\"abc\"}")
        val actualWithoutType = Jsons.clone(expectedWithoutType)
        JsonSchemas.mutateTypeToArrayStandard(expectedWithoutType)
        Assertions.assertEquals(expectedWithoutType, actualWithoutType)

        val expectedWithArrayType = Jsons.deserialize("{\"test\":\"abc\", \"type\":[\"object\"]}")
        val actualWithArrayType = Jsons.clone(expectedWithArrayType)
        JsonSchemas.mutateTypeToArrayStandard(actualWithArrayType)
        Assertions.assertEquals(expectedWithoutType, actualWithoutType)

        val expectedWithoutArrayType =
            Jsons.deserialize("{\"test\":\"abc\", \"type\":[\"object\"]}")
        val actualWithStringType = Jsons.deserialize("{\"test\":\"abc\", \"type\":\"object\"}")
        JsonSchemas.mutateTypeToArrayStandard(actualWithStringType)
        Assertions.assertEquals(expectedWithoutArrayType, actualWithStringType)
    }

    @Test
    @Throws(IOException::class)
    fun testTraverse() {
        val jsonWithAllTypes =
            Jsons.deserialize(MoreResources.readResource("json_schemas/json_with_all_types.json"))
        val mock: BiConsumer<JsonNode, List<JsonSchemas.FieldNameOrList>> = mock()

        JsonSchemas.traverseJsonSchema(jsonWithAllTypes, mock)
        val inOrder = Mockito.inOrder(mock)
        inOrder.verify(mock).accept(jsonWithAllTypes, emptyList())
        inOrder
            .verify(mock)
            .accept(
                jsonWithAllTypes[PROPERTIES][NAME],
                java.util.List.of(JsonSchemas.FieldNameOrList.fieldName(NAME))
            )
        inOrder
            .verify(mock)
            .accept(
                jsonWithAllTypes[PROPERTIES][NAME][PROPERTIES]["first"],
                java.util.List.of(
                    JsonSchemas.FieldNameOrList.fieldName(NAME),
                    JsonSchemas.FieldNameOrList.fieldName("first")
                )
            )
        inOrder
            .verify(mock)
            .accept(
                jsonWithAllTypes[PROPERTIES][NAME][PROPERTIES]["last"],
                java.util.List.of(
                    JsonSchemas.FieldNameOrList.fieldName(NAME),
                    JsonSchemas.FieldNameOrList.fieldName("last")
                )
            )
        inOrder
            .verify(mock)
            .accept(
                jsonWithAllTypes[PROPERTIES][COMPANY],
                java.util.List.of(JsonSchemas.FieldNameOrList.fieldName(COMPANY))
            )
        inOrder
            .verify(mock)
            .accept(
                jsonWithAllTypes[PROPERTIES][PETS],
                java.util.List.of(JsonSchemas.FieldNameOrList.fieldName(PETS))
            )
        inOrder
            .verify(mock)
            .accept(
                jsonWithAllTypes[PROPERTIES][PETS][ITEMS],
                java.util.List.of(
                    JsonSchemas.FieldNameOrList.fieldName(PETS),
                    JsonSchemas.FieldNameOrList.list()
                )
            )
        inOrder
            .verify(mock)
            .accept(
                jsonWithAllTypes[PROPERTIES][PETS][ITEMS][PROPERTIES]["type"],
                java.util.List.of(
                    JsonSchemas.FieldNameOrList.fieldName(PETS),
                    JsonSchemas.FieldNameOrList.list(),
                    JsonSchemas.FieldNameOrList.fieldName("type")
                )
            )
        inOrder
            .verify(mock)
            .accept(
                jsonWithAllTypes[PROPERTIES][PETS][ITEMS][PROPERTIES]["number"],
                java.util.List.of(
                    JsonSchemas.FieldNameOrList.fieldName(PETS),
                    JsonSchemas.FieldNameOrList.list(),
                    JsonSchemas.FieldNameOrList.fieldName("number")
                )
            )
        inOrder.verifyNoMoreInteractions()
    }

    @ValueSource(strings = ["anyOf", "oneOf", "allOf"])
    @ParameterizedTest
    @Throws(IOException::class)
    fun testTraverseComposite(compositeKeyword: String) {
        val jsonSchemaString =
            MoreResources.readResource("json_schemas/composite_json_schema.json")
                .replace("<composite-placeholder>".toRegex(), compositeKeyword)
        val jsonWithAllTypes = Jsons.deserialize(jsonSchemaString)
        val mock: BiConsumer<JsonNode, List<JsonSchemas.FieldNameOrList>> = mock()

        JsonSchemas.traverseJsonSchema(jsonWithAllTypes, mock)

        val inOrder = Mockito.inOrder(mock)
        inOrder.verify(mock).accept(jsonWithAllTypes, emptyList())
        inOrder.verify(mock).accept(jsonWithAllTypes[compositeKeyword][0], emptyList())
        inOrder.verify(mock).accept(jsonWithAllTypes[compositeKeyword][1], emptyList())
        inOrder
            .verify(mock)
            .accept(
                jsonWithAllTypes[compositeKeyword][1][PROPERTIES]["prop1"],
                java.util.List.of(JsonSchemas.FieldNameOrList.fieldName("prop1"))
            )
        inOrder.verify(mock).accept(jsonWithAllTypes[compositeKeyword][2], emptyList())
        inOrder
            .verify(mock)
            .accept(
                jsonWithAllTypes[compositeKeyword][2][ITEMS],
                java.util.List.of(JsonSchemas.FieldNameOrList.list())
            )
        inOrder
            .verify(mock)
            .accept(jsonWithAllTypes[compositeKeyword][3][compositeKeyword][0], emptyList())
        inOrder
            .verify(mock)
            .accept(jsonWithAllTypes[compositeKeyword][3][compositeKeyword][1], emptyList())
        inOrder
            .verify(mock)
            .accept(
                jsonWithAllTypes[compositeKeyword][3][compositeKeyword][1][ITEMS],
                java.util.List.of(JsonSchemas.FieldNameOrList.list())
            )
        inOrder.verifyNoMoreInteractions()
    }

    @Test
    @Throws(IOException::class)
    fun testTraverseMultiType() {
        val jsonWithAllTypes =
            Jsons.deserialize(
                MoreResources.readResource("json_schemas/json_with_array_type_fields.json")
            )
        val mock: BiConsumer<JsonNode, List<JsonSchemas.FieldNameOrList>> = mock()

        JsonSchemas.traverseJsonSchema(jsonWithAllTypes, mock)
        val inOrder = Mockito.inOrder(mock)
        inOrder.verify(mock).accept(jsonWithAllTypes, emptyList())
        inOrder
            .verify(mock)
            .accept(
                jsonWithAllTypes[PROPERTIES][COMPANY],
                java.util.List.of(JsonSchemas.FieldNameOrList.fieldName(COMPANY))
            )
        inOrder
            .verify(mock)
            .accept(jsonWithAllTypes[ITEMS], java.util.List.of(JsonSchemas.FieldNameOrList.list()))
        inOrder
            .verify(mock)
            .accept(
                jsonWithAllTypes[ITEMS][PROPERTIES][USER],
                java.util.List.of(
                    JsonSchemas.FieldNameOrList.list(),
                    JsonSchemas.FieldNameOrList.fieldName(USER)
                )
            )
        inOrder.verifyNoMoreInteractions()
    }

    @Test
    @Throws(IOException::class)
    fun testTraverseMultiTypeComposite() {
        val compositeKeyword = "anyOf"
        val jsonWithAllTypes =
            Jsons.deserialize(
                MoreResources.readResource(
                    "json_schemas/json_with_array_type_fields_with_composites.json"
                )
            )
        val mock: BiConsumer<JsonNode, List<JsonSchemas.FieldNameOrList>> = mock()

        JsonSchemas.traverseJsonSchema(jsonWithAllTypes, mock)

        val inOrder = Mockito.inOrder(mock)
        inOrder.verify(mock).accept(jsonWithAllTypes, emptyList())
        inOrder
            .verify(mock)
            .accept(
                jsonWithAllTypes[compositeKeyword][0][PROPERTIES][COMPANY],
                java.util.List.of(JsonSchemas.FieldNameOrList.fieldName(COMPANY))
            )
        inOrder
            .verify(mock)
            .accept(
                jsonWithAllTypes[compositeKeyword][1][PROPERTIES]["organization"],
                java.util.List.of(JsonSchemas.FieldNameOrList.fieldName("organization"))
            )
        inOrder
            .verify(mock)
            .accept(jsonWithAllTypes[ITEMS], java.util.List.of(JsonSchemas.FieldNameOrList.list()))
        inOrder
            .verify(mock)
            .accept(
                jsonWithAllTypes[ITEMS][PROPERTIES][USER],
                java.util.List.of(
                    JsonSchemas.FieldNameOrList.list(),
                    JsonSchemas.FieldNameOrList.fieldName("user")
                )
            )
        inOrder.verifyNoMoreInteractions()
    }

    @Test
    @Throws(IOException::class)
    fun testTraverseArrayTypeWithNoItemsDoNotThrowsException() {
        val jsonWithAllTypes =
            Jsons.deserialize(
                MoreResources.readResource("json_schemas/json_with_array_type_fields_no_items.json")
            )
        val mock: BiConsumer<JsonNode, List<JsonSchemas.FieldNameOrList>> = mock()

        JsonSchemas.traverseJsonSchema(jsonWithAllTypes, mock)
    }

    companion object {
        private const val UNCHECKED = "unchecked"
        private const val NAME = "name"
        private const val PROPERTIES = "properties"
        private const val PETS = "pets"
        private const val COMPANY = "company"
        private const val ITEMS = "items"
        private const val USER = "user"
    }
}
