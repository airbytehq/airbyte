/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.getAirbyteValue
import io.airbyte.cdk.load.data.json.toAirbyteValue
import io.airbyte.cdk.load.data.protobuf.toAirbyteValue
import io.airbyte.cdk.load.state.CheckpointId
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.util.*
import kotlin.collections.LinkedHashMap

data class DestinationRecordRaw(
    val stream: DestinationStream,
    val rawData: DestinationRecordSource,
    val serializedSizeBytes: Long,
    val checkpointId: CheckpointId? = null,
    val airbyteRawId: UUID,
) {
    // Currently file transfer is only supported for non-socket implementations
    val fileReference: FileReference? = rawData.fileReference

    val schema = stream.schema

    val schemaFields: SequencedMap<String, FieldType> =
        when (schema) {
            is ObjectType -> schema.properties
            else -> linkedMapOf()
        }

    /**
     * DEPRECATED: Now that we support multiple formats for speed, this is no longer an
     * optimization.
     */
    fun asJsonRecord(): JsonNode = rawData.asJsonRecord(stream.airbyteValueProxyFieldAccessors)

    fun asDestinationRecordAirbyteValue(): DestinationRecordAirbyteValue {
        return DestinationRecordAirbyteValue(
            stream = stream,
            data =
                if (rawData is DestinationRecordProtobufSource) {
                    rawData.toAirbyteValue(stream.airbyteValueProxyFieldAccessors)
                } else asJsonRecord().toAirbyteValue(),
            emittedAtMs = rawData.emittedAtMs,
            meta = rawData.sourceMeta,
        )
    }

    /**
     * Convert this record to an EnrichedRecord. Crucially, after this conversion, all entries in
     * [EnrichedDestinationRecordAirbyteValue.allTypedFields] are guaranteed to have
     * [EnrichedAirbyteValue.abValue] either be [NullValue], or match [EnrichedAirbyteValue.type]
     * (e.g. if `type` is [TimestampTypeWithTimezone], then `value` is either `NullValue`, or
     * [TimestampWithTimezoneValue]).
     */
    fun asEnrichedDestinationRecordAirbyteValue(
        extractedAtAsTimestampWithTimezone: Boolean = false,
        respectLegacyUnions: Boolean = false,
    ): EnrichedDestinationRecordAirbyteValue {
        val proxy = rawData.asAirbyteValueProxy()

        // Get the fields from the schema
        val schemaFields = stream.airbyteValueProxyFieldAccessors
        val declaredFields = LinkedHashMap<String, EnrichedAirbyteValue>()
        val undeclaredFields = LinkedHashMap<String, JsonNode>()

        // Process fields from the raw JSON.
        // First, get the declared fields, in the order defined by the catalog
        schemaFields.forEach { fieldAccessor ->
            if (!proxy.hasField(fieldAccessor)) {
                return@forEach
            }
            val fieldValue = proxy.getAirbyteValue(fieldAccessor)
            val enrichedValue =
                EnrichedAirbyteValue(
                    abValue = fieldValue,
                    type = fieldAccessor.type,
                    name = fieldAccessor.name,
                    airbyteMetaField = null,
                )
            
            if (fieldValue is NullValue) {
                enrichedValue.nullify(
                    AirbyteRecordMessageMetaChange.Reason.DESTINATION_SERIALIZATION_ERROR
                )
            }

            declaredFields[fieldAccessor.name] = enrichedValue
        }

        // Then, get the undeclared fields
        proxy.undeclaredFields(schemaFields).forEach { field ->
            undeclaredFields[field] = proxy.getJsonNode(field)!!
        }

        return EnrichedDestinationRecordAirbyteValue(
            stream = stream,
            declaredFields = declaredFields,
            undeclaredFields = undeclaredFields,
            emittedAtMs = rawData.emittedAtMs,
            sourceMeta = rawData.sourceMeta,
            serializedSizeBytes = serializedSizeBytes,
            extractedAtAsTimestampWithTimezone = extractedAtAsTimestampWithTimezone,
            airbyteRawId = airbyteRawId,
        )
    }

    fun asDestinationRecordAirbyteProxy() {
        TODO("Implement optimized interface here.")
    }
}
