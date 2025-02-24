/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2.config

import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue
import org.junit.jupiter.api.Test

internal class DataSourceFactoryTest {

    @Test
    fun `test data source base url conversion`() {
        val config =
            Fixtures.defaultConfig.copy(
                host = "myhost",
                port = 1234,
                database = "db",
            )
        val dataSource = config.toSQLServerDataSource()
        assertTrue { dataSource.url.startsWith("jdbc:sqlserver://myhost:1234;databaseName=db;") }
    }

    @Test
    fun `test data source handles optional passwords conversion`() {
        val config =
            Fixtures.defaultConfig.copy(
                user = "airbyte-test",
                password = null,
            )
        val dataSource = config.toSQLServerDataSource()
        assertEquals("airbyte-test", dataSource.user)
    }

    @Test
    fun `test jdbc params passthrough`() {
        val config = Fixtures.defaultConfig.copy(jdbcUrlParams = "custom=params")
        val dataSource = config.toSQLServerDataSource()
        assertTrue { dataSource.url.endsWith(";custom=params") }
    }

    @Test
    fun `test unencrypted config`() {
        val config = Fixtures.defaultConfig.copy(sslMethod = Unencrypted())
        val dataSource = config.toSQLServerDataSource()
        assertTrue { dataSource.url.contains(";encrypt=false") }
        assertFalse { dataSource.url.contains(";encrypt=true") }
    }

    @Test
    fun `test encrypted trust config`() {
        val config = Fixtures.defaultConfig.copy(sslMethod = EncryptedTrust())
        val dataSource = config.toSQLServerDataSource()
        assertTrue { dataSource.url.contains(";encrypt=true;trustServerCertificate=true") }
        assertFalse { dataSource.url.contains(";encrypt=false") }
    }

    @Test
    fun `test encrypted verify config`() {
        val sslMethod =
            EncryptedVerify(
                trustStoreName = "name",
                trustStorePassword = "password",
                hostNameInCertificate = "cert-host"
            )
        val config = Fixtures.defaultConfig.copy(sslMethod = sslMethod)
        val dataSource = config.toSQLServerDataSource()
        assertTrue { dataSource.url.contains(";encrypt=true") }
        assertTrue { dataSource.url.contains(";trustStoreName=${sslMethod.trustStoreName}") }
        assertTrue {
            dataSource.url.contains(";trustStorePassword=${sslMethod.trustStorePassword}")
        }
        assertTrue {
            dataSource.url.contains(";hostNameInCertificate=${sslMethod.hostNameInCertificate}")
        }
        assertFalse { dataSource.url.contains(";encrypt=false") }
        assertFalse { dataSource.url.contains(";trustServerCertificate=true") }
    }

    object Fixtures {
        val defaultConfig =
            MSSQLConfiguration(
                host = "localhost",
                port = 1433,
                database = "master",
                schema = "dbo",
                user = "airbyte",
                password = "super secure o//",
                jdbcUrlParams = null,
                sslMethod = Unencrypted(),
            )
    }
}
