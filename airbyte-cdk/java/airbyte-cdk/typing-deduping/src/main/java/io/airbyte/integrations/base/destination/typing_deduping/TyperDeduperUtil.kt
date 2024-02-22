package io.airbyte.integrations.base.destination.typing_deduping


/**
 * Extracts all the "raw" and "final" schemas identified in the [parsedCatalog] and ensures they
 * exist in the Destination Database.
 */
fun prepareAllSchemas(parsedCatalog: ParsedCatalog, sqlGenerator: SqlGenerator, destinationHandler: DestinationHandler) {
    val rawSchema = parsedCatalog.streams.mapNotNull { it.id.rawNamespace }
    val finalSchema = parsedCatalog.streams.mapNotNull { it.id.finalNamespace }
    val createAllSchemasSql = rawSchema.union(finalSchema)
        .map { sqlGenerator.createSchema(it) }
        .toList()
    destinationHandler.execute(Sql.concat(createAllSchemasSql))
}
