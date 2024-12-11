/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.parquet.ParquetMapperPipelineFactory
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.integrations.destination.iceberg.v2.io.IcebergUtil
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.math.BigDecimal
import java.time.Instant
import java.util.LinkedHashMap
import java.util.UUID
import org.apache.hadoop.conf.Configuration
import org.apache.iceberg.catalog.TableIdentifier
import org.apache.iceberg.data.IcebergGenerics
import org.apache.iceberg.data.Record
import org.apache.iceberg.nessie.NessieCatalog

object IcebergV2DataDumper : DestinationDataDumper {

    private fun convert(value: Any?, type: AirbyteType): AirbyteValue {
        return if (value == null) {
            NullValue
        } else {
            when (type) {
                StringType -> StringValue(value as String)
                is ArrayType -> ArrayValue((value as List<*>).map { convert(it, type.items.type) })
                BooleanType -> BooleanValue(value as Boolean)
                IntegerType -> IntegerValue(value as Long)
                NumberType -> NumberValue(BigDecimal(value as Double))
                else ->
                    throw IllegalArgumentException("Object type with empty schema is not supported")
            }
        }
    }

    private fun getCastedData(schema: ObjectType, record: Record): ObjectValue {
        return ObjectValue(
            LinkedHashMap(
                schema.properties
                    .map { (name, field) -> name to convert(record.getField(name), field.type) }
                    .toMap()
            )
        )
    }

    private fun getMetaData(record: Record): OutputRecord.Meta {
        val airbyteMeta =
            record.getField(DestinationRecord.Meta.COLUMN_NAME_AB_META) as? Record
                ?: throw IllegalStateException("Received no metadata in the record.")

        val syncId = airbyteMeta.getField("sync_id") as? Long
        val inputChanges =
            airbyteMeta.getField("changes") as? List<Record>
                ?: throw IllegalStateException("Received no changes in the metadata.")

        val metaChanges =
            inputChanges.map { change ->
                val field = change.getField("field") as String
                val changeValue =
                    AirbyteRecordMessageMetaChange.Change.fromValue(
                        change.getField("change") as String
                    )
                val reason =
                    AirbyteRecordMessageMetaChange.Reason.fromValue(
                        change.getField("reason") as String
                    )
                DestinationRecord.Change(field, changeValue, reason)
            }

        return OutputRecord.Meta(syncId = syncId, changes = metaChanges)
    }

    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        val config =
            IcebergV2ConfigurationFactory()
                .makeWithoutExceptionHandling(spec as IcebergV2Specification)
        val pipeline = ParquetMapperPipelineFactory().create(stream)
        val schema = pipeline.finalSchema as ObjectType
        val catalog = getNessieCatalog(config)
        val table =
            catalog.loadTable(
                TableIdentifier.of(stream.descriptor.namespace, stream.descriptor.name)
            )

        val outputRecords = mutableListOf<OutputRecord>()
        IcebergGenerics.read(table).build().use { records ->
            for (record in records) {
                outputRecords.add(
                    OutputRecord(
                        rawId =
                            UUID.fromString(
                                record
                                    .getField(DestinationRecord.Meta.COLUMN_NAME_AB_RAW_ID)
                                    .toString()
                            ),
                        extractedAt =
                            Instant.ofEpochMilli(
                                record.getField(DestinationRecord.Meta.COLUMN_NAME_AB_EXTRACTED_AT)
                                    as Long
                            ),
                        loadedAt = null,
                        generationId =
                            record.getField(DestinationRecord.Meta.COLUMN_NAME_AB_GENERATION_ID)
                                as Long,
                        data = getCastedData(schema, record),
                        airbyteMeta = getMetaData(record)
                    )
                )
            }
        }

        return outputRecords
    }

    override fun dumpFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<String> {
        TODO("Not yet implemented")
    }

    private fun getNessieCatalog(config: IcebergV2Configuration): NessieCatalog {
        val catalogProperties = IcebergUtil().toCatalogProperties(config)

        val catalog = NessieCatalog()
        catalog.setConf(Configuration())
        catalog.initialize("nessie", catalogProperties)
        return catalog
    }
}
