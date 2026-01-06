/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.datagen.flavor.increment

import io.airbyte.cdk.discover.Field
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
                    Field("id", IntegerFieldType),
                )
        )
    override val primaryKeys = mapOf(incrementTableName to listOf(listOf(("id"))))

    override val dataGenerator = IncrementDataGenerator()
}
