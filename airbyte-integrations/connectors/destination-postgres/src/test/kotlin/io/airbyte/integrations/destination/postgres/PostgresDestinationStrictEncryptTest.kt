/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres

import io.airbyte.commons.features.EnvVariableFeatureFlags
import io.airbyte.commons.features.FeatureFlagsWrapper
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.resources.MoreResources
import io.airbyte.protocol.models.v0.ConnectorSpecification
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class PostgresDestinationStrictEncryptTest {
    @Test
    @Throws(Exception::class)
    fun testGetSpec() {
        val dest =
            PostgresDestination.sshWrappedDestination(
                FeatureFlagsWrapper.overridingDeploymentMode(EnvVariableFeatureFlags(), "CLOUD")
            )

        Assertions.assertEquals(
            Jsons.deserialize(
                MoreResources.readResource("expected_spec_strict_encrypt.json"),
                ConnectorSpecification::class.java
            ),
            dest.spec()
        )
    }
}
