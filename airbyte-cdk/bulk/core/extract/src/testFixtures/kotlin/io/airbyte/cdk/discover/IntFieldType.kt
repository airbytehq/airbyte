/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.discover

import io.airbyte.cdk.data.AirbyteType
import io.airbyte.cdk.data.IntCodec
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.LeafAirbyteType

data object IntFieldType : FieldType {
    override val airbyteType: AirbyteType = LeafAirbyteType.INTEGER
    override val jsonEncoder: JsonEncoder<*> = IntCodec
}
