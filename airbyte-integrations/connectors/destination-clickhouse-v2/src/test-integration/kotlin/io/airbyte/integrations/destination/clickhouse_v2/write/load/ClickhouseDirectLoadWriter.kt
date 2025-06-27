/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.write.load

import com.clickhouse.client.api.Client
import com.clickhouse.client.api.ClientFaultCause
import com.clickhouse.client.api.data_formats.ClickHouseBinaryFormatReader
import com.clickhouse.client.api.internal.ServerSettings
import com.fasterxml.jackson.databind.node.ArrayNode
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.load.command.Dedupe
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
import io.airbyte.cdk.load.write.UnknownTypesBehavior
import io.airbyte.integrations.destination.clickhouse_v2.ClickhouseConfigUpdater
import io.airbyte.integrations.destination.clickhouse_v2.ClickhouseContainerHelper
import io.airbyte.integrations.destination.clickhouse_v2.Utils
import io.airbyte.integrations.destination.clickhouse_v2.config.toClickHouseCompatibleName
import io.airbyte.integrations.destination.clickhouse_v2.fixtures.ClickhouseExpectedRecordMapper
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfiguration
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfigurationFactory
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseSpecificationOss
import io.airbyte.integrations.destination.clickhouse_v2.write.load.ClientProvider.getClient
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.nio.file.Files
import java.time.ZonedDateTime
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Disabled

class ClickhouseDirectLoadWriter :
    BasicFunctionalityIntegrationTest(
        configContents = Files.readString(Utils.getConfigPath("valid_connection.json")),
        configSpecClass = ClickhouseSpecificationOss::class.java,
        dataDumper =
            ClickhouseDataDumper { spec ->
                val configOverrides = mutableMapOf<String, String>()
                ClickhouseConfigurationFactory()
                    .makeWithOverrides(spec as ClickhouseSpecificationOss, configOverrides)
            },
        destinationCleaner = ClickhouseDataCleaner,
        recordMangler = ClickhouseExpectedRecordMapper,
        isStreamSchemaRetroactive = true,
        dedupBehavior = DedupBehavior(DedupBehavior.CdcDeletionMode.SOFT_DELETE),
        stringifySchemalessObjects = false,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.STRINGIFY,
        unionBehavior = UnionBehavior.STRICT_STRINGIFY,
        stringifyUnionObjects = true,
        preserveUndeclaredFields = false,
        supportFileTransfer = false,
        commitDataIncrementally = false,
        commitDataIncrementallyOnAppend = true,
        allTypesBehavior =
            StronglyTyped(
                integerCanBeLarge = false,
                numberCanBeLarge = false,
                nestedFloatLosesPrecision = false,
            ),
        unknownTypesBehavior = UnknownTypesBehavior.PASS_THROUGH,
        nullEqualsUnset = true,
        configUpdater = ClickhouseConfigUpdater(),
        dedupChangeUsesDefault = true,
    ) {
    companion object {
        @JvmStatic
        @BeforeAll
        fun beforeAll() {
            ClickhouseContainerHelper.start()
        }

        @JvmStatic
        @BeforeAll
        fun afterAll() {
            ClickhouseContainerHelper.stop()
        }
    }

    @Disabled("Clickhouse does not support file transfer, so this test is skipped.")
    override fun testBasicWriteFile() {
        // Clickhouse does not support file transfer, so this test is skipped.
    }
}

class ClickhouseDataDumper(
    private val configProvider: (ConfigurationSpecification) -> ClickhouseConfiguration
) : DestinationDataDumper {
    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        val config = configProvider(spec)
        val client = getClient(config)

        val isDedup = stream.importType is Dedupe

        val output = mutableListOf<OutputRecord>()

        val cleanedNamespace =
            "${stream.mappedDescriptor.namespace ?: config.resolvedDatabase}".toClickHouseCompatibleName()
        val cleanedStreamName = stream.mappedDescriptor.name.toClickHouseCompatibleName()

        val namespacedTableName = "$cleanedNamespace.$cleanedStreamName"

        val response =
            client.query("SELECT * FROM $namespacedTableName ${if (isDedup) "FINAL" else ""}").get()

        val schema = client.getTableSchema(namespacedTableName)
        println("Schema:")
        println(schema.columns)

        val reader: ClickHouseBinaryFormatReader = client.newBinaryFormatReader(response, schema)
        while (reader.hasNext()) {
            val record = reader.next()
            val dataMap = linkedMapOf<String, AirbyteValue>()
            record.entries
                .filter { entry -> !Meta.COLUMN_NAMES.contains(entry.key) }
                .forEach { entry ->
                    if (entry.value != null)
                        println("${entry.key} -> ${entry.value} with value type: ${entry.value.javaClass}")
                    dataMap[entry.key] = AirbyteValue.from(entry.value) }
            val outputRecord =
                OutputRecord(
                    rawId = record[Meta.COLUMN_NAME_AB_RAW_ID] as String,
                    extractedAt =
                        (record[Meta.COLUMN_NAME_AB_EXTRACTED_AT] as ZonedDateTime)
                            .toInstant()
                            .toEpochMilli(),
                    loadedAt = null,
                    generationId = record[Meta.COLUMN_NAME_AB_GENERATION_ID] as Long,
                    data = ObjectValue(dataMap),
                    airbyteMeta = stringToMeta(record[Meta.COLUMN_NAME_AB_META] as String),
                )
            output.add(outputRecord)
        }

        return output
    }

    override fun dumpFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): Map<String, String> {
        throw UnsupportedOperationException("Clickhouse does not support file transfer.")
    }
}

object ClickhouseDataCleaner : DestinationCleaner {
    private val clickhouseSpecification =
        ValidatedJsonUtils.parseOne(
            ClickhouseSpecificationOss::class.java,
            Files.readString(Utils.getConfigPath("valid_connection.json"))
        )

    private val config =
        ClickhouseConfigurationFactory()
            .makeWithOverrides(
                clickhouseSpecification,
                mapOf(
                    "hostname" to ClickhouseContainerHelper.getIpAddress()!!,
                    "port" to (ClickhouseContainerHelper.getPort()?.toString())!!,
                    "protocol" to "http",
                    "username" to ClickhouseContainerHelper.getUsername()!!,
                    "password" to ClickhouseContainerHelper.getPassword()!!,
                )
            )

    override fun cleanup() {
        try {
            val client = getClient(config)

            val query = "select * from system.databases where name like 'test%'"

            val response = client.query(query).get()

            val reader = client.newBinaryFormatReader(response)
            while (reader.hasNext()) {
                val record = reader.next()
                val databaseName = record["name"] as String

                client.query("DROP DATABASE IF EXISTS $databaseName").get()
            }
        } catch (e: Exception) {
            // swallow the exception, we don't want to fail the test suite if the cleanup fails
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
        syncId = metaJson["sync_id"].longValue(),
    )
}

object ClientProvider {
    fun getClient(config: ClickhouseConfiguration): Client {
        return Client.Builder()
            .setPassword(config.password)
            .setUsername(config.username)
            .addEndpoint(config.endpoint)
            .setDefaultDatabase(config.resolvedDatabase)
            .retryOnFailures(ClientFaultCause.None)
            // // allow experimental JSON type
            // .serverSetting("allow_experimental_json_type", "1")
            // // allow JSON transcoding as a string
            // .serverSetting(ServerSettings.INPUT_FORMAT_BINARY_READ_JSON_AS_STRING, "1")
            // .serverSetting(ServerSettings.OUTPUT_FORMAT_BINARY_WRITE_JSON_AS_STRING, "1")
            .build()
    }
}
