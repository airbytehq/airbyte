/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.check

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.h2.H2TestFixture
import io.micronaut.context.annotation.Property
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

const val Q = "${CHECK_QUERIES_PREFIX}.queries"

@MicronautTest(rebuildContext = true)
class JdbcCheckQueriesTest {

    val h2 = H2TestFixture()

    @Inject lateinit var checkQueries: JdbcCheckQueries

    @Test
    fun testEmpty() {
        val empty = JdbcCheckQueries()
        Assertions.assertDoesNotThrow { h2.createConnection().use { empty.executeAll(it) } }
    }

    @Test
    @Property(name = "$Q[0]", value = "SELECT DATABASE_PATH() FROM DUAL")
    fun testPass() {
        Assertions.assertDoesNotThrow { h2.createConnection().use { checkQueries.executeAll(it) } }
    }

    @Test
    @Property(name = "$Q[0]", value = "SELECT DATABASE_PATH() FROM DUAL")
    @Property(name = "$Q[1]", value = "SELECT H2VERSION() FROM DUAL")
    fun testFail() {
        lateinit var message: String
        Assertions.assertThrows(ConfigErrorException::class.java) {
            try {
                h2.createConnection().use { checkQueries.executeAll(it) }
            } catch (e: Exception) {
                e.message?.let { message = it }
                throw e
            }
        }
        Assertions.assertEquals("H2VERSION(): 2.2.224", message)
    }
}
