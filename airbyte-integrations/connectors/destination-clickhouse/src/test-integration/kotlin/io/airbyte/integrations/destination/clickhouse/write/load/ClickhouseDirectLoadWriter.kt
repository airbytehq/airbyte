/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.write.load

import com.clickhouse.client.api.Client
import com.clickhouse.client.api.ClientFaultCause
import com.clickhouse.client.api.data_formats.ClickHouseBinaryFormatReader
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
import io.airbyte.integrations.destination.clickhouse.ClickhouseConfigUpdater
import io.airbyte.integrations.destination.clickhouse.ClickhouseContainerHelper
import io.airbyte.integrations.destination.clickhouse.Utils
import io.airbyte.integrations.destination.clickhouse.config.toClickHouseCompatibleName
import io.airbyte.integrations.destination.clickhouse.fixtures.ClickhouseExpectedRecordMapper
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseConfiguration
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseConfigurationFactory
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseSpecificationOss
import io.airbyte.integrations.destination.clickhouse.write.load.ClientProvider.getClient
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.nio.file.Files
import java.nio.file.Path
import java.time.ZonedDateTime
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test

class ClickhouseDirectLoadWriterWithJson :
    ClickhouseDirectLoadWriter(
        Utils.getConfigPath("valid_connection.json"),
        SchematizedNestedValueBehavior.PASS_THROUGH,
        false,
    ) {

    /**
     * The way clickhouse handle json makes this test unfit JSON keeps a schema of the JSONs
     * inserted. If a previous row has a JSON with a column A, It is expected that the subsequent
     * row, will have the column A. This test includes test case for schemaless type which aren't
     * behaving like the other warehouses
     */
    @Disabled("Unfit for clickhouse with Json") override fun testContainerTypes() {}
}

class ClickhouseDirectLoadWriterWithoutJson :
    ClickhouseDirectLoadWriter(
        Utils.getConfigPath("valid_connection_no_json.json"),
        SchematizedNestedValueBehavior.STRINGIFY,
        true,
    )

@Disabled("Requires local bastion and CH instance to pass")
class ClickhouseDirectLoadWriterWithoutJsonSshTunnel :
    ClickhouseDirectLoadWriter(
        Path.of("secrets/ssh-tunnel.json"),
        SchematizedNestedValueBehavior.STRINGIFY,
        true,
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }
}

abstract class ClickhouseDirectLoadWriter(
    configPath: Path,
    schematizedObjectBehavior: SchematizedNestedValueBehavior,
    stringifySchemalessObjects: Boolean
) :
    BasicFunctionalityIntegrationTest(
        configContents = Files.readString(configPath),
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
        stringifySchemalessObjects = stringifySchemalessObjects,
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

        val reader: ClickHouseBinaryFormatReader = client.newBinaryFormatReader(response, schema)
        while (reader.hasNext()) {
            val record = reader.next()
            val dataMap = linkedMapOf<String, AirbyteValue>()
            record.entries
                .filter { entry -> !Meta.COLUMN_NAMES.contains(entry.key) }
                .forEach { entry -> dataMap[entry.key] = AirbyteValue.from(entry.value) }
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
            .build()
    }
}
