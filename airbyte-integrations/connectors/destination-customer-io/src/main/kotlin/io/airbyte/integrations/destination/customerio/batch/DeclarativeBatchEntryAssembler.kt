package io.airbyte.integrations.destination.customerio.io.airbyte.integrations.destination.customerio.batch

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.interpolation.StringInterpolator
import io.airbyte.cdk.load.interpolation.toInterpolationContext
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.util.Jsons

class DeclarativeBatchEntryAssembler(private val template: String) {

    private val interpolator: StringInterpolator = StringInterpolator()
    private val expectedRecordFields: Set<String> = interpolator.extractAccessedRecordKeys(template)

    fun assemble(record: DestinationRecordRaw): JsonNode {
        val jsonRecord: ObjectNode = record.asJsonRecord() as ObjectNode
        val additionalProperties = Jsons.objectNode().apply {
            jsonRecord.properties().filter { entry -> entry.key !in expectedRecordFields }.forEach { entry -> this.replace(entry.key, entry.value) }
        }
        val entryAsString = interpolator.interpolate(
            template,
            mapOf(
                "record" to jsonRecord.toInterpolationContext(),
                "additional_properties" to additionalProperties.toPrettyString(),
            )
        )
        return Jsons.readTree(entryAsString)
    }

}
