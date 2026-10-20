/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.redis

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.cdk.ssh.TunnelSession
import io.airbyte.cdk.ssh.createTunnelSession
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.lettuce.core.RedisClient
import io.lettuce.core.RedisCommandExecutionException
import io.lettuce.core.api.StatefulRedisConnection
import io.lettuce.core.api.sync.RedisCommands
import io.lettuce.core.codec.StringCodec
import io.lettuce.core.output.KeyScanOutput
import io.lettuce.core.protocol.CommandArgs
import io.lettuce.core.protocol.CommandType
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.util.regex.Pattern
import org.apache.sshd.common.util.net.SshdSocketAddress

class RedisSourceMetadataQuerier(
    private val configuration: RedisSourceConfiguration,
    private val client: RedisClient,
    private val connection: StatefulRedisConnection<String, String>,
    private val tunnelSession: TunnelSession,
) : MetadataQuerier {
    private val commands: RedisCommands<String, String> = connection.sync()

    override fun streamNamespaces(): List<String> = emptyList()

    override fun streamNames(streamNamespace: String?): List<StreamIdentifier> =
        if (streamNamespace != null) {
            emptyList()
        } else {
            RedisKeyType.entries.map {
                StreamIdentifier.from(StreamDescriptor().withName(it.streamName))
            }
        }

    override fun fields(streamID: StreamIdentifier): List<EmittedField> =
        RedisKeyType.entries
            .firstOrNull { it.streamName == streamID.name }
            ?.fields
            ?.map { EmittedField(it.name, it.type) }
            ?: emptyList()

    override fun primaryKey(streamID: StreamIdentifier): List<List<String>> =
        RedisKeyType.entries.firstOrNull { it.streamName == streamID.name }?.primaryKey
            ?: emptyList()

    override fun extraChecks() {
        checkServerVersion()
        checkScanTypeSupport()
        commands.dbsize()
    }

    private fun checkServerVersion() {
        val info =
            try {
                commands.info("server")
            } catch (e: RedisCommandExecutionException) {
                if (e.message?.contains("NOPERM", ignoreCase = true) == true) {
                    return
                }
                throw e
            }
        val version =
            VERSION_PATTERN.matcher(info).let { matcher ->
                if (!matcher.find()) {
                    return
                }
                matcher.group(1).split('.').mapNotNull(String::toIntOrNull)
            }
        if (version.size < 2 || compareVersions(version, MINIMUM_VERSION) < 0) {
            throw ConfigErrorException("Redis version 6.0 or newer is required.")
        }
    }

    private fun checkScanTypeSupport() {
        try {
            commands.dispatch(
                CommandType.SCAN,
                KeyScanOutput(StringCodec.UTF8),
                CommandArgs<String, String>(StringCodec.UTF8)
                    .add("0")
                    .add("COUNT")
                    .add(1)
                    .add("TYPE")
                    .add("string"),
            )
        } catch (e: RedisCommandExecutionException) {
            if (e.message?.contains("ERR syntax error", ignoreCase = true) == true) {
                throw ConfigErrorException(
                    "Redis 6.0 or newer is required because this source uses SCAN TYPE.",
                    e,
                )
            }
            throw e
        }
    }

    override fun close() {
        try {
            connection.close()
        } finally {
            try {
                client.shutdown()
            } finally {
                tunnelSession.close()
            }
        }
    }

    companion object {
        private val VERSION_PATTERN =
            Pattern.compile("redis_version:([0-9]+\\.[0-9]+(?:\\.[0-9]+)?)")
        private val MINIMUM_VERSION = listOf(6, 0)

        private fun compareVersions(left: List<Int>, right: List<Int>): Int {
            for (i in 0 until maxOf(left.size, right.size)) {
                val difference = (left.getOrNull(i) ?: 0).compareTo(right.getOrNull(i) ?: 0)
                if (difference != 0) {
                    return difference
                }
            }
            return 0
        }
    }

    @Singleton
    @Primary
    class Factory : MetadataQuerier.Factory<RedisSourceConfiguration> {
        override fun session(config: RedisSourceConfiguration): MetadataQuerier {
            var tunnelSession: TunnelSession? = null
            var client: RedisClient? = null
            var connection: StatefulRedisConnection<String, String>? = null
            try {
                tunnelSession =
                    createTunnelSession(
                        SshdSocketAddress(config.host, config.port),
                        config.sshTunnel,
                        config.sshConnectionOptions,
                    )
                client =
                    RedisClientFactory.create(
                        config,
                        tunnelSession.address.hostString,
                        tunnelSession.address.port,
                    )
                connection = client.connect()
                return RedisSourceMetadataQuerier(config, client, connection, tunnelSession)
            } catch (e: Exception) {
                connection?.close()
                client?.shutdown()
                tunnelSession?.close()
                throw e
            }
        }
    }
}
