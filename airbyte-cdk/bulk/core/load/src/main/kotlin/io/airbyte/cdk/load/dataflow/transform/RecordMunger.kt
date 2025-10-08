/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.transform

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.dataflow.transform.medium.JsonConverter
import io.airbyte.cdk.load.dataflow.transform.medium.ProtobufConverter
import io.airbyte.cdk.load.message.DestinationRecordProtobufSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import jakarta.inject.Singleton

/*
 * Munges values and keys into a simple map form. Encapsulates
 * EnrichedAirbyteValue logic from other classes, so it can be replaced if
 * necessary, as we know it's slow. Delegates to JSON or PROTO converters
 * for medium-specific logic.
 *
 * The HashMap construction is deliberate for speed considerations.
 */
@Singleton
class RecordMunger(
    private val jsonConverter: JsonConverter,
    private val protobufConverter: ProtobufConverter
) {
    fun transformForDest(msg: DestinationRecordRaw): Map<String, AirbyteValue> {
        return when (val source = msg.rawData) {
            is DestinationRecordProtobufSource -> protobufConverter.convert(msg, source)
            else -> jsonConverter.convert(msg)
        }
    }
}
