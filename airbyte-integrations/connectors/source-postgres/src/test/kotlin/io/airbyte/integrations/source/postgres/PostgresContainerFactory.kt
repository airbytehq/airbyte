/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.testcontainers.TestContainerFactory
import io.airbyte.integrations.source.postgres.config.EncryptionDisable
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfigurationSpecification
import io.airbyte.integrations.source.postgres.config.StandardReplicationMethodConfigurationSpecification
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.IOException
import java.io.UncheckedIOException
import org.testcontainers.containers.Network
import org.testcontainers.containers.PostgreSQLContainer
import org.testcontainers.utility.DockerImageName
import org.testcontainers.utility.MountableFile

object PostgresContainerFactory {
    private const val POSTGRES_17_BULLSEYE = "postgres:17-bullseye"
    private val log = KotlinLogging.logger {}

    init {
        TestContainerFactory.register(POSTGRES_17_BULLSEYE, ::PostgreSQLContainer)
    }

    sealed interface PostgresContainerModifier :
        TestContainerFactory.ContainerModifier<PostgreSQLContainer<*>>

    /** Apply the postgresql.conf file that we've packaged as a resource. */
    data object withConf : PostgresContainerModifier {
        override fun modify(container: PostgreSQLContainer<*>) {
            container
                .withCopyFileToContainer(
                    MountableFile.forClasspathResource("postgresql.conf"),
                    "/etc/postgresql/postgresql.conf",
                )
                .withCommand("postgres -c config_file=/etc/postgresql/postgresql.conf")
        }
    }

    /** Create a new network and bind it to the container. */
    data object withNetwork : PostgresContainerModifier {
        override fun modify(container: PostgreSQLContainer<*>) {
            container.withNetwork(Network.newNetwork())
        }
    }

    /** Configure postgres with wal_level=logical. */
    data object withWalLevelLogical : PostgresContainerModifier {
        override fun modify(container: PostgreSQLContainer<*>) {
            container.withCommand("postgres -c wal_level=logical")
        }
    }

    /** Generate SSL certificates and tell postgres to enable SSL and use them. */
    data object withCert : PostgresContainerModifier {
        override fun modify(container: PostgreSQLContainer<*>) {
            container.start()
            val commands =
                arrayOf<String?>(
                    "psql -U test -c \"CREATE USER postgres WITH PASSWORD 'postgres';\"",
                    "psql -U test -c \"GRANT CONNECT ON DATABASE \"test\" TO postgres;\"",
                    "psql -U test -c \"ALTER USER postgres WITH SUPERUSER;\"",
                    "openssl ecparam -name prime256v1 -genkey -noout -out ca.key",
                    "openssl req -new -x509 -sha256 -key ca.key -out ca.crt -subj \"/CN=127.0.0.1\"",
                    "openssl ecparam -name prime256v1 -genkey -noout -out server.key",
                    "openssl req -new -sha256 -key server.key -out server.csr -subj \"/CN=localhost\"",
                    "openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365 -sha256",
                    "cp server.key /etc/ssl/private/",
                    "cp server.crt /etc/ssl/private/",
                    "cp ca.crt /etc/ssl/private/",
                    "chmod og-rwx /etc/ssl/private/server.* /etc/ssl/private/ca.*",
                    "chown postgres:postgres /etc/ssl/private/server.crt /etc/ssl/private/server.key /etc/ssl/private/ca.crt",
                    "echo \"ssl = on\" >> /var/lib/postgresql/data/postgresql.conf",
                    "echo \"ssl_cert_file = '/etc/ssl/private/server.crt'\" >> /var/lib/postgresql/data/postgresql.conf",
                    "echo \"ssl_key_file = '/etc/ssl/private/server.key'\" >> /var/lib/postgresql/data/postgresql.conf",
                    "echo \"ssl_ca_file = '/etc/ssl/private/ca.crt'\" >> /var/lib/postgresql/data/postgresql.conf",
                    "mkdir root/.postgresql",
                    "echo \"hostssl    all    all    127.0.0.1/32    cert clientcert=verify-full\" >> /var/lib/postgresql/data/pg_hba.conf",
                    "openssl ecparam -name prime256v1 -genkey -noout -out client.key",
                    "openssl req -new -sha256 -key client.key -out client.csr -subj \"/CN=postgres\"",
                    "openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 365 -sha256",
                    "cp client.crt ~/.postgresql/postgresql.crt",
                    "cp client.key ~/.postgresql/postgresql.key",
                    "chmod 0600 ~/.postgresql/postgresql.crt ~/.postgresql/postgresql.key",
                    "cp ca.crt root/.postgresql/ca.crt",
                    "chown postgres:postgres ~/.postgresql/ca.crt",
                    "psql -U test -c \"SELECT pg_reload_conf();\"",
                )
            for (cmd in commands) {
                try {
                    container.execInContainer("su", "-c", cmd)
                } catch (e: IOException) {
                    throw UncheckedIOException(e)
                } catch (e: InterruptedException) {
                    throw RuntimeException(e)
                }
            }
        }
    }

    /** Tell postgres to enable SSL. */
    data object withSSL : PostgresContainerModifier {
        override fun modify(container: PostgreSQLContainer<*>) {
            container.withCommand(
                "postgres " +
                    "-c ssl=on " +
                    "-c ssl_cert_file=/var/lib/postgresql/server.crt " +
                    "-c ssl_key_file=/var/lib/postgresql/server.key",
            )
        }
    }

    /** Configure postgres with client_encoding=sql_ascii. */
    data object withASCII : PostgresContainerModifier {
        override fun modify(container: PostgreSQLContainer<*>) {
            container.withCommand("postgres -c client_encoding=sql_ascii")
        }
    }

    fun shared17(): PostgreSQLContainer<*> {
        val dockerImageName = DockerImageName.parse(POSTGRES_17_BULLSEYE)
        return TestContainerFactory.shared(dockerImageName)
    }

    @JvmStatic
    fun config(
        postgresContainer: PostgreSQLContainer<*>,
        schemas: List<String> = listOf("public"),
    ): PostgresSourceConfigurationSpecification =
        PostgresSourceConfigurationSpecification().apply {
            host = postgresContainer.host
            port = postgresContainer.getMappedPort(PostgreSQLContainer.POSTGRESQL_PORT)
            username = postgresContainer.username
            password = postgresContainer.password
            jdbcUrlParams = ""
            encryptionJson = EncryptionDisable
            database = "test"
            this.schemas = schemas
            checkpointTargetIntervalSeconds = 60
            max_db_connections = 1
            setIncrementalConfigurationSpecificationValue(
                StandardReplicationMethodConfigurationSpecification
            )
        }
}
