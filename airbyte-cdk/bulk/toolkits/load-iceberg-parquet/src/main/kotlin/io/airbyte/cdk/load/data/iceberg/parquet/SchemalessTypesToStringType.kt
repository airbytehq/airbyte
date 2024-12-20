/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.iceberg.parquet

import io.airbyte.cdk.load.data.AirbyteSchemaIdentityMapper
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.UnknownType

class SchemalessTypesToStringType : AirbyteSchemaIdentityMapper {
    override fun mapArrayWithoutSchema(schema: ArrayTypeWithoutSchema) = StringType
    override fun mapObjectWithEmptySchema(schema: ObjectTypeWithEmptySchema) = StringType
    override fun mapObjectWithoutSchema(schema: ObjectTypeWithoutSchema) = StringType
    override fun mapUnknown(schema: UnknownType) = StringType
}
