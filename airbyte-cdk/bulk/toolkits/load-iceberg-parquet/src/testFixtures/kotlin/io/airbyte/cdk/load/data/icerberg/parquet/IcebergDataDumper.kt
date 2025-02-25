/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.icerberg.parquet

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.*
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.toolkits.iceberg.parquet.TableIdGenerator
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.time.Instant
import java.util.LinkedHashMap
import java.util.UUID
import org.apache.iceberg.catalog.Catalog
import org.apache.iceberg.data.IcebergGenerics
import org.apache.iceberg.data.Record

class IcebergDataDumper(
    private val tableIdGenerator: TableIdGenerator,
    private val getCatalog: (ConfigurationSpecification) -> Catalog,
) : DestinationDataDumper {

    private fun toAirbyteValue(record: Record, isRoot: Boolean = false): ObjectValue {
        return ObjectValue(
            LinkedHashMap(
                record
                    .struct()
                    .fields()
                    // _airbyte_* fields are handled explicitly by the caller
                    .filterNot { Meta.COLUMN_NAMES.contains(it.name()) }
                    // _pos is a column name added by iceberg automatically
                    // during dedupe syncs, so we should drop it.
                    .filterNot { isRoot && it.name() == "_pos" }
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
            record.getField(Meta.COLUMN_NAME_AB_META) as? Record
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
                Meta.Change(field, changeValue, reason)
            }

        return OutputRecord.Meta(syncId = syncId, changes = metaChanges)
    }

    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        val catalog = getCatalog(spec)
        val table = catalog.loadTable(tableIdGenerator.toTableIdentifier(stream.descriptor))

        val outputRecords = mutableListOf<OutputRecord>()
        IcebergGenerics.read(table).build().use { records ->
            for (record in records) {
                outputRecords.add(
                    OutputRecord(
                        rawId =
                            UUID.fromString(record.getField(Meta.COLUMN_NAME_AB_RAW_ID).toString()),
                        extractedAt =
                            Instant.ofEpochMilli(
                                record.getField(Meta.COLUMN_NAME_AB_EXTRACTED_AT) as Long
                            ),
                        loadedAt = null,
                        generationId = record.getField(Meta.COLUMN_NAME_AB_GENERATION_ID) as Long,
                        data = toAirbyteValue(record, isRoot = true),
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
