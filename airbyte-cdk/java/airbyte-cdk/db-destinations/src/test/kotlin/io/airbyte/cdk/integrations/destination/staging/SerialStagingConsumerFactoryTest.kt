/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.staging

import io.airbyte.cdk.integrations.destination.jdbc.WriteConfig
import io.airbyte.commons.exceptions.ConfigErrorException
import java.util.List
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.mockito.Mockito.mock

internal class SerialStagingConsumerFactoryTest {
    @Test
    fun detectConflictingStreams() {
        val configErrorException =
            Assertions.assertThrows(ConfigErrorException::class.java) {
                SerialFlush.function(
                    null,
                    mock(),
                    List.of(
                        WriteConfig(
                            "example_stream",
                            "source_schema",
                            "destination_default_schema",
                            null,
                            null,
                            mock()
                        ),
                        WriteConfig(
                            "example_stream",
                            "source_schema",
                            "destination_default_schema",
                            null,
                            null,
                            mock()
                        )
                    ),
                    mock(),
                )
            }

        Assertions.assertEquals(
            "You are trying to write multiple streams to the same table. Consider switching to a custom namespace format using \${SOURCE_NAMESPACE}, or moving one of them into a separate connection with a different stream prefix. Affected streams: source_schema.example_stream, source_schema.example_stream",
            configErrorException.message
        )
    }
}
