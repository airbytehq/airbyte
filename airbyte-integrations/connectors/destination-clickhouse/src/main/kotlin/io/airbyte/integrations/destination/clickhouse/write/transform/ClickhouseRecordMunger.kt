/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.write.transform

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.dataflow.transform.DataMunger
import io.airbyte.cdk.load.dataflow.transform.ProtobufToAirbyteConverter
import io.airbyte.cdk.load.message.DestinationRecordProtobufSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import jakarta.inject.Singleton

/*
 * Munges values and keys into a simple map form. Encapsulates
 * EnrichedAirbyteValue logic from other classes, so it can be replaced if
 * necessary, as we know it's slow.
 *
 * The HashMap construction is deliberate for speed considerations.
 */
@Singleton
class ClickhouseRecordMunger(
    private val catalogInfo: TableCatalog,
    private val coercer: ClickhouseCoercer,
) : DataMunger {
    private val protobufConverter = ProtobufToAirbyteConverter(ClickhouseFieldValidator())
    override fun transformForDest(msg: DestinationRecordRaw): Map<String, AirbyteValue> {
        return when (val source = msg.rawData) {
            is DestinationRecordProtobufSource -> transformProtobuf(msg, source)
            else -> transformEnrichedLegacy(msg)
        }
    }

    private fun transformEnrichedLegacy(msg: DestinationRecordRaw): HashMap<String, AirbyteValue> {
        // this actually munges and coerces data
        val enriched =
            msg.asEnrichedDestinationRecordAirbyteValue(extractedAtAsTimestampWithTimezone = true)

        val munged = HashMap<String, AirbyteValue>()
        enriched.declaredFields.forEach { field ->
            val mappedKey = catalogInfo.getMappedColumnName(msg.stream, field.key)!!
            val fieldType = msg.schemaFields[field.key]!!

            var mappedValue =
                field.value
                    .let { if (fieldType.type is UnionType) coercer.toJsonStringValue(it) else it }
                    .let { coercer.validate(it) }

            mappedValue = coercer.validate(mappedValue)

            munged[mappedKey] = mappedValue.abValue
        }
        // must be called second so it picks up any meta changes from above
        enriched.airbyteMetaFields.forEach { munged[it.key] = it.value.abValue }

        return munged
    }

    private fun transformProtobuf(
        msg: DestinationRecordRaw,
        source: DestinationRecordProtobufSource
    ): Map<String, AirbyteValue> {
        val stream = msg.stream
        val proxy = source.asAirbyteValueProxy()

        val fieldAccessors = stream.airbyteValueProxyFieldAccessors

        val result = HashMap<String, AirbyteValue>(stream.airbyteValueProxyFieldAccessors.size)
        val parsingFailures = mutableListOf<Meta.Change>()

        fieldAccessors.forEach { accessor ->
            val mappedColumnName =
                catalogInfo.getMappedColumnName(stream, accessor.name) ?: return@forEach

            val extractionResult = protobufConverter.extractFieldWithValidation(proxy, accessor)
            if (extractionResult.parsingError != null) {
                parsingFailures.add(extractionResult.parsingError!!)
            }

            if (extractionResult.value != null) {
                result[mappedColumnName] = extractionResult.value!!
            } else if (accessor.type !is UnknownType) {
                result[mappedColumnName] = NullValue
            }
        }

        addMetadataFields(result, msg, source, parsingFailures)

        return result
    }

    private fun addMetadataFields(
        result: HashMap<String, AirbyteValue>,
        msg: DestinationRecordRaw,
        source: DestinationRecordProtobufSource,
        parsingFailures: List<Meta.Change>
    ) {
        val timestampValue = java.time.Instant.ofEpochMilli(source.emittedAtMs)
        result[Meta.COLUMN_NAME_AB_EXTRACTED_AT] =
            TimestampWithTimezoneValue(
                java.time.OffsetDateTime.ofInstant(
                    timestampValue,
                    java.time.ZoneOffset.UTC,
                ),
            )

        result[Meta.COLUMN_NAME_AB_GENERATION_ID] =
            IntegerValue(msg.stream.generationId.toBigInteger())

        result[Meta.COLUMN_NAME_AB_RAW_ID] = StringValue(msg.airbyteRawId.toString())

        val allChanges =
            source.sourceMeta.changes + msg.stream.unknownColumnChanges + parsingFailures
        val changesArray = buildMetaArrayValue(allChanges)

        val metaValue =
            ObjectValue(
                linkedMapOf(
                    "sync_id" to IntegerValue(msg.stream.syncId.toBigInteger()),
                    "changes" to changesArray,
                ),
            )
        result[Meta.COLUMN_NAME_AB_META] = metaValue
    }

    private fun buildMetaArrayValue(allChanges: List<Meta.Change>): ArrayValue {
        val changeObjects =
            allChanges.map { change ->
                ObjectValue(
                    linkedMapOf(
                        "field" to StringValue(change.field),
                        "change" to StringValue(change.change.toString()),
                        "reason" to StringValue(change.reason.toString())
                    )
                )
            }

        return ArrayValue(changeObjects)
    }
}
