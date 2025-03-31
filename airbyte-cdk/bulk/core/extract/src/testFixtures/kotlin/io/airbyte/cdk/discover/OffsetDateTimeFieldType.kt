/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.discover

import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.OffsetDateTimeCodec

data object OffsetDateTimeFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType =
        LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE
    override val jsonEncoder: JsonEncoder<*> = OffsetDateTimeCodec
}
