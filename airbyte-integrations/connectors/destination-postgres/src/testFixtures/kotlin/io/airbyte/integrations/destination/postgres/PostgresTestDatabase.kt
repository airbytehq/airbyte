/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.postgres

import com.google.common.collect.ImmutableMap
import io.airbyte.cdk.db.factory.DatabaseDriver
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.testutils.ContainerFactory
import io.airbyte.cdk.testutils.TestDatabase
import io.airbyte.commons.json.Jsons.jsonNode
import java.io.IOException
import java.io.UncheckedIOException
import java.util.function.Consumer
import java.util.stream.Stream
import org.jooq.SQLDialect
import org.testcontainers.containers.PostgreSQLContainer

/**
 * TODO: This class is a copy from source-postgres:testFixtures. Eventually merge into a common
 * fixtures module.
 */
class PostgresTestDatabase(container: PostgreSQLContainer<*>) :
    TestDatabase<
        PostgreSQLContainer<*>, PostgresTestDatabase, PostgresTestDatabase.PostgresConfigBuilder>(
        container
    ) {
    enum class BaseImage(val reference: String) {
        POSTGRES_16("postgres:16-bullseye"),
        POSTGRES_12("postgres:12-bullseye"),
        POSTGRES_13("postgres:13-alpine"),
        POSTGRES_9("postgres:9-alpine"),
        POSTGRES_SSL_DEV("marcosmarxm/postgres-ssl:dev")
    }

    enum class ContainerModifier(override val modifier: Consumer<PostgreSQLContainer<*>>) :
        ContainerFactory.ContainerModifier<PostgreSQLContainer<*>> {
        ASCII(
            Consumer<PostgreSQLContainer<*>> { container: PostgreSQLContainer<*> ->
                PostgresContainerFactory.Companion.withASCII(container)
            }
        ),
        CONF(
            Consumer<PostgreSQLContainer<*>> { container: PostgreSQLContainer<*> ->
                PostgresContainerFactory.Companion.withConf(container)
            }
        ),
        NETWORK(
            Consumer<PostgreSQLContainer<*>> { container: PostgreSQLContainer<*> ->
                PostgresContainerFactory.Companion.withNetwork(container)
            }
        ),
        SSL(
            Consumer<PostgreSQLContainer<*>> { container: PostgreSQLContainer<*> ->
                PostgresContainerFactory.Companion.withSSL(container)
            }
        ),
        CERT(
            Consumer<PostgreSQLContainer<*>> { container: PostgreSQLContainer<*> ->
                PostgresContainerFactory.Companion.withCert(container)
            }
        ),
    }

    override fun inContainerBootstrapCmd(): Stream<Stream<String>> {
        return Stream.of(
            psqlCmd(
                Stream.of(
                    String.format("CREATE DATABASE %s", databaseName),
                    String.format("CREATE USER %s PASSWORD '%s'", userName, password),
                    String.format(
                        "GRANT ALL PRIVILEGES ON DATABASE %s TO %s",
                        databaseName,
                        userName
                    ),
                    String.format("ALTER USER %s WITH SUPERUSER", userName)
                )
            )
        )
    }

    /**
     * Close resources held by this instance. This deliberately avoids dropping the database, which
     * is really expensive in Postgres. This is because a DROP DATABASE in Postgres triggers a
     * CHECKPOINT. Call [.dropDatabaseAndUser] to explicitly drop the database and the user.
     */
    override fun inContainerUndoBootstrapCmd(): Stream<String> {
        return Stream.empty()
    }

    /** Drop the database owned by this instance. */
    fun dropDatabaseAndUser() {
        execInContainer(
            psqlCmd(
                Stream.of(
                    String.format("DROP DATABASE %s", databaseName),
                    String.format("DROP OWNED BY %s", userName),
                    String.format("DROP USER %s", userName)
                )
            )
        )
    }

    fun psqlCmd(sql: Stream<String>): Stream<String> {
        return Stream.concat(
            Stream.of(
                "psql",
                "-d",
                container.databaseName,
                "-U",
                container.username,
                "-v",
                "ON_ERROR_STOP=1",
                "-a"
            ),
            sql.flatMap { stmt: String -> Stream.of("-c", stmt) }
        )
    }

    override val databaseDriver: DatabaseDriver
        get() = DatabaseDriver.POSTGRESQL

    override val sqlDialect: SQLDialect
        get() = SQLDialect.POSTGRES

    private var cachedCerts: Certificates? = null

    @get:Synchronized
    val certificates: Certificates
        get() {
            if (cachedCerts == null) {
                val caCert: String
                val clientKey: String
                val clientCert: String
                try {
                    caCert =
                        container.execInContainer("su", "-c", "cat ca.crt").stdout.trim {
                            it <= ' '
                        }
                    clientKey =
                        container.execInContainer("su", "-c", "cat client.key").stdout.trim {
                            it <= ' '
                        }
                    clientCert =
                        container.execInContainer("su", "-c", "cat client.crt").stdout.trim {
                            it <= ' '
                        }
                } catch (e: IOException) {
                    throw UncheckedIOException(e)
                } catch (e: InterruptedException) {
                    throw RuntimeException(e)
                }
                cachedCerts = Certificates(caCert, clientCert, clientKey)
            }
            return cachedCerts!!
        }

    @JvmRecord
    data class Certificates(
        val caCertificate: String,
        val clientCertificate: String,
        val clientKey: String
    )

    override fun configBuilder(): PostgresConfigBuilder {
        return PostgresConfigBuilder(this)
    }

    val replicationSlotName: String
        get() = withNamespace("debezium_slot")

    val publicationName: String
        get() = withNamespace("publication")

    fun withReplicationSlot(): PostgresTestDatabase {
        return this.with(
                "SELECT pg_create_logical_replication_slot('%s', 'pgoutput');",
                replicationSlotName
            )
            .onClose("SELECT pg_drop_replication_slot('%s');", replicationSlotName)
    }

    fun withPublicationForAllTables(): PostgresTestDatabase {
        return this.with("CREATE PUBLICATION %s FOR ALL TABLES;", publicationName)
            .onClose("DROP PUBLICATION %s CASCADE;", publicationName)
    }

    class PostgresConfigBuilder(testdb: PostgresTestDatabase) :
        ConfigBuilder<PostgresTestDatabase, PostgresConfigBuilder>(testdb) {
        fun withSchemas(vararg schemas: String?): PostgresConfigBuilder {
            return with(JdbcUtils.SCHEMAS_KEY, listOf(*schemas))
        }

        fun withStandardReplication(): PostgresConfigBuilder {
            return with(
                "replication_method",
                ImmutableMap.builder<Any, Any>().put("method", "Standard").build()
            )
        }

        @JvmOverloads
        fun withCdcReplication(
            lsnCommitBehaviour: String = "While reading Data"
        ): PostgresConfigBuilder {
            return this.with("is_test", true)
                .with(
                    "replication_method",
                    jsonNode(
                        ImmutableMap.builder<Any, Any>()
                            .put("method", "CDC")
                            .put("replication_slot", testDatabase.replicationSlotName)
                            .put("publication", testDatabase.publicationName)
                            .put(
                                "initial_waiting_seconds",
                                DEFAULT_CDC_REPLICATION_INITIAL_WAIT.seconds
                            )
                            .put("lsn_commit_behaviour", lsnCommitBehaviour)
                            .build()
                    )
                )
        }

        fun withXminReplication(): PostgresConfigBuilder {
            return this.with(
                "replication_method",
                jsonNode(ImmutableMap.builder<Any, Any>().put("method", "Xmin").build())
            )
        }
    }

    companion object {
        fun `in`(baseImage: BaseImage, vararg modifiers: ContainerModifier): PostgresTestDatabase {
            val container: PostgreSQLContainer<out PostgreSQLContainer<*>> =
                PostgresContainerFactory().shared(baseImage.reference, *modifiers)
            return PostgresTestDatabase(container).initialized()
        }
    }
}
