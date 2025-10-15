/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.datagen

import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.BigDecimalCodec
import io.airbyte.cdk.data.BigDecimalIntegerCodec
import io.airbyte.cdk.data.BooleanCodec
import io.airbyte.cdk.data.DoubleCodec
import io.airbyte.cdk.data.IntCodec
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.JsonStringCodec
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.LocalDateCodec
import io.airbyte.cdk.data.LocalDateTimeCodec
import io.airbyte.cdk.data.LocalTimeCodec
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.data.OffsetTimeCodec
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.discover.FieldType

data object IntegerFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.INTEGER
    override val jsonEncoder: JsonEncoder<*> = IntCodec
}

data object BigIntegerFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.INTEGER
    override val jsonEncoder: JsonEncoder<*> = BigDecimalIntegerCodec
}

data object NumberFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.NUMBER
    override val jsonEncoder: JsonEncoder<*> = DoubleCodec
}

data object BigDecimalFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.NUMBER
    override val jsonEncoder: JsonEncoder<*> = BigDecimalCodec
}

data object BooleanFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.BOOLEAN
    override val jsonEncoder: JsonEncoder<*> = BooleanCodec
}

data object StringFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.STRING
    override val jsonEncoder: JsonEncoder<*> = TextCodec
}

data object DateFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.DATE
    override val jsonEncoder: JsonEncoder<*> = LocalDateCodec
}

data object TimeWithTimeZoneFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.TIME_WITH_TIMEZONE
    override val jsonEncoder: JsonEncoder<*> = OffsetTimeCodec
}

data object TimeWithoutTimeZoneFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE
    override val jsonEncoder: JsonEncoder<*> = LocalTimeCodec
}

data object TimestampWithTimeZoneFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType =
        LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE
    override val jsonEncoder: JsonEncoder<*> = OffsetDateTimeCodec
}

data object TimestampWithoutTimeZoneFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType =
        LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE
    override val jsonEncoder: JsonEncoder<*> = LocalDateTimeCodec
}

data object JsonFieldType : FieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.JSONB
    override val jsonEncoder: JsonEncoder<*> = JsonStringCodec
}
