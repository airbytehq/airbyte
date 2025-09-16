/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.model.discover

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.databind.JsonNode

/** Base interface for all Airbyte types in declarative destinations. */
@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, include = JsonTypeInfo.As.PROPERTY, property = "type")
@JsonSubTypes(
    JsonSubTypes.Type(value = StringType::class, name = "string"),
    JsonSubTypes.Type(value = BooleanType::class, name = "boolean"),
    JsonSubTypes.Type(value = IntegerType::class, name = "integer"),
    JsonSubTypes.Type(value = NumberType::class, name = "number"),
    JsonSubTypes.Type(value = DateType::class, name = "date"),
    JsonSubTypes.Type(value = TimestampTypeWithTimezone::class, name = "timestamp_with_timezone"),
    JsonSubTypes.Type(
        value = TimestampTypeWithoutTimezone::class,
        name = "timestamp_without_timezone"
    ),
    JsonSubTypes.Type(value = TimeTypeWithTimezone::class, name = "time_with_timezone"),
    JsonSubTypes.Type(value = TimeTypeWithoutTimezone::class, name = "time_without_timezone"),
    JsonSubTypes.Type(value = ArrayType::class, name = "array"),
    JsonSubTypes.Type(value = ArrayTypeWithoutSchema::class, name = "array_without_schema"),
    JsonSubTypes.Type(value = ObjectType::class, name = "object"),
    JsonSubTypes.Type(value = ObjectTypeWithEmptySchema::class, name = "object_with_empty_schema"),
    JsonSubTypes.Type(value = ObjectTypeWithoutSchema::class, name = "object_without_schema"),
    JsonSubTypes.Type(value = UnionType::class, name = "union_type"),
    JsonSubTypes.Type(value = UnknownType::class, name = "unknown_type")
)
sealed interface AirbyteType

data object StringType : AirbyteType

data object BooleanType : AirbyteType

data object IntegerType : AirbyteType

data object NumberType : AirbyteType

data object DateType : AirbyteType

data object TimestampTypeWithTimezone : AirbyteType

data object TimestampTypeWithoutTimezone : AirbyteType

data object TimeTypeWithTimezone : AirbyteType

data object TimeTypeWithoutTimezone : AirbyteType

data class ArrayType(@JsonProperty("items") val items: FieldType) : AirbyteType

data object ArrayTypeWithoutSchema : AirbyteType

data class ObjectType(
    @JsonProperty("properties") val properties: Map<String, FieldType>,
    @JsonProperty("additional_properties") val additionalProperties: Boolean,
    @JsonProperty("required") val required: List<String>? = null,
) : AirbyteType

data object ObjectTypeWithEmptySchema : AirbyteType

data object ObjectTypeWithoutSchema : AirbyteType

data class UnionType(
    @JsonProperty("options") val options: List<AirbyteType>,
    @JsonProperty("is_legacy_union") val isLegacyUnion: Boolean,
) : AirbyteType

data class UnknownType(@JsonProperty("schema") val schema: JsonNode) : AirbyteType

data class FieldType(
    @JsonProperty("type") val type: AirbyteType,
    @JsonProperty("nullable") val nullable: Boolean
)
