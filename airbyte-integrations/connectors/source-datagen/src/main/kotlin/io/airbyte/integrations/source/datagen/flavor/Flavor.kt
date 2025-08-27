package io.airbyte.integrations.source.datagen.flavor

import io.airbyte.cdk.discover.Field

//
interface Flavor {
    val namespace: String
    val tableNames: Set<String>
    val fields: Map<String, List<Field>>
    val primaryKey: List<String>
    val dataGenerator: DataGenerator
}
