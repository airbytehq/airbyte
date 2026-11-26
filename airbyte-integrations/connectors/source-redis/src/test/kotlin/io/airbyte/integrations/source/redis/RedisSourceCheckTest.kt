/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.redis

import io.airbyte.cdk.command.SyncsTestFixture
import io.airbyte.cdk.ssh.SshBastionContainer
import io.airbyte.cdk.testcontainers.DOCKER_HOST_FROM_WITHIN_CONTAINER
import java.io.File
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.testcontainers.Testcontainers
import org.testcontainers.containers.BindMode
import org.testcontainers.containers.GenericContainer

class RedisSourceCheckTest {
    @Test
    fun testCheckSucceeds() {
        SyncsTestFixture.testCheck(config(plain))
    }

    @Test
    fun testConfiguredPasswordIsAcceptedByNopassUser() {
        SyncsTestFixture.testCheck(config(plain, password = "any-password"))
    }

    @Test
    fun testWrongPasswordIsClassified() {
        redisContainer("--requirepass", "correct-password").use { redis ->
            redis.start()
            SyncsTestFixture.testCheck(
                config(redis, password = "incorrect-password"),
                expectedFailure = "Redis rejected the configured password or ACL username",
            )
        }
    }

    @Test
    fun testMissingPasswordIsClassified() {
        redisContainer("--requirepass", "correct-password").use { redis ->
            redis.start()
            SyncsTestFixture.testCheck(
                config(redis),
                expectedFailure = "Redis requires authentication",
            )
        }
    }

    @Test
    fun testReadAclUserMayCheckWhenInfoIsDenied() {
        createAclUser(plain, "reader", "reader-password", "+@read")
        SyncsTestFixture.testCheck(config(plain, username = "reader", password = "reader-password"))
    }

    @Test
    fun testScanPermissionFailureIsClassified() {
        createAclUser(plain, "no-scan", "no-scan-password", "+@read", "-scan")
        SyncsTestFixture.testCheck(
            config(plain, username = "no-scan", password = "no-scan-password"),
            expectedFailure = "Redis does not permit a required command",
        )
    }

    @Test
    fun testDatabaseOutOfRangeIsClassified() {
        redisContainer("--databases", "2").use { redis ->
            redis.start()
            SyncsTestFixture.testCheck(
                config(redis, database = 3),
                expectedFailure = "The configured Redis database index is out of range",
            )
        }
    }

    @Test
    fun testUnreachableRedisIsClassified() {
        SyncsTestFixture.testCheck(
            RedisSourceConfigurationSpecification().apply {
                host = "127.0.0.1"
                port = 1
            },
            expectedFailure = "Could not connect to Redis",
        )
    }

    @Test
    fun testTlsRequireSucceedsWithoutCertificateValidation() {
        SyncsTestFixture.testCheck(config(tls, sslMode = RedisSslRequired))
    }

    @Test
    fun testVerifyCaSucceedsWithTrustedCertificate() {
        SyncsTestFixture.testCheck(
            config(tls, sslMode = verifyCa(certificate("ca.crt"))),
        )
    }

    @Test
    fun testVerifyCaRejectsWrongCertificateAuthority() {
        SyncsTestFixture.testCheck(
            config(tls, sslMode = verifyCa(certificate("wrong-ca.crt"))),
            expectedFailure = "The Redis server certificate is not trusted",
        )
    }

    @Test
    fun testVerifyFullRejectsHostnameMismatch() {
        SyncsTestFixture.testCheck(
            config(tls, host = "127.0.0.2", sslMode = verifyFull(certificate("ca.crt"))),
            expectedFailure = "Redis server certificate hostname does not match",
        )
    }

    @Test
    fun testMutualTlsRequiresClientCertificate() {
        SyncsTestFixture.testCheck(
            config(mutualTls, sslMode = verifyCa(certificate("ca.crt"))),
            expectedFailure = "Redis requires a client certificate",
        )
    }

    @Test
    fun testMutualTlsSucceedsWithClientCertificate() {
        SyncsTestFixture.testCheck(
            config(
                mutualTls,
                sslMode =
                    verifyCa(
                        certificate("ca.crt"),
                        certificate("client.crt"),
                        certificate("client.key"),
                    ),
            ),
        )
    }

    @Test
    fun testPlainClientAgainstTlsPortIsClassified() {
        SyncsTestFixture.testCheck(
            config(tls, sslMode = RedisSslDisabled),
            expectedFailure = "The Redis server closed the connection during the handshake",
        )
    }

    @Test
    fun testTlsClientAgainstPlainPortIsClassified() {
        SyncsTestFixture.testCheck(
            config(plain, sslMode = RedisSslRequired),
            expectedFailure = "The configured TLS mode does not match the Redis server",
        )
    }

    @Test
    fun testClusterDatabaseSelectionIsClassified() {
        redisContainer(
                "--cluster-enabled",
                "yes",
                "--cluster-config-file",
                "/tmp/nodes.conf",
                "--cluster-node-timeout",
                "5000",
                "--databases",
                "2",
            )
            .use { redis ->
                redis.start()
                SyncsTestFixture.testCheck(
                    config(redis, database = 1),
                    expectedFailure = "Redis Cluster mode is not supported",
                )
            }
    }

    @Test
    fun testCheckSucceedsThroughSshTunnel() {
        val port = plain.getMappedPort(REDIS_PORT)
        Testcontainers.exposeHostPorts(port)
        SshBastionContainer(tunnelingToHostPort = port).use { bastion ->
            val configuration =
                config(
                        plain,
                        host = DOCKER_HOST_FROM_WITHIN_CONTAINER,
                        port = port,
                    )
                    .apply { setTunnelMethodValue(bastion.outerPasswordAuthTunnelMethod) }
            SyncsTestFixture.testCheck(configuration)
        }
    }

    private fun config(
        redis: GenericContainer<*>,
        host: String = redis.host,
        port: Int = redis.getMappedPort(REDIS_PORT),
        username: String? = null,
        password: String? = null,
        database: Int? = null,
        sslMode: RedisSslModeConfiguration = RedisSslDisabled,
    ) =
        RedisSourceConfigurationSpecification().apply {
            this.host = host
            this.port = port
            this.username = username
            this.password = password
            this.database = database
            setSslModeValue(sslMode)
        }

    private fun createAclUser(
        redis: GenericContainer<*>,
        username: String,
        password: String,
        vararg rules: String,
    ) {
        val result =
            redis.execInContainer(
                "redis-cli",
                "ACL",
                "SETUSER",
                username,
                "on",
                ">$password",
                *rules,
            )
        Assertions.assertEquals(0, result.exitCode, result.stderr)
    }

    private fun verifyCa(
        caCertificate: String,
        clientCertificate: String? = null,
        clientKey: String? = null,
    ) =
        RedisSslVerifyCa().apply {
            this.caCertificate = caCertificate
            this.clientCertificate = clientCertificate
            this.clientKey = clientKey
        }

    private fun verifyFull(caCertificate: String) =
        RedisSslVerifyFull().apply { this.caCertificate = caCertificate }

    private fun certificate(name: String): String = File("$TLS_DIR/$name").readText()

    private fun redisContainer(vararg args: String): GenericContainer<*> =
        RedisTestContainer().withExposedPorts(REDIS_PORT).withCommand("redis-server", *args)

    companion object {
        private const val REDIS_IMAGE = "redis:8"
        private const val REDIS_PORT = 6379
        private val TLS_DIR = File("src/test/resources/tls").absolutePath
        lateinit var plain: GenericContainer<*>
        lateinit var tls: GenericContainer<*>
        lateinit var mutualTls: GenericContainer<*>

        @JvmStatic
        @BeforeAll
        fun startRedisContainers() {
            plain = RedisTestContainer().withExposedPorts(REDIS_PORT)
            plain.start()
            tls = tlsContainer(clientAuth = false)
            tls.start()
            mutualTls = tlsContainer(clientAuth = true)
            mutualTls.start()
        }

        @JvmStatic
        @AfterAll
        fun stopRedisContainers() {
            plain.stop()
            tls.stop()
            mutualTls.stop()
        }

        private fun tlsContainer(clientAuth: Boolean): GenericContainer<*> =
            RedisTestContainer()
                .withExposedPorts(REDIS_PORT)
                .withFileSystemBind(TLS_DIR, "/tls", BindMode.READ_ONLY)
                .withCommand(
                    "redis-server",
                    "--port",
                    "0",
                    "--tls-port",
                    REDIS_PORT.toString(),
                    "--tls-cert-file",
                    "/tls/server.crt",
                    "--tls-key-file",
                    "/tls/server.key",
                    "--tls-ca-cert-file",
                    "/tls/ca.crt",
                    "--tls-auth-clients",
                    if (clientAuth) "yes" else "no",
                )
    }
}
