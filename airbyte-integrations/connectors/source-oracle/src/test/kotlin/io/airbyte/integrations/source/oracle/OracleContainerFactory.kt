/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.oracle

import io.airbyte.cdk.testcontainers.TestContainerFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Duration
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
        TestContainerFactory.ContainerModifier<OracleContainer> {

        fun Container<*>.exec(cmd: String): Container.ExecResult {
            val result: Container.ExecResult = execInContainer("sh", "-c", cmd)
            log.info { "EXEC: $cmd" }
            for (line in (result.stdout ?: "").lines()) {
                log.info { "STDOUT: $line" }
            }
            for (line in (result.stderr ?: "").lines()) {
                log.info { "STDERR: $line" }
            }
            if (result.exitCode != 0) {
                throw RuntimeException("exit code ${result.exitCode} for $cmd")
            }
            return result
        }

        fun Container<*>.append(destination: String, contents: String) {
            log.info { "EXEC: appending data to $destination" }
            for (line in contents.lines()) {
                val cmd = "echo \"$line\" >> $destination"
                val result: Container.ExecResult = execInContainer("sh", "-c", cmd)
                if (result.exitCode != 0) {
                    throw RuntimeException("exit code ${result.exitCode} for $cmd")
                }
            }
        }
    }

    data object WithNetwork : OracleContainerModifier {
        override fun modify(container: OracleContainer) {
            container.withNetwork(Network.newNetwork())
        }
    }

    data object WithSslAndNne : OracleContainerModifier {
        override fun modify(container: OracleContainer) {
            container.addExposedPort(2484)
            container.start()
            log.info { "Creating Oracle Wallet in the container..." }
            container.exec(walletCreate)
            log.info { "Creating self-signed certificate and adding it to Oracle Wallet..." }
            container.exec(walletAdd)
            log.info { "Exporting self-signed certificate from Oracle Wallet..." }
            container.exec(walletExport)
            log.info { "Shutting down database..." }
            container.exec("echo 'SHUTDOWN IMMEDIATE;' | sqlplus / AS SYSDBA")
            log.info { "Stopping listener..." }
            container.exec("lsnrctl stop")
            log.info { "Rewriting sqlnet.ora..." }
            container.exec("echo > $SQLNET_ORA_PATH")
            container.append(SQLNET_ORA_PATH, SQLNET_ORA_CONTENTS)
            log.info { "Rewriting listener.ora..." }
            container.exec("echo > $LISTENER_ORA_PATH")
            container.append(LISTENER_ORA_PATH, LISTENER_ORA_CONTENTS)
            log.info { "Restarting listener..." }
            container.exec("lsnrctl start")
            log.info { "Restarting database..." }
            container.exec("echo 'STARTUP;' | sqlplus / AS SYSDBA")
            log.info { "Wait for service registration..." }
            while (true) {
                val result: Container.ExecResult = container.exec("lsnrctl status")
                if (result.stdout.contains("The listener supports no services")) {
                    Thread.sleep(Duration.ofSeconds(1))
                } else {
                    break
                }
            }
            log.info { "Done configuring Oracle container for SSL and NNE." }
        }

        fun decorateWithSSL(
            configSpec: OracleSourceConfigurationSpecification,
            container: OracleContainer
        ) {
            val result: Container.ExecResult = container.execInContainer("cat", CERT_CRT)
            if (result.exitCode != 0) {
                throw RuntimeException("exit code ${result.exitCode} for exporting $CERT_CRT")
            }
            val encryption: Encryption = SslCertificate().apply { sslCertificate = result.stdout }
            configSpec.setEncryptionValue(encryption)
            configSpec.port = container.getMappedPort(2484)
        }

        const val WALLET_PATH = "/opt/oracle/wallet"
        const val WALLET_PASSWORD = "foobarbaz1"
        const val ORACLE_HOME = "/opt/oracle/product/23ai/dbhomeFree"
        const val LISTENER_ORA_PATH = "$ORACLE_HOME/network/admin/listener.ora"
        const val SQLNET_ORA_PATH = "$ORACLE_HOME/network/admin/sqlnet.ora"
        const val CERT_DN = "CN=testsecurity Root,O=testsecurity,C=US"
        const val CERT_CRT = "cert.crt"

        val walletCreate: String =
            listOf(
                    "orapki wallet",
                    "create",
                    "-wallet $WALLET_PATH",
                    "-pwd $WALLET_PASSWORD",
                    "-auto_login",
                )
                .joinToString(separator = " ")

        val walletAdd: String =
            listOf(
                    "orapki wallet",
                    "add",
                    "-wallet $WALLET_PATH",
                    "-pwd $WALLET_PASSWORD",
                    "-dn '$CERT_DN'",
                    "-self_signed",
                    "-validity 365",
                    "-keysize 1024",
                )
                .joinToString(separator = " ")

        val walletExport: String =
            listOf(
                    "orapki wallet",
                    "export",
                    "-wallet $WALLET_PATH",
                    "-pwd $WALLET_PASSWORD",
                    "-dn '$CERT_DN'",
                    "-cert $CERT_CRT",
                )
                .joinToString(separator = " ")

        const val LISTENER_ORA_CONTENTS =
            """
LISTENER =
  (DESCRIPTION_LIST =
    (DESCRIPTION =
      (ADDRESS = (PROTOCOL = IPC)(KEY = EXTPROC_FOR_FREE))
      (ADDRESS = (PROTOCOL = TCP)(HOST = 0.0.0.0)(PORT = 1521))
      (ADDRESS = (PROTOCOL = TCPS)(HOST = 0.0.0.0)(PORT = 2484))
    )
  )

DEFAULT_SERVICE_LISTENER = FREE

SSL_VERSION = 1.2
SSL_CLIENT_AUTHENTICATION = FALSE
WALLET_LOCATION = (SOURCE = (METHOD = FILE)(METHOD_DATA = (DIRECTORY = $WALLET_PATH)))
"""

        const val SQLNET_ORA_CONTENTS =
            """
NAMES.DIRECTORY_PATH = (EZCONNECT, TNSNAMES)
# See https://github.com/gvenzl/oci-oracle-xe/issues/43
DISABLE_OOB=ON
BREAK_POLL_SKIP=1000

SSL_VERSION = 1.2
SSL_CLIENT_AUTHENTICATION = FALSE
WALLET_LOCATION = (SOURCE = (METHOD = FILE)(METHOD_DATA = (DIRECTORY = $WALLET_PATH)))

SQLNET.ENCRYPTION_SERVER = REQUIRED
SQLNET.ENCRYPTION_TYPES_SERVER = (AES256, AES192, AES128)
"""
    }

    data object WithCdc : OracleContainerModifier {
        override fun modify(container: OracleContainer) {
            container.start()
            log.info { "Creating $RECOVERY_DIR in the container..." }
            container.exec("mkdir -p $RECOVERY_DIR")
            log.info { "Creating $SCRIPT in the container..." }
            container.append(SCRIPT, CDC_SQL)
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
