/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.command.MetadataYamlPropertySource
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class PostgresSourceMetadataTest {
    @Test
    fun `maxSecondsBetweenMessages allows four hours between source messages`() {
        val metadata = MetadataYamlPropertySource.loadFromResource()

        assertEquals(
            14400,
            metadata["airbyte.connector.metadata.max-seconds-between-messages"],
        )
    }
}
