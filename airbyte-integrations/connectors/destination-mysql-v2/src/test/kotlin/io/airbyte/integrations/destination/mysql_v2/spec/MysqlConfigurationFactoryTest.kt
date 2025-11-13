/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql_v2.spec

import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class MysqlConfigurationFactoryTest {

    private lateinit var factory: MysqlConfigurationFactory

    @BeforeEach
    fun setup() {
        factory = MysqlConfigurationFactory()
    }

    // ========== Basic Configuration Tests ==========

    @Test
    fun testMakeWithoutExceptionHandlingBasicConfig() {
        val spec = mockk<MysqlSpecification>(relaxed = true) {
            every { host } returns "localhost"
            every { port } returns 3306
            every { database } returns "test_db"
            every { username } returns "test_user"
            every { password } returns "test_password"
            every { ssl } returns false
            every { sslMode } returns SslMode.DISABLED
            every { jdbcUrlParams } returns null
            every { batchSize } returns 5000
        }

        val config = factory.makeWithoutExceptionHandling(spec)

        assertEquals("localhost", config.host)
        assertEquals(3306, config.port)
        assertEquals("test_db", config.database)
        assertEquals("test_user", config.username)
        assertEquals("test_password", config.password)
        assertFalse(config.ssl)
        assertEquals(SslMode.DISABLED, config.sslMode)
        assertNull(config.jdbcUrlParams)
        assertEquals(5000, config.batchSize)
    }

    @Test
    fun testMakeWithAllFieldsPopulated() {
        val spec = mockk<MysqlSpecification>(relaxed = true) {
            every { host } returns "db.example.com"
            every { port } returns 3307
            every { database } returns "production_db"
            every { username } returns "admin"
            every { password } returns "securePassword123"
            every { ssl } returns true
            every { sslMode } returns SslMode.VERIFY_IDENTITY
            every { jdbcUrlParams } returns "connectTimeout=10000&socketTimeout=60000"
            every { batchSize } returns 10000
        }

        val config = factory.makeWithoutExceptionHandling(spec)

        assertEquals("db.example.com", config.host)
        assertEquals(3307, config.port)
        assertEquals("production_db", config.database)
        assertEquals("admin", config.username)
        assertEquals("securePassword123", config.password)
        assertTrue(config.ssl)
        assertEquals(SslMode.VERIFY_IDENTITY, config.sslMode)
        assertEquals("connectTimeout=10000&socketTimeout=60000", config.jdbcUrlParams)
        assertEquals(10000, config.batchSize)
    }

    // ========== SSL Mode Tests ==========

    @Test
    fun testMakeWithSslModeDisabled() {
        val spec = mockk<MysqlSpecification>(relaxed = true) {
            every { host } returns "localhost"
            every { port } returns 3306
            every { database } returns "test_db"
            every { username } returns "user"
            every { password } returns "pass"
            every { ssl } returns false
            every { sslMode } returns SslMode.DISABLED
            every { jdbcUrlParams } returns null
            every { batchSize } returns 5000
        }

        val config = factory.makeWithoutExceptionHandling(spec)
        assertEquals(SslMode.DISABLED, config.sslMode)
    }

    @Test
    fun testMakeWithSslModePreferred() {
        val spec = mockk<MysqlSpecification>(relaxed = true) {
            every { host } returns "localhost"
            every { port } returns 3306
            every { database } returns "test_db"
            every { username } returns "user"
            every { password } returns "pass"
            every { ssl } returns true
            every { sslMode } returns SslMode.PREFERRED
            every { jdbcUrlParams } returns null
            every { batchSize } returns 5000
        }

        val config = factory.makeWithoutExceptionHandling(spec)
        assertEquals(SslMode.PREFERRED, config.sslMode)
    }

    @Test
    fun testMakeWithSslModeRequired() {
        val spec = mockk<MysqlSpecification>(relaxed = true) {
            every { host } returns "localhost"
            every { port } returns 3306
            every { database } returns "test_db"
            every { username } returns "user"
            every { password } returns "pass"
            every { ssl } returns true
            every { sslMode } returns SslMode.REQUIRED
            every { jdbcUrlParams } returns null
            every { batchSize } returns 5000
        }

        val config = factory.makeWithoutExceptionHandling(spec)
        assertEquals(SslMode.REQUIRED, config.sslMode)
    }

    @Test
    fun testMakeWithSslModeVerifyCa() {
        val spec = mockk<MysqlSpecification>(relaxed = true) {
            every { host } returns "localhost"
            every { port } returns 3306
            every { database } returns "test_db"
            every { username } returns "user"
            every { password } returns "pass"
            every { ssl } returns true
            every { sslMode } returns SslMode.VERIFY_CA
            every { jdbcUrlParams } returns null
            every { batchSize } returns 5000
        }

        val config = factory.makeWithoutExceptionHandling(spec)
        assertEquals(SslMode.VERIFY_CA, config.sslMode)
    }

    @Test
    fun testMakeWithSslModeVerifyIdentity() {
        val spec = mockk<MysqlSpecification>(relaxed = true) {
            every { host } returns "localhost"
            every { port } returns 3306
            every { database } returns "test_db"
            every { username } returns "user"
            every { password } returns "pass"
            every { ssl } returns true
            every { sslMode } returns SslMode.VERIFY_IDENTITY
            every { jdbcUrlParams } returns null
            every { batchSize } returns 5000
        }

        val config = factory.makeWithoutExceptionHandling(spec)
        assertEquals(SslMode.VERIFY_IDENTITY, config.sslMode)
    }

    @Test
    fun testMakeWithNullSslModeDefaultsToPreferred() {
        val spec = mockk<MysqlSpecification>(relaxed = true) {
            every { host } returns "localhost"
            every { port } returns 3306
            every { database } returns "test_db"
            every { username } returns "user"
            every { password } returns "pass"
            every { ssl } returns false
            every { sslMode } returns null
            every { jdbcUrlParams } returns null
            every { batchSize } returns 5000
        }

        val config = factory.makeWithoutExceptionHandling(spec)
        assertEquals(SslMode.PREFERRED, config.sslMode)
    }

    // ========== Default Value Tests ==========

    @Test
    fun testDefaultPortValue() {
        val spec = mockk<MysqlSpecification> {
            every { host } returns "localhost"
            every { port } returns 3306  // Default MySQL port
            every { database } returns "test_db"
            every { username } returns "user"
            every { password } returns "pass"
            every { ssl } returns false
            every { sslMode } returns SslMode.PREFERRED
            every { jdbcUrlParams } returns null
            every { batchSize } returns 5000
        }

        val config = factory.makeWithoutExceptionHandling(spec)
        assertEquals(3306, config.port)
    }

    @Test
    fun testDefaultBatchSize() {
        val spec = mockk<MysqlSpecification>(relaxed = true) {
            every { host } returns "localhost"
            every { port } returns 3306
            every { database } returns "test_db"
            every { username } returns "user"
            every { password } returns "pass"
            every { ssl } returns false
            every { sslMode } returns SslMode.PREFERRED
            every { jdbcUrlParams } returns null
            every { batchSize } returns 5000  // Default batch size
        }

        val config = factory.makeWithoutExceptionHandling(spec)
        assertEquals(5000, config.batchSize)
    }

    @Test
    fun testDefaultSslFalse() {
        val spec = mockk<MysqlSpecification>(relaxed = true) {
            every { host } returns "localhost"
            every { port } returns 3306
            every { database } returns "test_db"
            every { username } returns "user"
            every { password } returns "pass"
            every { ssl } returns false  // Default SSL value
            every { sslMode } returns SslMode.PREFERRED
            every { jdbcUrlParams } returns null
            every { batchSize } returns 5000
        }

        val config = factory.makeWithoutExceptionHandling(spec)
        assertFalse(config.ssl)
    }

    // ========== JDBC URL Parameters Tests ==========

    @Test
    fun testMakeWithNullJdbcUrlParams() {
        val spec = mockk<MysqlSpecification>(relaxed = true) {
            every { host } returns "localhost"
            every { port } returns 3306
            every { database } returns "test_db"
            every { username } returns "user"
            every { password } returns "pass"
            every { ssl } returns false
            every { sslMode } returns SslMode.PREFERRED
            every { jdbcUrlParams } returns null
            every { batchSize } returns 5000
        }

        val config = factory.makeWithoutExceptionHandling(spec)
        assertNull(config.jdbcUrlParams)
    }

    @Test
    fun testMakeWithEmptyJdbcUrlParams() {
        val spec = mockk<MysqlSpecification>(relaxed = true) {
            every { host } returns "localhost"
            every { port } returns 3306
            every { database } returns "test_db"
            every { username } returns "user"
            every { password } returns "pass"
            every { ssl } returns false
            every { sslMode } returns SslMode.PREFERRED
            every { jdbcUrlParams } returns ""
            every { batchSize } returns 5000
        }

        val config = factory.makeWithoutExceptionHandling(spec)
        assertEquals("", config.jdbcUrlParams)
    }

    @Test
    fun testMakeWithComplexJdbcUrlParams() {
        val params = "connectTimeout=10000&socketTimeout=60000&useSSL=true&requireSSL=false"
        val spec = mockk<MysqlSpecification>(relaxed = true) {
            every { host } returns "localhost"
            every { port } returns 3306
            every { database } returns "test_db"
            every { username } returns "user"
            every { password } returns "pass"
            every { ssl } returns true
            every { sslMode } returns SslMode.REQUIRED
            every { jdbcUrlParams } returns params
            every { batchSize } returns 5000
        }

        val config = factory.makeWithoutExceptionHandling(spec)
        assertEquals(params, config.jdbcUrlParams)
    }

    // ========== Custom Port Tests ==========

    @Test
    fun testMakeWithCustomPort() {
        val spec = mockk<MysqlSpecification>(relaxed = true) {
            every { host } returns "localhost"
            every { port } returns 3307
            every { database } returns "test_db"
            every { username } returns "user"
            every { password } returns "pass"
            every { ssl } returns false
            every { sslMode } returns SslMode.PREFERRED
            every { jdbcUrlParams } returns null
            every { batchSize } returns 5000
        }

        val config = factory.makeWithoutExceptionHandling(spec)
        assertEquals(3307, config.port)
    }

    @Test
    fun testMakeWithHighPortNumber() {
        val spec = mockk<MysqlSpecification>(relaxed = true) {
            every { host } returns "localhost"
            every { port } returns 65535
            every { database } returns "test_db"
            every { username } returns "user"
            every { password } returns "pass"
            every { ssl } returns false
            every { sslMode } returns SslMode.PREFERRED
            every { jdbcUrlParams } returns null
            every { batchSize } returns 5000
        }

        val config = factory.makeWithoutExceptionHandling(spec)
        assertEquals(65535, config.port)
    }

    // ========== Custom Batch Size Tests ==========

    @Test
    fun testMakeWithSmallBatchSize() {
        val spec = mockk<MysqlSpecification>(relaxed = true) {
            every { host } returns "localhost"
            every { port } returns 3306
            every { database } returns "test_db"
            every { username } returns "user"
            every { password } returns "pass"
            every { ssl } returns false
            every { sslMode } returns SslMode.PREFERRED
            every { jdbcUrlParams } returns null
            every { batchSize } returns 100
        }

        val config = factory.makeWithoutExceptionHandling(spec)
        assertEquals(100, config.batchSize)
    }

    @Test
    fun testMakeWithLargeBatchSize() {
        val spec = mockk<MysqlSpecification>(relaxed = true) {
            every { host } returns "localhost"
            every { port } returns 3306
            every { database } returns "test_db"
            every { username } returns "user"
            every { password } returns "pass"
            every { ssl } returns false
            every { sslMode } returns SslMode.PREFERRED
            every { jdbcUrlParams } returns null
            every { batchSize } returns 50000
        }

        val config = factory.makeWithoutExceptionHandling(spec)
        assertEquals(50000, config.batchSize)
    }

    // ========== Special Character Tests ==========

    @Test
    fun testMakeWithSpecialCharactersInPassword() {
        val spec = mockk<MysqlSpecification>(relaxed = true) {
            every { host } returns "localhost"
            every { port } returns 3306
            every { database } returns "test_db"
            every { username } returns "user"
            every { password } returns "p@ssw0rd!#$%"
            every { ssl } returns false
            every { sslMode } returns SslMode.PREFERRED
            every { jdbcUrlParams } returns null
            every { batchSize } returns 5000
        }

        val config = factory.makeWithoutExceptionHandling(spec)
        assertEquals("p@ssw0rd!#$%", config.password)
    }

    @Test
    fun testMakeWithSpecialCharactersInUsername() {
        val spec = mockk<MysqlSpecification>(relaxed = true) {
            every { host } returns "localhost"
            every { port } returns 3306
            every { database } returns "test_db"
            every { username } returns "user@domain.com"
            every { password } returns "pass"
            every { ssl } returns false
            every { sslMode } returns SslMode.PREFERRED
            every { jdbcUrlParams } returns null
            every { batchSize } returns 5000
        }

        val config = factory.makeWithoutExceptionHandling(spec)
        assertEquals("user@domain.com", config.username)
    }

    @Test
    fun testMakeWithHyphenatedDatabaseName() {
        val spec = mockk<MysqlSpecification>(relaxed = true) {
            every { host } returns "localhost"
            every { port } returns 3306
            every { database } returns "test-database-name"
            every { username } returns "user"
            every { password } returns "pass"
            every { ssl } returns false
            every { sslMode } returns SslMode.PREFERRED
            every { jdbcUrlParams } returns null
            every { batchSize } returns 5000
        }

        val config = factory.makeWithoutExceptionHandling(spec)
        assertEquals("test-database-name", config.database)
    }

    @Test
    fun testMakeWithIPv4Host() {
        val spec = mockk<MysqlSpecification>(relaxed = true) {
            every { host } returns "192.168.1.100"
            every { port } returns 3306
            every { database } returns "test_db"
            every { username } returns "user"
            every { password } returns "pass"
            every { ssl } returns false
            every { sslMode } returns SslMode.PREFERRED
            every { jdbcUrlParams } returns null
            every { batchSize } returns 5000
        }

        val config = factory.makeWithoutExceptionHandling(spec)
        assertEquals("192.168.1.100", config.host)
    }

    @Test
    fun testMakeWithFullyQualifiedDomainName() {
        val spec = mockk<MysqlSpecification>(relaxed = true) {
            every { host } returns "mysql.example.com"
            every { port } returns 3306
            every { database } returns "test_db"
            every { username } returns "user"
            every { password } returns "pass"
            every { ssl } returns false
            every { sslMode } returns SslMode.PREFERRED
            every { jdbcUrlParams } returns null
            every { batchSize } returns 5000
        }

        val config = factory.makeWithoutExceptionHandling(spec)
        assertEquals("mysql.example.com", config.host)
    }

    // ========== Edge Cases ==========

    @Test
    fun testMakeWithEmptyStringValues() {
        val spec = mockk<MysqlSpecification>(relaxed = true) {
            every { host } returns ""
            every { port } returns 3306
            every { database } returns ""
            every { username } returns ""
            every { password } returns ""
            every { ssl } returns false
            every { sslMode } returns SslMode.PREFERRED
            every { jdbcUrlParams } returns null
            every { batchSize } returns 5000
        }

        val config = factory.makeWithoutExceptionHandling(spec)
        assertEquals("", config.host)
        assertEquals("", config.database)
        assertEquals("", config.username)
        assertEquals("", config.password)
    }

    @Test
    fun testMakeWithMinimumBatchSize() {
        val spec = mockk<MysqlSpecification>(relaxed = true) {
            every { host } returns "localhost"
            every { port } returns 3306
            every { database } returns "test_db"
            every { username } returns "user"
            every { password } returns "pass"
            every { ssl } returns false
            every { sslMode } returns SslMode.PREFERRED
            every { jdbcUrlParams } returns null
            every { batchSize } returns 1
        }

        val config = factory.makeWithoutExceptionHandling(spec)
        assertEquals(1, config.batchSize)
    }
}
