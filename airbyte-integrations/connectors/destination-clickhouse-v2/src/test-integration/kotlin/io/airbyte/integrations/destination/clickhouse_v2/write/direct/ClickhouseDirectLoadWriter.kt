/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.write.direct

import com.clickhouse.client.api.Client
import com.clickhouse.client.api.ClientFaultCause
import com.clickhouse.client.api.data_formats.ClickHouseBinaryFormatReader
import com.fasterxml.jackson.databind.node.ArrayNode
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
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
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfiguration
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfigurationFactory
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseSpecification
import io.airbyte.integrations.destination.clickhouse_v2.write.direct.ClientProvider.getClient
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.nio.file.Files
import java.time.ZonedDateTime
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Disabled

class ClickhouseDirectLoadWriter :
    BasicFunctionalityIntegrationTest(
        configContents = Files.readString(Utils.getConfigPath("valid_connection.json")),
        configSpecClass = ClickhouseSpecification::class.java,
        dataDumper =
            ClickhouseDataDumper { spec ->
                ClickhouseConfigurationFactory()
                    .makeWithOverrides(spec as ClickhouseSpecification, mapOf())
            },
        destinationCleaner = ClickhouseDataCleaner,
        isStreamSchemaRetroactive = true,
        dedupBehavior = DedupBehavior(),
        stringifySchemalessObjects = true,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.STRINGIFY,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.STRINGIFY,
        unionBehavior = UnionBehavior.STRINGIFY,
        preserveUndeclaredFields = false,
        supportFileTransfer = false,
        commitDataIncrementally = true,
        allTypesBehavior =
            StronglyTyped(
                integerCanBeLarge = false,
                numberCanBeLarge = false,
                nestedFloatLosesPrecision = false,
            ),
        unknownTypesBehavior = UnknownTypesBehavior.SERIALIZE,
        nullEqualsUnset = true,
        configUpdater = ClickhouseConfigUpdater(),
    ) {
    companion object {
        @JvmStatic
        @BeforeAll
        fun beforeAll() {
            ClickhouseContainerHelper.start()
        }
    }

    @Disabled("Clickhouse does not support file transfer, so this test is skipped.")
    override fun testBasicWriteFile() {
        // Clickhouse does not support file transfer, so this test is skipped.
    }

    @Disabled() override fun testInterruptedTruncateWithoutPriorData() {}

    @Disabled override fun testNoColumns() {}

    @Disabled override fun testTruncateRefresh() {}

    @Disabled override fun testDedupWithStringKey() {}

    @Disabled override fun testDedupChangeCursor() {}

    @Disabled override fun testBasicTypes() {}

    @Disabled override fun testDedupChangePk() {}

    @Disabled override fun testClear() {}

    @Disabled override fun testDedup() {}

    @Disabled override fun testTruncateRefreshNoData() {}

    @Disabled override fun testManyStreamsCompletion() {}

    @Disabled override fun testInterruptedTruncateWithPriorData() {}

    @Disabled override fun testContainerTypes() {}

    @Disabled override fun testFunkyCharacters() {}

    @Disabled override fun testNamespaces() {}

    @Disabled override fun resumeAfterCancelledTruncate() {}

    @Disabled override fun testUnknownTypes() {}

    @Disabled override fun testAppendJsonSchemaEvolution() {}

    @Disabled override fun testFunkyCharactersDedup() {}

    @Disabled override fun testAppendSchemaEvolution() {}

    @Disabled override fun testNoData() {}

    @Disabled override fun testDedupNoCursor() {}

    @Disabled override fun testOverwriteSchemaEvolution() {}

    @Disabled override fun testUnions() {}
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

        val output = mutableListOf<OutputRecord>()

        val response =
            client
                .query(
                    "SELECT * FROM ${stream.descriptor.namespace ?: config.resolvedDatabase}.${stream.descriptor.name}"
                )
                .get()

        val reader: ClickHouseBinaryFormatReader = client.newBinaryFormatReader(response)
        while (reader.hasNext()) {
            val record = reader.next()
            val dataMap = linkedMapOf<String, AirbyteValue>()
            record.entries
                .filter { entry -> !Meta.COLUMN_NAMES.contains(entry.key) }
                .map { entry ->
                    val airbyteValue =
                        when (entry.value) {
                            is Long -> IntegerValue(entry.value as Long)
                            is String -> StringValue(entry.value as String)
                            else ->
                                throw UnsupportedOperationException(
                                    "Clickhouse data dumper doesn't know how to dump type ${entry.value::class.java} with value ${entry.value}"
                                )
                        }
                    dataMap.put(entry.key, airbyteValue)
                }
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
            ClickhouseSpecification::class.java,
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
        val client = getClient(config)

        val query = "select * from system.databases where name like 'test%'"

        client.query(query).get().use { response ->
            val reader = client.newBinaryFormatReader(response)
            while (reader.hasNext()) {
                val record = reader.next()
                val databaseName = record["name"] as String

                client.query("DROP DATABASE IF EXISTS $databaseName").get()
            }
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
    private var client: Client? = null

    fun getClient(config: ClickhouseConfiguration): Client {
        if (client == null) {
            client =
                Client.Builder()
                    .setPassword(config.password)
                    .setUsername(config.username)
                    .addEndpoint(config.endpoint)
                    .setDefaultDatabase(config.resolvedDatabase)
                    .retryOnFailures(ClientFaultCause.None)
                    .build()
        }
        return client!!
    }
}
