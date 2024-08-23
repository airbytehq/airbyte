package io.airbyte.integrations.base.destination.experimental

import io.airbyte.protocol.models.AirbyteStream
import io.airbyte.protocol.models.ConfiguredAirbyteStream
import io.airbyte.protocol.models.DestinationSyncMode
import java.time.ZonedDateTime
import org.junit.Test
import org.junit.jupiter.api.Assumptions.assumeTrue
import org.junit.jupiter.api.assertThrows

enum class BadValueHandling {
    CRASH,
    NULL,
    ACCEPT,
}

abstract class TypingIntegrationTest<Config>(
    destinationProcessFactory: DestinationProcessFactory<Config>,
    config: Config,
    private val rootLevelBadValueHandling: BadValueHandling = BadValueHandling.NULL,
    private val nestedBadValueHandling: BadValueHandling = BadValueHandling.ACCEPT,
) : IntegrationTest<Config>(destinationProcessFactory, config) {

    @Test
    fun testCrashAllTypesRootLevelBadValues() {
        assumeTrue(
            rootLevelBadValueHandling == BadValueHandling.CRASH,
            "Destination supports bad values at the root level of a record",
        )

        assertThrows<Exception> {
            runSync(
                ConfiguredAirbyteStream()
                    .withDestinationSyncMode(DestinationSyncMode.APPEND)
                    .withGenerationId(0)
                    .withMinimumGenerationId(0)
                    .withSyncId(0)
                    .withStream(
                        AirbyteStream()
                            .withName(TODO())
                            .withNamespace(TODO())
                            .withJsonSchema(TODO()),
                    ),
                listOf(
                    InputRecord(
                        extractedAt = 100,
                        generationId = 0,
                        data = """{"id": 42, "integer": "purple", "timestamp": "purple"}""",
                        recordChanges = null,
                    )
                ),
            )
        }
    }

    @Test
    fun testNullAllTypesRootLevelBadValues() {
        assumeTrue(
            rootLevelBadValueHandling == BadValueHandling.NULL,
            "Destination does not null  bad values at the root level of a record",
        )

        runSync(
            ConfiguredAirbyteStream()
                .withDestinationSyncMode(DestinationSyncMode.APPEND)
                .withGenerationId(0)
                .withMinimumGenerationId(0)
                .withSyncId(0)
                .withStream(
                    AirbyteStream()
                        .withName(TODO())
                        .withNamespace(TODO())
                        .withJsonSchema(TODO()),
                ),
            listOf(
                InputRecord(
                    extractedAt = 100,
                    generationId = 0,
                    // some good values, some bad values
                    data = """{"id": 42, "integer": "purple", "timestamp": "2024-01-23T12:34:56Z"}""",
                    recordChanges = null,
                )
            ),
        )

        dumpAndDiffRecords(
            canonicalExpectedRawRecords = listOf(
                ExpectedOutputRecord(
                    extractedAt = 100,
                    generationId = 0,
                    data = mapOf(
                        // raw data always retains all values
                        "id" to 42,
                        "integer" to "purple",
                        "timestamp" to "2024-01-23T12:34:56Z"
                    ),
                    airbyteMeta = """{"sync_id": 0}""",
                ),
            ),
            canonicalExpectedFinalRecords = listOf(
                ExpectedOutputRecord(
                    extractedAt = 100,
                    generationId = 0,
                    // bad values were removed
                    data = mapOf(
                        "id" to 42,
                        "integer" to ZonedDateTime.parse("2024-01-23T12:34:56Z")
                    ),
                    // and we added a bunch of items to airbyte_meta.changes
                    airbyteMeta = """{TODO write the airbyte_meta entries}""",
                )
            ),
            TODO("stream name"),
            TODO("stream namespace"),
        )
    }
}
