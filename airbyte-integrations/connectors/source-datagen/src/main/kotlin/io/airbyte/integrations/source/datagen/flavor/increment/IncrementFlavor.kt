/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.datagen.flavor.increment

import io.airbyte.cdk.discover.EmittedField
import io.airbyte.integrations.source.datagen.IntegerFieldType
import io.airbyte.integrations.source.datagen.flavor.Flavor

data object IncrementFlavor : Flavor {
    val incrementTableName = "increment"

    override val namespace = "increment"
    override val tableNames = setOf(incrementTableName)
    override val fields =
        mapOf(
            incrementTableName to
                listOf(
                    EmittedField("id", IntegerFieldType),
                )
        )
    override val primaryKeys = mapOf(incrementTableName to listOf(listOf(("id"))))

    override val dataGenerator = IncrementDataGenerator()
}
