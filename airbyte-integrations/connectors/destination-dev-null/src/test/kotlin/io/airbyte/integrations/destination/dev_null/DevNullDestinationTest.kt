/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.dev_null

import io.airbyte.commons.json.Jsons
import io.airbyte.commons.resources.MoreResources
import io.airbyte.protocol.models.v0.ConnectorSpecification
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class DevNullDestinationTest {
    @Test
    @Throws(Exception::class)
    fun testSpec() {
        val actual = DevNullDestination().spec()
        val expected =
            Jsons.deserialize(
                MoreResources.readResource("expected_spec.json"),
                ConnectorSpecification::class.java
            )

        Assertions.assertEquals(expected, actual)
    }
}
