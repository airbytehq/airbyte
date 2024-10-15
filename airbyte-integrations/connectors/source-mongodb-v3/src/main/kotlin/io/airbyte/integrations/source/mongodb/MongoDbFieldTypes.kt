/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb

import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.BinaryCodec
import io.airbyte.cdk.data.BooleanCodec
import io.airbyte.cdk.data.JsonDecoder
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.JsonStringCodec
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.NullCodec
import io.airbyte.cdk.discover.LosslessFieldType
import java.nio.ByteBuffer

data object MongoBooleanFieldType : LosslessFieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.BOOLEAN
    override val jsonEncoder: JsonEncoder<Boolean> = BooleanCodec
    override val jsonDecoder: JsonDecoder<Boolean> = BooleanCodec
}

data object MongoNumberFieldType : LosslessFieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.NUMBER
    override val jsonEncoder: JsonEncoder<Boolean> = BooleanCodec
    override val jsonDecoder: JsonDecoder<Boolean> = BooleanCodec
}

data object MongoNullFieldType : LosslessFieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.NULL
    override val jsonEncoder: JsonEncoder<Any?> = NullCodec
    override val jsonDecoder: JsonDecoder<Any?> = NullCodec
}

data object MongoStringFieldType : LosslessFieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.STRING
    override val jsonEncoder: JsonEncoder<String> = JsonStringCodec
    override val jsonDecoder: JsonDecoder<String> = JsonStringCodec
}

data object MongoObjectFieldType : LosslessFieldType {
    override val airbyteSchemaType: AirbyteSchemaType = LeafAirbyteSchemaType.BINARY
    override val jsonEncoder: JsonEncoder<ByteBuffer> = BinaryCodec
    override val jsonDecoder: JsonDecoder<ByteBuffer> = BinaryCodec
}
