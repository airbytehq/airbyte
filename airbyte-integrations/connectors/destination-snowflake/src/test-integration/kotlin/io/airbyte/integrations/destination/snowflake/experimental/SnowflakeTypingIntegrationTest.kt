package io.airbyte.integrations.destination.snowflake.experimental

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.base.destination.experimental.DestinationProcessFactory
import io.airbyte.integrations.base.destination.experimental.ExpectedOutputRecord
import io.airbyte.integrations.base.destination.experimental.OutputRecord
import io.airbyte.integrations.base.destination.experimental.TypingIntegrationTest
import java.time.Instant
import java.time.ZonedDateTime
import java.util.UUID

// micronaut can magically inject this stuff...?
// TODO how can we mangle `config` to have a random default_schema param,
//   and enforce that on all test classes
// TODO use a real config object instead of JsonNode
class SnowflakeTypingIntegrationTest(destinationProcessFactory: DestinationProcessFactory<JsonNode>,
                                     config: JsonNode
) : TypingIntegrationTest<JsonNode>(
    destinationProcessFactory, config
) {
    // These methods should probably be defined in some snowflake utility class,
    // and maybe actually injected instead of inherited
    override fun dumpFinalRecords(
        streamName: String,
        streamNamespace: String?
    ): List<OutputRecord> {
        // TODO actually query snowflake, but return strongly-typed stuff
        // e.g.:
        return listOf(
            OutputRecord(
                // destination implementers now need to actually extract the
                // airbyte fields explicitly
                rawId = UUID.randomUUID(),
                extractedAt = Instant.now(),
                loadedAt = Instant.now(),
                generationId = 42L,
                // !! no more testing against jsonnode. destination implementers
                // should return a strongly-typed map.
                // this is very doable with JDBC (though our JdbcDatabase class makes it annoying);
                // I would assume it's also possible with avro.
                data = mapOf(
                    "id" to 42L,
                    "updated_at" to ZonedDateTime.parse("2024-01-23T12:34:56Z"),
                    // note: no airbyte_* fields in here!
                    // destination implementers need to filter that stuff out.
                ),
                // airbyte meta is still a json blob... that's probably fine?
                airbyteMeta = Jsons.deserialize("""{"sync_id": 42}"""),
            ),
        )
    }

    override fun dumpRawRecords(streamName: String, streamNamespace: String?): List<OutputRecord> {
        // TODO actually query the db
        return listOf(
            OutputRecord(
                rawId = UUID.randomUUID(),
                extractedAt = Instant.now(),
                loadedAt = Instant.now(),
                generationId = 42L,
                // unlike final records, where we require actual types,
                // raw records are just the original json blob.
                // arguably, this should be a separate class RawOutputRecord?
                data = mapOf(
                    "id" to 42L,
                    "updated_at" to "2024-01-23T12:34:56Z",
                ),
                airbyteMeta = Jsons.deserialize("""{"sync_id": 42}"""),
            ),
        )
    }

    override fun canonicalRecordToDestinationRecord(expectedRecord: ExpectedOutputRecord): ExpectedOutputRecord {
        return expectedRecord.copy(
            data = expectedRecord.data.let {
                // Snowflake upcases all column names
                it.mapKeys { (k, _) -> k.uppercase() }
                // no need to do anything with timestamps - dumpRecords already converts to
                // ZonedDateTime, LocalDateTime, etc.
            }
        )
    }

    override fun cleanUpOldTestOutputs() {
        TODO("Not yet implemented")
        // search and destroy any schemas/tables where the name resembles "test_stream_2024_01_23_arst"
    }
}
