/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

class NullableToUnionNull : AirbyteSchemaIdentityMapper {
    override fun mapField(field: FieldType): FieldType {
        if (field.nullable) {
            return FieldType(UnionType(listOf(field.type, NullType)), nullable = false)
        }
        return field
    }
}
