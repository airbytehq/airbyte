/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.avro.toAvroSchema
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertDoesNotThrow

class AirbyteTypeToAvroSchemaTest {
    @Test
    fun `test name mangling`() {
        val schema =
            ObjectType(
                properties =
                    linkedMapOf(
                        "1d_view" to FieldType(type = StringType, nullable = false),
                    )
            )
        val descriptor = DestinationStream.Descriptor("test", "stream")
        assertDoesNotThrow { schema.toAvroSchema(descriptor) }
    }
}
