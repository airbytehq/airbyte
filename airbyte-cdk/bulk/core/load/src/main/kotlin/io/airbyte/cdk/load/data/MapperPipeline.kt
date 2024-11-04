/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationRecord
import kotlin.reflect.KClass

class MapperPipeline(
    inputSchema: AirbyteType,
    schemaValueMapperPairs:
        List<Pair<KClass<out AirbyteSchemaMapper>, KClass<out AirbyteValueMapper>>>,
) {
    private val schemas: List<AirbyteType>
    private val mapperChain: (AirbyteValue, DestinationRecord.Meta) -> AirbyteValue

    val finalSchema: AirbyteType

    init {
        val (schemaMappers, valueMappers) = schemaValueMapperPairs.unzip()
        schemas =
            schemaMappers.runningFold(inputSchema) { schema, mapper ->
                mapper.constructors.first().call().map(schema)
            }
        finalSchema = schemas.last()
        // Build a big ol' monad chain
        mapperChain =
            valueMappers.zip(schemas).fold({ record, _ -> record }) {
                previousMappers,
                (mapper, schema) ->
                { record, meta ->
                    val mapped = previousMappers(record, meta)
                    mapper.constructors.first().call(meta).map(mapped, schema)
                }
            }
    }

    fun map(record: DestinationRecord): DestinationRecord {
        val mapped = mapperChain(record.data, record.meta ?: DestinationRecord.Meta())
        return record.copy(data = mapped) // Meta was mutated in place
    }
}

interface MapperPipelineFactory {
    fun create(stream: DestinationStream): MapperPipeline
}
