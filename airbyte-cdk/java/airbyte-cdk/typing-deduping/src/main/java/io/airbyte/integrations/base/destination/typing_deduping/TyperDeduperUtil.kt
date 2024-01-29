package io.airbyte.integrations.base.destination.typing_deduping

import com.google.common.collect.Streams
import java.util.*

/**
 * Extracts all the "raw" and "final" schemas identified in the [parsedCatalog] and ensures they
 * exist in the Destination Database.
 */
fun <T> prepareAllSchemas(parsedCatalog: ParsedCatalog, sqlGenerator: SqlGenerator<T>, destinationHandler: DestinationHandler<T>) {
    val rawSchema =
        parsedCatalog.streams.stream().map { stream: StreamConfig -> stream.id.rawNamespace }
    val finalSchema =
        parsedCatalog.streams.stream().map { stream: StreamConfig -> stream.id.finalNamespace }
    val createAllSchemasSql = Streams.concat(rawSchema, finalSchema)
        .filter { obj: String? -> Objects.nonNull(obj) }
        .distinct()
        .map { schema: String? -> sqlGenerator.createSchema(schema) }
        .toList()
    destinationHandler.execute(Sql.concat(createAllSchemasSql))
}
