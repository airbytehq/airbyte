/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.discover

import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.IntCodec
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.LeafAirbyteSchemaType

data object IntFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.INTEGER
    override val jsonEncoder: JsonEncoder<*> = IntCodec
}
