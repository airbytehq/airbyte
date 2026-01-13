/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.test.util.Root
import io.airbyte.cdk.load.test.util.SchemaRecordBuilder
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class AirbyteSchemaIdentityMapperTest {
    @Test
    fun testIdMapping() {
        val (inputSchema, expectedOutput) =
            SchemaRecordBuilder<Root>()
                .with(DateType)
                .with(StringType)
                .with(IntegerType)
                .with(BooleanType)
                .with(NumberType)
                .with(ArrayType(FieldType(StringType, true)))
                .with(UnionType.of(StringType, IntegerType))
                .withRecord()
                .with(TimeTypeWithTimezone)
                .with(TimeTypeWithoutTimezone)
                .with(TimestampTypeWithTimezone)
                .with(TimestampTypeWithoutTimezone)
                .withRecord()
                .with(ObjectTypeWithoutSchema)
                .with(ObjectTypeWithEmptySchema)
                .with(ArrayTypeWithoutSchema)
                .endRecord()
                .endRecord()
                .build()

        val mapper = object : AirbyteSchemaIdentityMapper {}
        Assertions.assertEquals(expectedOutput, mapper.map(inputSchema))
    }
}
