/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql.write

import com.fasterxml.jackson.databind.node.ArrayNode
import com.zaxxer.hikari.HikariConfig
import com.zaxxer.hikari.HikariDataSource
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import java.sql.Date
import java.sql.Time
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetTime
import java.time.ZoneOffset
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
import io.airbyte.integrations.destination.mysql.MySQLConfigUpdater
import io.airbyte.integrations.destination.mysql.MySQLContainerHelper
import io.airbyte.integrations.destination.mysql.Utils
import io.airbyte.integrations.destination.mysql.config.toMySQLCompatibleName
import io.airbyte.integrations.destination.mysql.fixtures.MySQLExpectedRecordMapper
import io.airbyte.integrations.destination.mysql.spec.MySQLConfiguration
import io.airbyte.integrations.destination.mysql.spec.MySQLConfigurationFactory
import io.airbyte.integrations.destination.mysql.spec.MySQLSpecificationOss
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.nio.file.Files
import java.nio.file.Path
import java.sql.Timestamp
import javax.sql.DataSource
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test

class MySQLDirectLoadWriter :
    MySQLAcceptanceTest(
        Utils.getConfigPath("valid_connection.json"),
        SchematizedNestedValueBehavior.STRINGIFY,
    )

abstract class MySQLAcceptanceTest(
    configPath: Path,
    schematizedObjectBehavior: SchematizedNestedValueBehavior,
) :
    BasicFunctionalityIntegrationTest(
        configContents = Files.readString(configPath),
        configSpecClass = MySQLSpecificationOss::class.java,
        dataDumper =
            MySQLDataDumper { spec ->
                val configOverrides = mutableMapOf<String, String>()
                MySQLConfigurationFactory()
                    .makeWithOverrides(spec as MySQLSpecificationOss, configOverrides)
            },
        destinationCleaner = MySQLDataCleaner,
        recordMangler = MySQLExpectedRecordMapper,
        isStreamSchemaRetroactive = true,
        dedupBehavior = DedupBehavior(DedupBehavior.CdcDeletionMode.SOFT_DELETE),
        stringifySchemalessObjects = true,
        schematizedObjectBehavior = schematizedObjectBehavior,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.STRINGIFY,
        unionBehavior = UnionBehavior.STRINGIFY,
        stringifyUnionObjects = true,
        supportFileTransfer = false,
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
        configUpdater = MySQLConfigUpdater(),
        dedupChangeUsesDefault = true,
        useDataFlowPipeline = true,
    ) {
    companion object {
        @JvmStatic
        @BeforeAll
        fun beforeAll() {
            MySQLContainerHelper.start()
        }

        @JvmStatic
        @BeforeAll
        fun afterAll() {
            MySQLContainerHelper.stop()
        }
    }

    @Disabled("MySQL does not support file transfer")
    override fun testBasicWriteFile() {
        // MySQL does not support file transfer
    }
}

class MySQLDataDumper(
    private val configProvider: (ConfigurationSpecification) -> MySQLConfiguration
) : DestinationDataDumper {
    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        val config = configProvider(spec)
        val dataSource = getDataSource(config)
        val output = mutableListOf<OutputRecord>()

        val cleanedNamespace =
            "${stream.mappedDescriptor.namespace ?: config.database}".toMySQLCompatibleName()
        val cleanedStreamName = stream.mappedDescriptor.name.toMySQLCompatibleName()

        dataSource.connection.use { connection ->
            val sql = "SELECT * FROM `$cleanedNamespace`.`$cleanedStreamName`"
            connection.createStatement().use { statement ->
                val rs = statement.executeQuery(sql)
                val metadata = rs.metaData

                while (rs.next()) {
                    val dataMap = linkedMapOf<String, AirbyteValue>()
                    for (i in 1..metadata.columnCount) {
                        val columnName = metadata.getColumnName(i)
                        if (!Meta.COLUMN_NAMES.contains(columnName)) {
                            val value = rs.getObject(i)
                            if (value != null) {
                                // Convert JDBC types to Airbyte types
                                // MySQL DATETIME doesn't store timezone info, so we assume UTC
                                val airbyteValue = when (value) {
                                    is LocalDateTime -> TimestampWithTimezoneValue(value.atOffset(ZoneOffset.UTC))
                                    is Time -> TimeWithoutTimezoneValue(value.toLocalTime())
                                    is LocalTime -> TimeWithoutTimezoneValue(value)
                                    is Date -> DateValue(value.toLocalDate())
                                    is LocalDate -> DateValue(value)
                                    else -> AirbyteValue.from(value)
                                }
                                dataMap[columnName] = airbyteValue
                            }
                        }
                    }

                    val rawId = rs.getString(Meta.COLUMN_NAME_AB_RAW_ID)
                    val extractedAt = rs.getTimestamp(Meta.COLUMN_NAME_AB_EXTRACTED_AT)
                    val generationId = rs.getLong(Meta.COLUMN_NAME_AB_GENERATION_ID)
                    val metaStr = rs.getString(Meta.COLUMN_NAME_AB_META)

                    val outputRecord =
                        OutputRecord(
                            rawId = rawId,
                            extractedAt = extractedAt.time,
                            loadedAt = null,
                            generationId = generationId,
                            data = ObjectValue(dataMap),
                            airbyteMeta = stringToMeta(metaStr ?: ""),
                        )
                    output.add(outputRecord)
                }
            }
        }

        return output
    }

    override fun dumpFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): Map<String, String> {
        throw UnsupportedOperationException("MySQL does not support file transfer.")
    }

    private fun getDataSource(config: MySQLConfiguration): DataSource {
        val hikariConfig = HikariConfig().apply {
            jdbcUrl = "jdbc:mysql://${config.hostname}:${config.port}/?sslMode=DISABLED&allowPublicKeyRetrieval=true"
            username = config.username
            password = config.password
            maximumPoolSize = 5
            connectionTimeout = 30000
            driverClassName = "com.mysql.cj.jdbc.Driver"
        }
        return HikariDataSource(hikariConfig)
    }
}

object MySQLDataCleaner : DestinationCleaner {
    override fun cleanup() {
        try {
            val hikariConfig = HikariConfig().apply {
                jdbcUrl = "jdbc:mysql://${MySQLContainerHelper.getHost()}:${MySQLContainerHelper.getPort()}/?sslMode=DISABLED&allowPublicKeyRetrieval=true"
                username = MySQLContainerHelper.getUsername()
                password = MySQLContainerHelper.getPassword()
                maximumPoolSize = 5
                connectionTimeout = 30000
                driverClassName = "com.mysql.cj.jdbc.Driver"
            }
            val dataSource = HikariDataSource(hikariConfig)

            dataSource.connection.use { connection ->
                connection.createStatement().use { statement ->
                    val rs = statement.executeQuery("SHOW DATABASES LIKE 'test%'")
                    val databasesToDelete = mutableListOf<String>()
                    while (rs.next()) {
                        databasesToDelete.add(rs.getString(1))
                    }
                    databasesToDelete.forEach { dbName ->
                        statement.execute("DROP DATABASE IF EXISTS `$dbName`")
                    }
                }
            }
        } catch (e: Exception) {
            // Swallow exception to not fail test suite
        }
    }
}

fun stringToMeta(metaAsString: String): OutputRecord.Meta {
    if (metaAsString.isEmpty()) {
        return OutputRecord.Meta(
            changes = emptyList(),
            syncId = null,
        )
    }
    val metaJson = Jsons.readTree(metaAsString)

    val changes =
        (metaJson["changes"] as ArrayNode).map { change ->
            Meta.Change(
                field = change["field"].textValue(),
                change =
                    AirbyteRecordMessageMetaChange.Change.fromValue(change["change"].textValue()),
                reason =
                    AirbyteRecordMessageMetaChange.Reason.fromValue(change["reason"].textValue()),
            )
        }

    return OutputRecord.Meta(
        changes = changes,
        syncId = metaJson["sync_id"]?.longValue(),
    )
}
