/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.datagen.flavor

import io.airbyte.cdk.discover.Field

interface Flavor {
    val namespace: String
    val tableNames: Set<String>
    val fields: Map<String, List<Field>>
    val primaryKeys: Map<String, List<List<String>>>
    val dataGenerator: DataGenerator
}
