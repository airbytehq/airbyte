/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.legacy.testFixtures

import com.google.common.collect.ImmutableMap
import io.airbyte.cdk.test.fixtures.legacy.DatabaseDriver
import io.airbyte.cdk.test.fixtures.legacy.JdbcUtils
import io.airbyte.cdk.test.fixtures.legacy.Jsons
import io.airbyte.cdk.test.fixtures.legacy.TestDatabase
import io.airbyte.integrations.source.postgres.legacy.testFixtures.PostgresSpecConstants.INVALID_CDC_CURSOR_POSITION_PROPERTY
import io.airbyte.integrations.source.postgres.legacy.testFixtures.PostgresSpecConstants.RESYNC_DATA_OPTION
import java.io.IOException
import java.io.UncheckedIOException
import java.util.List
import java.util.stream.Stream
import org.jooq.SQLDialect
import org.testcontainers.containers.PostgreSQLContainer

class PostgresTestDatabase(container: PostgreSQLContainer<*>) :
    TestDatabase<
        PostgreSQLContainer<*>,
        PostgresTestDatabase,
        PostgresTestDatabase.PostgresConfigBuilder,
    >(
        container,
    ) {
    enum class BaseImage(reference: String, majorVersion: Int) {
        POSTGRES_17("postgres:17-bullseye", 17),
        POSTGRES_16("postgres:16-bullseye", 16),
        POSTGRES_12("postgres:12-bullseye", 12),
        POSTGRES_9("postgres:9-alpine", 9),
        POSTGRES_SSL_DEV("marcosmarxm/postgres-ssl:dev", 16);

        val reference: String
        val majorVersion: Int

        init {
            this.reference = reference
            this.majorVersion = majorVersion
        }
    }

    enum class ContainerModifier(methodName: String) {
        ASCII("withASCII"),
        CONF("withConf"),
        NETWORK("withNetwork"),
        SSL("withSSL"),
        WAL_LEVEL_LOGICAL("withWalLevelLogical"),
        CERT("withCert"),
        ;

        val methodName: String

        init {
            this.methodName = methodName
        }
    }

    override fun inContainerBootstrapCmd(): Stream<Stream<String>> {
        return Stream.of<Stream<String>>(
            psqlCmd(
                Stream.of<String?>(
                    String.format("CREATE DATABASE %s", databaseName),
                    String.format("CREATE USER %s PASSWORD '%s'", userName, password),
                    String.format(
                        "GRANT ALL PRIVILEGES ON DATABASE %s TO %s",
                        databaseName,
                        userName,
                    ),
                    String.format("ALTER USER %s WITH SUPERUSER", userName),
                ),
            ),
        )
    }

    /**
     * Close resources held by this instance. This deliberately avoids dropping the database, which
     * is really expensive in Postgres. This is because a DROP DATABASE in Postgres triggers a
     * CHECKPOINT. Call [.dropDatabaseAndUser] to explicitly drop the database and the user.
     */
    override fun inContainerUndoBootstrapCmd(): Stream<String> {
        return Stream.empty<String>()
    }

    /** Drop the database owned by this instance. */
    fun dropDatabaseAndUser() {
        execInContainer(
            psqlCmd(
                Stream.of<String?>(
                    String.format("DROP DATABASE %s", databaseName),
                    String.format("DROP OWNED BY %s", userName),
                    String.format("DROP USER %s", userName),
                ),
            ),
        )
    }

    fun psqlCmd(sql: Stream<String>): Stream<String> {
        return Stream.concat<String>(
            Stream.of<String>(
                "psql",
                "-d",
                container.getDatabaseName(),
                "-U",
                container.getUsername(),
                "-v",
                "ON_ERROR_STOP=1",
                "-a",
            ),
            sql.flatMap<String?> { stmt: String? -> Stream.of<String?>("-c", stmt) },
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
                        container.execInContainer("su", "-c", "cat ca.crt").getStdout().trim {
                            it <= ' '
                        }
                    clientKey =
                        container.execInContainer("su", "-c", "cat client.key").getStdout().trim {
                            it <= ' '
                        }
                    clientCert =
                        container.execInContainer("su", "-c", "cat client.crt").getStdout().trim {
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
        val caCertificate: String?,
        val clientCertificate: String?,
        val clientKey: String?
    )

    override fun configBuilder(): PostgresConfigBuilder {
        return PostgresConfigBuilder(this)
    }

    val replicationSlotName: String?
        get() = withNamespace("debezium_slot")

    val publicationName: String?
        get() = withNamespace("publication")

    fun withReplicationSlot(): PostgresTestDatabase? {
        return this.with(
                "SELECT pg_create_logical_replication_slot('%s', 'pgoutput');",
                this.replicationSlotName,
            )
            .onClose("SELECT pg_drop_replication_slot('%s');", this.replicationSlotName)
    }

    fun withPublicationForAllTables(): PostgresTestDatabase? {
        return this.with("CREATE PUBLICATION %s FOR ALL TABLES;", this.publicationName)
            .onClose("DROP PUBLICATION %s CASCADE;", this.publicationName)
    }

    class PostgresConfigBuilder(testdb: PostgresTestDatabase) :
        ConfigBuilder<PostgresTestDatabase, PostgresConfigBuilder>(
            testdb,
        ) {
        fun withSchemas(vararg schemas: String?): PostgresConfigBuilder {
            return with(JdbcUtils.SCHEMAS_KEY, List.of<String?>(*schemas))
        }

        fun withStandardReplication(): PostgresConfigBuilder {
            return with(
                "replication_method",
                ImmutableMap.builder<Any, Any>().put("method", "Standard").build(),
            )
        }

        @JvmOverloads
        fun withCdcReplication(
            LsnCommitBehaviour: String = "While reading Data",
            cdcCursorFailBehaviour: String = RESYNC_DATA_OPTION
        ): PostgresConfigBuilder {
            return this.with("is_test", true)
                .with(
                    "replication_method",
                    Jsons.jsonNode<ImmutableMap<Any, Any>?>(
                        ImmutableMap.builder<Any?, Any?>()
                            .put("method", "CDC")
                            .put("replication_slot", testDatabase.replicationSlotName)
                            .put("publication", testDatabase.publicationName)
                            .put(
                                "initial_waiting_seconds",
                                DEFAULT_CDC_REPLICATION_INITIAL_WAIT.getSeconds(),
                            )
                            .put("lsn_commit_behaviour", LsnCommitBehaviour)
                            .put(INVALID_CDC_CURSOR_POSITION_PROPERTY, cdcCursorFailBehaviour)
                            .build(),
                    ),
                )
        }

        fun withXminReplication(): PostgresConfigBuilder {
            return this.with(
                "replication_method",
                Jsons.jsonNode<ImmutableMap<Any, Any>>(
                    ImmutableMap.builder<Any, Any>().put("method", "Xmin").build(),
                ),
            )
        }
    }

    override fun close() {
        //        PostgresDebeziumStateUtil.disposeInitialState() // TODO: check here
        super.close()
    }

    companion object {
        @Suppress("deprecation")
        fun `in`(baseImage: BaseImage, vararg modifiers: ContainerModifier?): PostgresTestDatabase {
            val methodNames =
                Stream.of<ContainerModifier>(
                        *modifiers,
                    )
                    .map<String?> { im: ContainerModifier -> im.methodName }
                    .toList()
                    .toTypedArray<String>()
            val container: PostgreSQLContainer<*> =
                PostgresContainerFactory().shared(baseImage.reference, *methodNames)
            return PostgresTestDatabase(container).initialized()
        }
    }
}
