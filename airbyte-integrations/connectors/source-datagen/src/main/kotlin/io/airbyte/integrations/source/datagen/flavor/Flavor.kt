/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.datagen.flavor

import io.airbyte.cdk.discover.Field

interface Flavor {
    val namespace: String
    var tableNames: Set<String>
    var fields: Map<String, List<Field>>
    var primaryKey: List<String>
    val dataGenerator: DataGenerator
}
