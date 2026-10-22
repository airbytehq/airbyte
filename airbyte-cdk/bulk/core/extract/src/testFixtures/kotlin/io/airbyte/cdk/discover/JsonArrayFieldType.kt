/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.discover

import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.ArrayAirbyteSchemaType
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.JsonStringCodec
import io.airbyte.cdk.data.LeafAirbyteSchemaType

/** An array whose elements have no declared type, as a schemaless source discovers them. */
data object JsonArrayFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType =
        ArrayAirbyteSchemaType(LeafAirbyteSchemaType.JSONB)
    override val jsonEncoder: JsonEncoder<*> = JsonStringCodec
}
