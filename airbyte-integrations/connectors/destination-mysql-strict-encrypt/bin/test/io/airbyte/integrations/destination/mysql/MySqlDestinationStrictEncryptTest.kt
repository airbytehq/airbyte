/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.mysql

import io.airbyte.commons.json.Jsons.deserialize
import io.airbyte.commons.resources.MoreResources.readResource
import io.airbyte.protocol.models.v0.ConnectorSpecification
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class MySqlDestinationStrictEncryptTest {
    @Test
    @Throws(Exception::class)
    fun testGetSpec() {
        println(MySQLDestinationStrictEncrypt().spec().connectionSpecification)
        Assertions.assertEquals(
            deserialize(readResource("expected_spec.json"), ConnectorSpecification::class.java),
            MySQLDestinationStrictEncrypt().spec()
        )
    }
}
