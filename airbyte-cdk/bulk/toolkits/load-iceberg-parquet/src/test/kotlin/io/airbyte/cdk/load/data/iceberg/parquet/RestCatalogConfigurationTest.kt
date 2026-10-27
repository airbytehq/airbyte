/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.load.data.iceberg.parquet

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.iceberg.parquet.RestCatalogConfiguration
import org.assertj.core.api.Assertions.assertThat
import org.assertj.core.api.Assertions.assertThatThrownBy
import org.junit.jupiter.api.Test

class RestCatalogConfigurationTest {
    @Test
    fun `optional REST properties preserve unauthenticated catalogs`() {
        assertThat(RestCatalogConfiguration("https://catalog", "default").toProperties())
            .containsExactlyEntriesOf(mapOf("uri" to "https://catalog"))
    }

    @Test
    fun `REST authentication modes are mutually exclusive and OAuth requires a pair`() {
        for (config in
            listOf(
                {
                    RestCatalogConfiguration(
                        "https://catalog",
                        "default",
                        token = "token",
                        clientId = "id",
                        clientSecret = "secret",
                    )
                },
                {
                    RestCatalogConfiguration(
                        "https://catalog",
                        "default",
                        token = "token",
                        clientId = "id",
                    )
                },
                { RestCatalogConfiguration("https://catalog", "default", clientId = "id") },
                { RestCatalogConfiguration("https://catalog", "default", clientSecret = "secret") },
            )) {
            assertThatThrownBy { config() }.isInstanceOf(ConfigErrorException::class.java)
        }
    }
}
