package io.airbyte.integrations.destination.snowflake.experimental

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.integrations.base.destination.experimental.DestinationProcessFactory
import io.airbyte.integrations.base.destination.experimental.ExpectedOutputRecord
import io.airbyte.integrations.base.destination.experimental.NameHandlingIntegrationTest

class SnowflakeNameHandlingIntegrationTest(
    destinationProcessFactory: DestinationProcessFactory<JsonNode>,
    config: JsonNode
) : NameHandlingIntegrationTest<JsonNode>(
    destinationProcessFactory, config,
) {
    override fun canonicalRecordToDestinationRecord(expectedRecord: ExpectedOutputRecord): ExpectedOutputRecord {
        return expectedRecord.copy(
            data = expectedRecord.data.let {
                it.mapKeys { (k, _) ->
                    when (testInfo.testMethod.get().name) {
                        "testFieldNameCasingCollision" -> {
                            when (k) {
                                // Hardcode specific field renamings for this test case.
                                // (I forget what our actual collision-handling logic would do, these are
                                // just placeholder values)
                                "fieldsDifferingOnlyInCasing" -> "FIELDSDIFFERINGONLYINCASING_THE_FIRST"
                                "FIELDSDIFFERINGONLYINCASING" -> "FIELDSDIFFERINGONLYINCASING_THE_SECOND"
                                "fieldsdifferingonlyincasing" -> "FIELDSDIFFERINGONLYINCASING_THE_THIRD"
                                else -> k
                            }
                        }
                        else -> k
                    }
                }.mapKeys { (k, _) ->
                    // Snowflake upcases all column names
                    k.uppercase()
                }
            },
        )
    }
}
