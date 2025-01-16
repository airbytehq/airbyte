/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.integrations.destination.mssql.v2.config.DataSourceFactory
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLConfigurationFactory
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLSpecification
import io.airbyte.protocol.models.Jsons
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import java.nio.file.Files
import java.time.Instant
import java.util.UUID

abstract class MSSQLWriterTest(
    configPath: String,
    dataDumper: DestinationDataDumper,
    dataCleaner: DestinationCleaner,
) :
    BasicFunctionalityIntegrationTest(
        configContents = Files.readString(MSSQLTestConfigUtil.getConfigPath(configPath)),
        configSpecClass = MSSQLSpecification::class.java,
        dataDumper = dataDumper,
        destinationCleaner = dataCleaner,
        isStreamSchemaRetroactive = false,
        supportsDedup = false,
        stringifySchemalessObjects = false,
        promoteUnionToObject = true,
        preserveUndeclaredFields = false,
        commitDataIncrementally = true,
        allTypesBehavior = StronglyTyped(integerCanBeLarge = false),
        nullEqualsUnset = true,
        supportFileTransfer = false,
        envVars = emptyMap(),
    )

class MSSQLDataDumper : DestinationDataDumper {
    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        val config =
            MSSQLConfigurationFactory().makeWithoutExceptionHandling(spec as MSSQLSpecification)
        val sqlBuilder = MSSQLQueryBuilder(config, stream)
        val dataSource = DataSourceFactory().dataSource(config)
        val output = mutableListOf<OutputRecord>()
        dataSource.connection.use { connection ->
            val statement = connection.prepareStatement(sqlBuilder.selectAllRecords())
            statement.executeQuery().use { rs ->
                while (rs.next()) {
                    val objectValue = sqlBuilder.readResult(rs, sqlBuilder.finalTableSchema)
                    val record =
                        OutputRecord(
                            rawId =
                                rs.getString(MSSQLQueryBuilder.AIRBYTE_RAW_ID)?.let {
                                    UUID.fromString(it)
                                },
                            extractedAt =
                                Instant.ofEpochMilli(
                                    rs.getLong(MSSQLQueryBuilder.AIRBYTE_EXTRACTED_AT)
                                ),
                            loadedAt = null,
                            generationId = rs.getLong(MSSQLQueryBuilder.AIRBYTE_GENERATION_ID),
                            data = objectValue,
                            airbyteMeta =
                                rs.getString(MSSQLQueryBuilder.AIRBYTE_META)?.let {
                                    val meta =
                                        Jsons.deserialize(it, AirbyteRecordMessageMeta::class.java)
                                    OutputRecord.Meta(
                                        changes =
                                            meta.changes
                                                .map { change ->
                                                    Meta.Change(
                                                        field = change.field,
                                                        change = change.change,
                                                        reason = change.reason,
                                                    )
                                                }
                                                .toList(),
                                        syncId =
                                            meta.additionalProperties["syncId"]
                                                ?.toString()
                                                ?.toLong()
                                    )
                                },
                        )
                    output.add(record)
                }
            }
        }
        return output
    }

    override fun dumpFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<String> {
        return emptyList()
    }
}

class MSSQLDataCleaner : DestinationCleaner {
    override fun cleanup() {
        // TODO("Not yet implemented")
    }
}

class StandardInsert :
    MSSQLWriterTest(
        "check/valid.json",
        MSSQLDataDumper(),
        MSSQLDataCleaner(),
    )
