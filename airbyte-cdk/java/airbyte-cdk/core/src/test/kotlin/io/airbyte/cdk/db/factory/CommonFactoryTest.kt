/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.factory

import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.BeforeAll
import org.testcontainers.containers.PostgreSQLContainer

/**
 * Common test suite for the classes found in the `io.airbyte.cdk.db.factory` package.
 */
internal open class CommonFactoryTest {
    companion object {
        private const val DATABASE_NAME = "airbyte_test_database"

        protected var container: PostgreSQLContainer<*>? = null

        @BeforeAll
        fun dbSetup() {
            container = PostgreSQLContainer<SELF>("postgres:13-alpine")
                    .withDatabaseName(DATABASE_NAME)
                    .withUsername("docker")
                    .withPassword("docker")
            container!!.start()
        }

        @AfterAll
        fun dbDown() {
            container!!.close()
        }
    }
}
