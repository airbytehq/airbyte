/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2

import io.airbyte.integrations.destination.mongodb_v2.config.toMongodbCompatibleName
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test

/**
 * Quick smoke tests that don't require MongoDB running.
 * These validate basic functionality and naming rules.
 */
class MongodbSmokeTest {

    @Test
    fun `test MongoDB name compatibility - basic`() {
        assertEquals("test_collection", "test_collection".toMongodbCompatibleName())
        assertEquals("TestCollection", "TestCollection".toMongodbCompatibleName())
    }

    @Test
    fun `test MongoDB name compatibility - removes null characters`() {
        assertEquals("testcollection", "test\u0000collection".toMongodbCompatibleName())
    }

    @Test
    fun `test MongoDB name compatibility - replaces dollars`() {
        assertEquals("_price", "\$price".toMongodbCompatibleName())
        assertEquals("price_usd", "price\$usd".toMongodbCompatibleName())
    }

    @Test
    fun `test MongoDB name compatibility - replaces dots`() {
        assertEquals("user_name", "user.name".toMongodbCompatibleName())
        assertEquals("nested_field_value", "nested.field.value".toMongodbCompatibleName())
    }

    @Test
    fun `test MongoDB name compatibility - system prefix`() {
        // system.collection -> _system_collection (dots get replaced, prefix added)
        assertEquals("_system_collection", "system.collection".toMongodbCompatibleName())
    }

    @Test
    fun `test MongoDB name compatibility - length limit`() {
        val longName = "a".repeat(150)
        val compatible = longName.toMongodbCompatibleName()
        assertEquals(120, compatible.length)
        assertTrue(compatible.startsWith("aaa"))
    }

    @Test
    fun `test MongoDB name compatibility - complex case`() {
        val input = "system.user\$name.field\u0000test"
        // system. prefix detected, then all special chars replaced, then prefix added
        val expected = "_system_user_name_fieldtest"
        assertEquals(expected, input.toMongodbCompatibleName())
    }

    @Test
    fun `test configuration auth type values`() {
        val authTypes = io.airbyte.integrations.destination.mongodb_v2.spec.MongodbConfiguration.AuthType.values()
        assertEquals(2, authTypes.size)

        assertEquals("login/password", io.airbyte.integrations.destination.mongodb_v2.spec.MongodbConfiguration.AuthType.LOGIN_PASSWORD.value)
        assertEquals("none", io.airbyte.integrations.destination.mongodb_v2.spec.MongodbConfiguration.AuthType.NONE.value)
    }

    @Test
    fun `test connector can be instantiated`() {
        // Just verify the main class exists and can be referenced
        assertNotNull(MongodbDestination::class.java)
    }
}
