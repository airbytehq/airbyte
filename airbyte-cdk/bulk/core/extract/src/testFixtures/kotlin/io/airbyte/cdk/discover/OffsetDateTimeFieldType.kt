/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.discover

import io.airbyte.cdk.data.AirbyteType
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.LeafAirbyteType
import io.airbyte.cdk.data.OffsetDateTimeCodec

data object OffsetDateTimeFieldType : FieldType {
    override val airbyteType: AirbyteType = LeafAirbyteType.TIMESTAMP_WITH_TIMEZONE
    override val jsonEncoder: JsonEncoder<*> = OffsetDateTimeCodec
}
