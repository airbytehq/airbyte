/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.dev_null

import io.airbyte.cdk.integrations.base.adaptive.AdaptiveSourceRunner
import io.airbyte.commons.features.EnvVariableFeatureFlags
import io.airbyte.commons.features.FeatureFlagsWrapper
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.resources.MoreResources
import io.airbyte.protocol.models.v0.ConnectorSpecification
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class CloudDevNullDestinationTest {
    @Test
    @Throws(Exception::class)
    fun testSpec() {
        val actual =
            TestingDestinations(
                    FeatureFlagsWrapper.overridingDeploymentMode(
                        EnvVariableFeatureFlags(),
                        AdaptiveSourceRunner.CLOUD_MODE
                    )
                )
                .spec()
        val expected =
            Jsons.deserialize(
                MoreResources.readResource("expected_spec_cloud.json"),
                ConnectorSpecification::class.java
            )
        Assertions.assertEquals(expected, actual)
    }
}
