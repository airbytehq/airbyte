/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue

// implemented by connectors
class MapperPipeline(
    inputSchema: AirbyteType,
    schemaValueMapperPairs: List<Pair<AirbyteSchemaMapper, AirbyteValueMapper>>,
) {
    private val schemasWithMappers: List<Pair<AirbyteType, AirbyteValueMapper>>

    val finalSchema: AirbyteType

    init {
        val (schemaMappers, valueMappers) = schemaValueMapperPairs.unzip()
        val schemas =
            schemaMappers.runningFold(inputSchema) { schema, mapper -> mapper.map(schema) }
        schemasWithMappers = schemas.zip(valueMappers)
        finalSchema = schemas.last()
    }

    fun map(record: DestinationRecordAirbyteValue): DestinationRecordAirbyteValue =
        record.copy(
            declaredFields =
                record.declaredFields.mapValues { (_, value) -> nullifyLongStrings(value) }
        )

    private fun nullifyLongStrings(value: EnrichedAirbyteValue): EnrichedAirbyteValue {
        return if (
            value.type is StringType && value.value is StringValue && value.value.value.length > 100
        ) {
            value.toTruncated(newValue = StringValue(value.value.value.substring(0, 100)))
        } else {
            value
        }
    }
}

interface MapperPipelineFactory {
    fun create(stream: DestinationStream): MapperPipeline
}
