/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationRecord.Change

class MapperPipeline(
    inputSchema: AirbyteType,
    schemaValueMapperPairs: List<Pair<AirbyteSchemaMapper, AirbyteValueMapper>>,
) {
    private val schemasWithMappers: List<Pair<AirbyteType, AirbyteValueMapper>>

    val finalSchema: AirbyteType

    init {
        val (schemaMappers, valueMappers) = schemaValueMapperPairs.unzip()
        val schemas =
            schemaMappers.runningFold(inputSchema) { schema, mapper ->
                println("mapping from schema=$schema using mapper=${mapper.javaClass.simpleName}")
                mapper.map(schema)
            }
        schemasWithMappers = schemas.zip(valueMappers)
        finalSchema = schemas.last()
    }

    fun map(data: AirbyteValue, changes: List<Change>? = null): Pair<AirbyteValue, List<Change>> =
        schemasWithMappers.fold(data to (changes ?: emptyList())) {
            (value, changes),
            (schema, mapper) ->
            // TODO: S3V2: Remove before release
            val (valueNext, changesNext) = mapper.map(value, schema, changes)
            println(
                "MapperPipeline.map<${mapper.javaClass.simpleName}>(using schema=$schema): value=$valueNext, changes=$changesNext"
            )
            valueNext to changesNext
        }
}

interface MapperPipelineFactory {
    fun create(stream: DestinationStream): MapperPipeline
}
