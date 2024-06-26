/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.mysql

import io.airbyte.commons.features.EnvVariableFeatureFlags
import io.airbyte.commons.features.FeatureFlagsWrapper
import io.airbyte.commons.json.Jsons.deserialize
import io.airbyte.commons.resources.MoreResources.readResource
import io.airbyte.protocol.models.v0.ConnectorSpecification
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class MySqlDestinationCloudTest {
    @Test
    @Throws(Exception::class)
    fun testGetSpec() {
        val dest: MySQLDestination = MySQLDestination()
        dest.featureFlags =
            FeatureFlagsWrapper.overridingDeploymentMode(EnvVariableFeatureFlags(), "CLOUD")
        val spec = dest.spec()
        println(spec.connectionSpecification)
        Assertions.assertEquals(
            deserialize(
                readResource("expected_spec_cloud.json"),
                ConnectorSpecification::class.java
            ),
            spec
        )
    }
}
