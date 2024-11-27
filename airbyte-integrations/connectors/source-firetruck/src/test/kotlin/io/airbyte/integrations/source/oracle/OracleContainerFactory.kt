/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.oracle

import io.airbyte.cdk.testcontainers.TestContainerFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import org.testcontainers.containers.Container
import org.testcontainers.containers.Network
import org.testcontainers.containers.OracleContainer
import org.testcontainers.utility.DockerImageName

object OracleContainerFactory {
    const val COMPATIBLE_NAME = "gvenzl/oracle-xe"
    private val log = KotlinLogging.logger {}

    init {
        TestContainerFactory.register(COMPATIBLE_NAME, ::OracleContainer)
    }

    sealed interface OracleContainerModifier :
        TestContainerFactory.ContainerModifier<OracleContainer>

    data object WithNetwork : OracleContainerModifier {
        override fun modify(container: OracleContainer) {
            container.withNetwork(Network.newNetwork())
        }
    }

    data object WithCdc : OracleContainerModifier {
        override fun modify(container: OracleContainer) {
            container.start()
            log.info { "Creating $RECOVERY_DIR in the container..." }
            container.exec("mkdir -p $RECOVERY_DIR")
            log.info { "Creating $SCRIPT in the container..." }
            for (line in CDC_SQL.lines()) {
                val trimmed: String = line.trim().takeIf { it.isNotBlank() } ?: continue
                container.exec("echo \"$trimmed\" >> $SCRIPT")
            }
            log.info { "Piping $SCRIPT to sqlplus in the container..." }
            container.exec("sqlplus /nolog < $SCRIPT")
            log.info { "Setting the container default user to $CDC_USER..." }
            container.withUsername(CDC_USER)
            log.info { "Done preparing the container for CDC." }
        }

        const val RECOVERY_DIR = "/opt/oracle/oradata/recovery_area"
        const val SCRIPT = "/tmp/cdc.sql"
        const val CDC_USER = "test_cdc"
        const val PDB_NAME = "FREEPDB1"
        const val CDC_PASSWORD = "test"
        const val CDC_SQL =
            """
            CONNECT sys/test AS SYSDBA
            ALTER SYSTEM SET db_recovery_file_dest_size = 1G;
            ALTER SYSTEM SET db_recovery_file_dest = '$RECOVERY_DIR' scope=spfile;
            SHUTDOWN IMMEDIATE
            STARTUP MOUNT
            ALTER DATABASE ARCHIVELOG;
            ALTER DATABASE OPEN;
            ALTER DATABASE ADD SUPPLEMENTAL LOG DATA;
            CREATE USER $CDC_USER IDENTIFIED BY $CDC_PASSWORD;
            GRANT CREATE SESSION, DBA TO $CDC_USER;
            ALTER USER $CDC_USER DEFAULT TABLESPACE users QUOTA UNLIMITED ON users;
            ALTER SESSION SET CONTAINER = $PDB_NAME;
            GRANT CREATE SESSION, DBA TO $CDC_USER;
            ALTER USER $CDC_USER DEFAULT TABLESPACE users QUOTA UNLIMITED ON users;
            EXIT;
        """

        fun Container<*>.exec(cmd: String) {
            val result: Container.ExecResult = execInContainer("sh", "-c", cmd)
            log.info { "EXEC: $cmd" }
            for (line in (result.stdout ?: "").lines()) {
                log.info { "STDOUT: $line" }
            }
            for (line in (result.stderr ?: "").lines()) {
                log.info { "STDOUT: $line" }
            }
            if (result.exitCode != 0) {
                throw RuntimeException("exit code ${result.exitCode} for $cmd")
            }
        }
    }

    fun exclusive(
        imageName: String,
        vararg modifiers: OracleContainerModifier,
    ): OracleContainer {
        val dockerImageName =
            DockerImageName.parse(imageName).asCompatibleSubstituteFor(COMPATIBLE_NAME)
        return TestContainerFactory.exclusive(dockerImageName, *modifiers)
    }

    fun shared(
        imageName: String,
        vararg modifiers: OracleContainerModifier,
    ): OracleContainer {
        val dockerImageName =
            DockerImageName.parse(imageName).asCompatibleSubstituteFor(COMPATIBLE_NAME)
        return TestContainerFactory.shared(dockerImageName, *modifiers)
    }

    @JvmStatic
    fun configSpecification(
        oracleContainer: OracleContainer
    ): OracleSourceConfigurationSpecification =
        OracleSourceConfigurationSpecification().apply {
            host = oracleContainer.host
            port = oracleContainer.oraclePort
            username = oracleContainer.username
            password = oracleContainer.password
            jdbcUrlParams = ""
            schemas = listOf(oracleContainer.username)
            setConnectionDataValue(ServiceName().apply { serviceName = "FREEPDB1" })
            checkpointTargetIntervalSeconds = 60
            concurrency = 1
        }
}
