/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.standardtest.destination.comparator

import com.fasterxml.jackson.databind.JsonNode

interface TestDataComparator {
    fun assertSameData(expected: List<JsonNode>, actual: List<JsonNode>)
}
