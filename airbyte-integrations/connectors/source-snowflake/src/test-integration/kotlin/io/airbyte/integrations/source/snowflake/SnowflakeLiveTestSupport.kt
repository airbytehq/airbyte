/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamState
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.airbyte.protocol.models.v0.SyncMode
import java.nio.file.Files
import java.nio.file.Path
import java.sql.Connection
import java.sql.DriverManager
import java.util.Properties
import kotlin.random.Random
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Assumptions

/**
 * Helpers for tests that run against a real Snowflake account.
 *
 * The connection comes from the first existing file among `secrets/config.json` and
 * `secrets/config_key_pair.json` (the latter is what CI fetches from GSM). Without either file
 * every live test is skipped through [assumeConfigured].
 */
object SnowflakeLiveTestSupport {
    private val candidateConfigs = listOf("secrets/config.json", "secrets/config_key_pair.json")

    val configPath: Path? =
        candidateConfigs.map { Path.of(it) }.firstOrNull { Files.isRegularFile(it) }

    fun assumeConfigured() {
        Assumptions.assumeTrue(
            configPath != null,
            "no ${candidateConfigs.joinToString(" or ")}: skipping live Snowflake tests",
        )
    }

    /**
     * The user-provided config with test overrides. [sessionTimezone] is appended to
     * `jdbc_url_params` because the Snowflake account default (America/Los_Angeles) shifts
     * TIMESTAMP_NTZ cursor bounds (airbytehq/airbyte#83800); pass `null` to keep the account
     * default.
     */
    fun spec(
        schema: String? = null,
        concurrency: Int? = null,
        checkpointSeconds: Int? = null,
        checkPrivileges: Boolean? = null,
        sessionTimezone: String? = "UTC",
    ): SnowflakeSourceConfigurationSpecification {
        val spec: SnowflakeSourceConfigurationSpecification =
            Jsons.readValue(
                Files.readAllBytes(configPath!!),
                SnowflakeSourceConfigurationSpecification::class.java,
            )
        schema?.let { spec.schema = it }
        concurrency?.let { spec.concurrency = it }
        checkpointSeconds?.let { spec.checkpointTargetIntervalSeconds = it }
        checkPrivileges?.let { spec.checkPrivileges = it }
        sessionTimezone?.let {
            spec.jdbcUrlParams =
                listOfNotNull(spec.jdbcUrlParams?.takeIf(String::isNotBlank), "TIMEZONE=$it")
                    .joinToString("&")
        }
        return spec
    }

    fun config(spec: SnowflakeSourceConfigurationSpecification): SnowflakeSourceConfiguration =
        SnowflakeSourceConfigurationFactory().makeWithoutExceptionHandling(spec)

    /** A plain driver connection (the CDK's factory forces read-only, which we do not want). */
    fun connect(spec: SnowflakeSourceConfigurationSpecification): Connection {
        val config = config(spec)
        val props = Properties().apply { putAll(config.jdbcProperties) }
        return DriverManager.getConnection(String.format(config.jdbcUrlFmt, config.realHost), props)
    }

    fun execute(conn: Connection, sql: String) {
        conn.createStatement().use { it.execute(sql) }
    }

    /** Runs a `;`-terminated SQL script from the test resources with `${VAR}` substitution. */
    fun executeScript(conn: Connection, resource: String, vars: Map<String, String>) {
        var text: String =
            javaClass.classLoader.getResourceAsStream(resource)?.use {
                it.readAllBytes().decodeToString()
            }
                ?: throw IllegalArgumentException("missing test resource $resource")
        vars.forEach { (k, v) -> text = text.replace("\${$k}", v) }
        val statement = StringBuilder()
        for (line in text.lines()) {
            val trimmed = line.trim()
            if (trimmed.isEmpty() || trimmed.startsWith("--")) continue
            statement.append(line).append('\n')
            if (trimmed.endsWith(";")) {
                execute(conn, statement.toString().trim().removeSuffix(";"))
                statement.setLength(0)
            }
        }
    }

    /**
     * Schema names never contain `_`: the driver treats `_` and `%` in a schema filter as LIKE
     * wildcards and lists the whole database (minutes on a large account).
     */
    fun newSchemaName(): String {
        val letters = (1..4).map { ('A'..'Z').random(Random.Default) }.joinToString("")
        return "AIRBYTEIT${System.currentTimeMillis()}$letters"
    }

    fun discover(spec: SnowflakeSourceConfigurationSpecification): AirbyteCatalog =
        CliRunner.source("discover", spec).run().catalogs().single()

    /** Configures the named streams of a discovered catalog for [syncMode]. */
    fun configured(
        catalog: AirbyteCatalog,
        names: List<String>,
        syncMode: SyncMode = SyncMode.FULL_REFRESH,
        cursor: String? = null,
    ): ConfiguredAirbyteCatalog {
        val streams =
            names.map { name ->
                val stream =
                    catalog.streams.firstOrNull { it.name == name }
                        ?: throw AssertionError("stream $name missing from discovered catalog")
                ConfiguredAirbyteStream()
                    .withStream(stream)
                    .withSyncMode(syncMode)
                    .withDestinationSyncMode(
                        if (syncMode == SyncMode.INCREMENTAL) DestinationSyncMode.APPEND
                        else DestinationSyncMode.OVERWRITE
                    )
                    .withPrimaryKey(stream.sourceDefinedPrimaryKey)
                    .withCursorField(cursor?.let { listOf(it) } ?: emptyList())
            }
        return ConfiguredAirbyteCatalog().withStreams(streams)
    }

    fun read(
        spec: SnowflakeSourceConfigurationSpecification,
        catalog: ConfiguredAirbyteCatalog,
        state: List<AirbyteStateMessage> = emptyList(),
    ): BufferingOutputConsumer = CliRunner.source("read", spec, catalog, state).run()

    fun streamState(name: String, namespace: String, state: String): AirbyteStateMessage =
        AirbyteStateMessage()
            .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
            .withStream(
                AirbyteStreamState()
                    .withStreamDescriptor(
                        StreamDescriptor().withName(name).withNamespace(namespace)
                    )
                    .withStreamState(Jsons.readTree(state))
            )

    fun BufferingOutputConsumer.recordsOf(stream: String): List<JsonNode> =
        records().filter { it.stream == stream }.map { it.data }

    fun BufferingOutputConsumer.statesOf(stream: String): List<JsonNode> =
        states()
            .filter { it.stream?.streamDescriptor?.name == stream }
            .map { it.stream.streamState }

    fun BufferingOutputConsumer.lastStateOf(stream: String): JsonNode? =
        statesOf(stream).lastOrNull()

    fun BufferingOutputConsumer.assertNoErrors() {
        val errors =
            traces().filter { it.type == AirbyteTraceMessage.Type.ERROR }.map { it.error.message }
        Assertions.assertTrue(errors.isEmpty(), "unexpected error traces: $errors")
    }

    fun ids(records: List<JsonNode>, field: String = "ID"): List<Long> =
        records.map { it[field].asLong() }.sorted()
}
