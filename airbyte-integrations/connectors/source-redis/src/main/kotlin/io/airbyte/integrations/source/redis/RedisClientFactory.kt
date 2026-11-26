/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.redis

import io.lettuce.core.RedisClient
import io.lettuce.core.RedisURI
import io.lettuce.core.SslOptions
import io.lettuce.core.SslVerifyMode
import io.netty.handler.ssl.SslContextBuilder
import io.netty.handler.ssl.util.InsecureTrustManagerFactory
import java.io.ByteArrayInputStream

object RedisClientFactory {
    fun create(
        configuration: RedisSourceConfiguration,
        host: String = configuration.host,
        port: Int = configuration.port,
    ): RedisClient {
        val sslMode = configuration.sslMode
        val uriBuilder =
            RedisURI.Builder.redis(host, port)
                .withDatabase(configuration.database)
                .withSsl(sslMode !is RedisSslDisabled)
        when (val mode = sslMode) {
            RedisSslDisabled -> Unit
            RedisSslRequired -> uriBuilder.withVerifyPeer(SslVerifyMode.NONE)
            is RedisSslVerifyCa -> {
                uriBuilder.withVerifyPeer(SslVerifyMode.CA)
            }
            is RedisSslVerifyFull -> {
                uriBuilder.withVerifyPeer(SslVerifyMode.FULL)
            }
        }
        if (configuration.username != null && configuration.password != null) {
            uriBuilder.withAuthentication(configuration.username, configuration.password)
        } else if (configuration.password != null) {
            uriBuilder.withPassword(configuration.password.toCharArray())
        } else if (configuration.username != null) {
            uriBuilder.withAuthentication(configuration.username, CharArray(0))
        }
        val client = RedisClient.create(uriBuilder.build())
        if (sslMode !is RedisSslDisabled) {
            client.setOptions(
                io.lettuce.core.ClientOptions.builder()
                    .sslOptions(
                        SslOptions.builder()
                            .sslContext { builder -> configureSslContext(builder, sslMode) }
                            .build(),
                    )
                    .build(),
            )
        }
        return client
    }

    private fun configureSslContext(
        builder: SslContextBuilder,
        mode: RedisSslModeConfiguration,
    ) {
        when (mode) {
            RedisSslDisabled -> Unit
            RedisSslRequired -> builder.trustManager(InsecureTrustManagerFactory.INSTANCE)
            is RedisSslVerifyCa ->
                configureCertificates(
                    builder,
                    mode.caCertificate,
                    mode.clientCertificate,
                    mode.clientKey,
                    mode.clientKeyPassword,
                )
            is RedisSslVerifyFull ->
                configureCertificates(
                    builder,
                    mode.caCertificate,
                    mode.clientCertificate,
                    mode.clientKey,
                    mode.clientKeyPassword,
                )
        }
    }

    private fun configureCertificates(
        builder: SslContextBuilder,
        caCertificate: String?,
        clientCertificate: String?,
        clientKey: String?,
        clientKeyPassword: String?,
    ) {
        if (caCertificate != null) {
            builder.trustManager(ByteArrayInputStream(caCertificate.toByteArray(Charsets.UTF_8)))
        }
        if (clientCertificate != null || clientKey != null) {
            require(clientCertificate != null && clientKey != null) {
                "Both 'client_certificate' and 'client_key' are required for mutual TLS."
            }
            builder.keyManager(
                ByteArrayInputStream(clientCertificate.toByteArray(Charsets.UTF_8)),
                ByteArrayInputStream(clientKey.toByteArray(Charsets.UTF_8)),
                clientKeyPassword,
            )
        }
    }
}
