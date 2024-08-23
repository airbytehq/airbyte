package io.airbyte.integrations.base.destination.experimental

import io.airbyte.protocol.models.AirbyteStream
import io.airbyte.protocol.models.ConfiguredAirbyteStream
import io.airbyte.protocol.models.DestinationSyncMode
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertDoesNotThrow
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ArgumentsSource
import org.junit.jupiter.params.provider.ValueSource

abstract class NameHandlingIntegrationTest<Config>(destinationProcessFactory: DestinationProcessFactory<Config>,
                                                   config: Config
) : IntegrationTest<Config>(
    destinationProcessFactory, config
) {

    // I could go either way on the existence of this test / how much it should actually do
    // e.g. maybe it should just assertNotThrows on runSync, instead of doing a full dumpAndDiff.
    // but writing out the whole thing just to see what it looks like
    // (in particular, see SnowflakeNameHandlingIntegrationTest.canonicalRecordToDestinationRecord)
    @Test
    fun testFieldNameCasingCollision() {
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
                    data = """{"id": 42, "fieldsDifferingOnlyInCasing": 1, "FIELDSDIFFERINGONLYINCASING": 2, "fieldsdifferingonlyincasing": 3}""",
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
                        "id" to 42,
                        "fieldsDifferingOnlyInCasing" to 1,
                        "FIELDSDIFFERINGONLYINCASING" to 2,
                        "fieldsdifferingonlyincasing" to 3,
                    ),
                    airbyteMeta = """{"sync_id": 0}""",
                ),
            ),
            canonicalExpectedFinalRecords = listOf(
                ExpectedOutputRecord(
                    extractedAt = 100,
                    generationId = 0,
                    data = mapOf(
                        "id" to 42,
                        "fieldsDifferingOnlyInCasing" to 1,
                        "FIELDSDIFFERINGONLYINCASING" to 2,
                        "fieldsdifferingonlyincasing" to 3,
                    ),
                    airbyteMeta = """{"sync_id": 0}""",
                ),
            ),
            "stream name",
            "stream namespace",
        )
    }

    @ParameterizedTest
    @ValueSource(
        strings = [
            // every special character on a qwerty keyboard
            // (leading space is intentional)
            """ `-=~!@#$%^&*()_+[]\{}|;':",./<>?""",
            // some SQL dialects use this as a string delimiter
            "$$",
            // lol, lmao
            // (test that we support weird unicode stuff)
            "😂",
        ],
    )
    // TODO duplicate for append mode
    fun testWeirdCharsDedup(specialChars: String) {
        // TODO assumeTrue(supports dedup)

        // we don't make strong guarantees about what will happen,
        // but we at least guarantee that we won't crash
        assertDoesNotThrow {
            runSync(
                ConfiguredAirbyteStream()
                    .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
                    .withGenerationId(0)
                    .withMinimumGenerationId(0)
                    .withSyncId(0)
                    .withStream(
                        AirbyteStream()
                            .withName("stream$specialChars")
                            .withNamespace(randomizedNamespace + specialChars)
                            .withJsonSchema(TODO("schema where the column name includes $specialChars")),
                    )
                    .withCursorField(listOf("cursor$specialChars"))
                    .withPrimaryKey(listOf(listOf("pk$specialChars"))),
                records = TODO(),
            )
        }
    }
}
