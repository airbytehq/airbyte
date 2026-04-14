/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.doris.write

import com.fasterxml.jackson.databind.node.ArrayNode
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.DedupBehavior
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.integrations.destination.doris.DorisConfigUpdater
import io.airbyte.integrations.destination.doris.DorisContainerHelper
import io.airbyte.integrations.destination.doris.DorisTestUtils
import io.airbyte.integrations.destination.doris.fixtures.DorisExpectedRecordMapper
import io.airbyte.integrations.destination.doris.schema.toDorisCompatibleName
import io.airbyte.integrations.destination.doris.spec.DorisSpecification
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.util.Calendar
import java.util.TimeZone
import org.junit.jupiter.api.BeforeAll

class DorisAcceptanceTest :
    BasicFunctionalityIntegrationTest(
        configContents = DorisTestUtils.buildConfigJson(),
        configSpecClass = DorisSpecification::class.java,
        dataDumper = DorisDataDumper(),
        destinationCleaner = DorisDataCleaner,
        recordMangler = DorisExpectedRecordMapper,
        isStreamSchemaRetroactive = true,
        dedupBehavior = DedupBehavior(DedupBehavior.CdcDeletionMode.SOFT_DELETE),
        stringifySchemalessObjects = true,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.STRINGIFY,
        unionBehavior = UnionBehavior.STRINGIFY,
        stringifyUnionObjects = true,
        commitDataIncrementally = false,
        commitDataIncrementallyOnAppend = true,
        commitDataIncrementallyToEmptyDestinationOnAppend = true,
        commitDataIncrementallyToEmptyDestinationOnDedupe = true,
        allTypesBehavior =
            StronglyTyped(
                integerCanBeLarge = false,
                numberCanBeLarge = false,
                nestedFloatLosesPrecision = false,
            ),
        nullEqualsUnset = true,
        configUpdater = DorisConfigUpdater(),
    ) {
    companion object {
        @JvmStatic
        @BeforeAll
        fun startContainer() {
            DorisContainerHelper.start()
        }
    }
}

class DorisDataDumper : DestinationDataDumper {
    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        val config = DorisTestUtils.specToConfig(spec)
        val output = mutableListOf<OutputRecord>()

        val cleanedNamespace =
            (stream.mappedDescriptor.namespace ?: config.database).toDorisCompatibleName()
        val cleanedStreamName = stream.mappedDescriptor.name.toDorisCompatibleName()

        DorisTestUtils.getConnection(cleanedNamespace).use { conn ->
            conn.createStatement().use { stmt ->
                val rs = stmt.executeQuery("SELECT * FROM `$cleanedStreamName`")
                val metaData = rs.metaData
                val columnNames = (1..metaData.columnCount).map { metaData.getColumnName(it) }

                while (rs.next()) {
                    val dataMap = linkedMapOf<String, AirbyteValue>()
                    for (colName in columnNames) {
                        if (colName !in Meta.COLUMN_NAMES) {
                            val value = rs.getObject(colName)
                            dataMap[colName] = AirbyteValue.from(value)
                        }
                    }

                    val metaString = rs.getString(Meta.COLUMN_NAME_AB_META) ?: ""
                    output.add(
                        OutputRecord(
                            rawId = rs.getString(Meta.COLUMN_NAME_AB_RAW_ID),
                            extractedAt =
                                rs.getTimestamp(
                                        Meta.COLUMN_NAME_AB_EXTRACTED_AT,
                                        Calendar.getInstance(TimeZone.getTimeZone("UTC"))
                                    )
                                    .time,
                            loadedAt = null,
                            generationId = rs.getLong(Meta.COLUMN_NAME_AB_GENERATION_ID),
                            data = ObjectValue(dataMap),
                            airbyteMeta = stringToMeta(metaString),
                        )
                    )
                }
            }
        }

        return output
    }

    override fun dumpFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): Map<String, String> {
        throw UnsupportedOperationException("Doris does not support file transfer.")
    }
}

object DorisDataCleaner : DestinationCleaner {
    override fun cleanup() {
        try {
            DorisContainerHelper.start()
            DorisTestUtils.getConnection().use { conn ->
                conn.createStatement().use { stmt ->
                    val rs =
                        stmt.executeQuery(
                            "SELECT SCHEMA_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME LIKE 'test%'"
                        )
                    val databases = mutableListOf<String>()
                    while (rs.next()) {
                        databases.add(rs.getString("SCHEMA_NAME"))
                    }
                    databases.forEach { db -> stmt.execute("DROP DATABASE IF EXISTS `$db`") }
                }
            }
        } catch (_: Exception) {
            // Swallow cleanup failures
        }
    }
}

fun stringToMeta(metaAsString: String): OutputRecord.Meta {
    if (metaAsString.isEmpty()) {
        return OutputRecord.Meta(changes = emptyList(), syncId = null)
    }
    val metaJson = Jsons.readTree(metaAsString)
    val changes =
        (metaJson["changes"] as? ArrayNode)?.map { change ->
            Meta.Change(
                field = change["field"].textValue(),
                change =
                    AirbyteRecordMessageMetaChange.Change.fromValue(change["change"].textValue()),
                reason =
                    AirbyteRecordMessageMetaChange.Reason.fromValue(change["reason"].textValue()),
            )
        }
            ?: emptyList()

    return OutputRecord.Meta(
        changes = changes,
        syncId = metaJson["sync_id"]?.longValue(),
    )
}
