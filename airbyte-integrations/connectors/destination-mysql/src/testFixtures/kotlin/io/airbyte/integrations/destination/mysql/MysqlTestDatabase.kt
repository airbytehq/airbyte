/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql

import io.airbyte.cdk.db.factory.DatabaseDriver
import io.airbyte.cdk.testutils.TestDatabase
import java.util.stream.Collectors
import java.util.stream.Stream
import org.jooq.SQLDialect
import org.testcontainers.containers.MySQLContainer

/** Much like the destination-postgres PostgresTestDatabase, this was copied from source-mysql. */
class MysqlTestDatabase(container: MySQLContainer<*>) :
    TestDatabase<MySQLContainer<*>, MysqlTestDatabase, MysqlTestDatabase.MySQLConfigBuilder>(
        container,
    ) {
    enum class BaseImage(val reference: String) {
        MYSQL_8("mysql:8.0"),
    }

    enum class ContainerModifier(val methodName: String) {
        MOSCOW_TIMEZONE("withMoscowTimezone"),
        INVALID_TIMEZONE_CEST("withInvalidTimezoneCEST"),
        ROOT_AND_SERVER_CERTIFICATES("withRootAndServerCertificates"),
        CLIENT_CERTITICATE("withClientCertificate"),
        NETWORK("withNetwork"),
        CUSTOM_NAME("withCustomName")
    }

    override fun inContainerBootstrapCmd(): Stream<Stream<String>> {
        // Besides setting up user and privileges, we also need to create a soft link otherwise
        // airbyte-ci on github runner would not be able to connect to DB, because the sock file
        // does not
        // exist.
        return Stream.of(
            Stream.of(
                "sh",
                "-c",
                "ln -s -f /var/lib/mysql/mysql.sock /var/run/mysqld/mysqld.sock",
            ),
            mysqlCmd(
                Stream.of(
                    String.format("SET GLOBAL max_connections=%d", MAX_CONNECTIONS),
                    String.format("CREATE DATABASE \\`%s\\`", databaseName),
                    String.format(
                        "CREATE USER '%s' IDENTIFIED BY '%s'",
                        userName,
                        password,
                    ),
                    // Grant privileges also to the container's user, which is not root.
                    String.format(
                        "GRANT ALL PRIVILEGES ON *.* TO '%s', '%s' WITH GRANT OPTION",
                        userName,
                        container.username,
                    ),
                    "set global local_infile=true",
                    "REVOKE ALL PRIVILEGES, GRANT OPTION FROM $userName@'%'",
                    "GRANT ALTER, CREATE, INSERT, INDEX, UPDATE, DELETE, SELECT, DROP ON *.* TO $userName@'%'"
                ),
            ),
        )
    }

    override fun inContainerUndoBootstrapCmd(): Stream<String> {
        return mysqlCmd(
            Stream.of(
                String.format("DROP USER '%s'", userName),
                String.format("DROP DATABASE \\`%s\\`", databaseName),
            ),
        )
    }

    override val databaseDriver: DatabaseDriver
        get() = DatabaseDriver.MYSQL

    override val sqlDialect: SQLDialect
        get() = SQLDialect.MYSQL

    override fun configBuilder(): MySQLConfigBuilder {
        return MySQLConfigBuilder(this)
    }

    fun mysqlCmd(sql: Stream<String>): Stream<String> {
        return Stream.of(
            "bash",
            "-c",
            String.format(
                "set -o errexit -o pipefail; echo \"%s\" | mysql -v -v -v --user=root --password=test",
                sql.collect(Collectors.joining("; ")),
            ),
        )
    }

    class MySQLConfigBuilder(testDatabase: MysqlTestDatabase) :
        ConfigBuilder<MysqlTestDatabase, MySQLConfigBuilder>(testDatabase)

    companion object {
        fun `in`(baseImage: BaseImage, vararg methods: ContainerModifier?): MysqlTestDatabase {
            val methodNames =
                Stream.of(*methods)
                    .map<String> { im: ContainerModifier? -> im?.methodName }
                    .toList()
                    .toTypedArray<String>()
            val container: MySQLContainer<out MySQLContainer<*>?> =
                MySQLContainerFactory().shared(baseImage.reference, *methodNames)
            return MysqlTestDatabase(container).initialized()
        }

        private const val MAX_CONNECTIONS = 1000
    }
}
