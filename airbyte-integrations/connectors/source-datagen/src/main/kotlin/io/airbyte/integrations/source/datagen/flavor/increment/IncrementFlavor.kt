package io.airbyte.integrations.source.datagen.flavor.increment

import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.integrations.source.datagen.flavor.Flavor

data object IncrementFlavor: Flavor {
    override val namespace = "increment"
    override val tableNames = setOf("increment")
    override val fields = mapOf(
        "increment" to listOf(Field("id", IntFieldType))
    )
    override val primaryKey = listOf("id")
    override val dataGenerator = IncrementDataGenerator()
}
