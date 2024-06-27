/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.factory

import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.BeforeAll
import org.testcontainers.containers.PostgreSQLContainer

/** Common test suite for the classes found in the `io.airbyte.cdk.db.factory` package. */
internal open class CommonFactoryTest {
    companion object {
        private const val DATABASE_NAME = "airbyte_test_database"

        @JvmStatic
        protected var container: PostgreSQLContainer<*> =
            PostgreSQLContainer<Nothing>("postgres:13-alpine")

        @JvmStatic
        @BeforeAll
        fun dbSetup(): Unit {
            container.withDatabaseName(DATABASE_NAME).withUsername("docker").withPassword("docker")
            container.start()
        }

        @JvmStatic
        @AfterAll
        fun dbDown(): Unit {
            container.close()
        }
    }
}
