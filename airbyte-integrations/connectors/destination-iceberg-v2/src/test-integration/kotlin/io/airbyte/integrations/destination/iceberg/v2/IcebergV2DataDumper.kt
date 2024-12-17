/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.*
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.time.Instant
import java.util.LinkedHashMap
import java.util.UUID
import org.apache.iceberg.data.IcebergGenerics
import org.apache.iceberg.data.Record

object IcebergV2DataDumper : DestinationDataDumper {

    private fun toAirbyteValue(record: Record): ObjectValue {
        return ObjectValue(
            LinkedHashMap(
                record
                    .struct()
                    .fields()
                    .filterNot { DestinationRecord.Meta.COLUMN_NAMES.contains(it.name()) }
                    .associate { field ->
                        val name = field.name()
                        val airbyteValue =
                            when (val value = record.getField(field.name())) {
                                is Record -> toAirbyteValue(value)
                                else -> AirbyteValue.from(value)
                            }
                        name to airbyteValue
                    }
            )
        )
    }

    private fun getMetaData(record: Record): OutputRecord.Meta {
        val airbyteMeta =
            record.getField(DestinationRecord.Meta.COLUMN_NAME_AB_META) as? Record
                ?: throw IllegalStateException("Received no metadata in the record.")

        val syncId = airbyteMeta.getField("sync_id") as? Long
        @Suppress("UNCHECKED_CAST")
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
        val config = IcebergV2TestUtil.getConfig(spec)
        val catalog = IcebergV2TestUtil.getCatalog(config)
        val table =
            catalog.loadTable(
                TableIdGeneratorFactory(config).create().toTableIdentifier(stream.descriptor)
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
                        data = toAirbyteValue(record),
                        airbyteMeta = getMetaData(record)
                    )
                )
            }
        }

        // some catalogs (e.g. Nessie) have a close() method. Call it here.
        if (catalog is AutoCloseable) {
            catalog.close()
        }
        return outputRecords
    }

    override fun dumpFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<String> {
        throw NotImplementedError("Iceberg doesn't support universal file transfer")
    }
}
