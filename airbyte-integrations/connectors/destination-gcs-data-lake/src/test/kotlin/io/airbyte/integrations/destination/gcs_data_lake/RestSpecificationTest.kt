/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.gcs_data_lake

import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.load.command.iceberg.parquet.TimeColumnType
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeSpecification
import java.io.File
import org.assertj.core.api.Assertions.assertThat
import org.assertj.core.api.Assertions.assertThatThrownBy
import org.junit.jupiter.api.Test

class RestSpecificationTest {
    @Test
    fun `time option defaults to TIME and accepts STRING`() {
        assertThat(Jsons.readValue("{}", GcsDataLakeSpecification::class.java).timeColumnType)
            .isEqualTo(TimeColumnType.TIME)
        assertThat(
                Jsons.readValue(
                        """{"time_column_type":"STRING"}""",
                        GcsDataLakeSpecification::class.java,
                    )
                    .timeColumnType,
            )
            .isEqualTo(TimeColumnType.STRING)
        assertThatThrownBy {
                Jsons.readValue(
                    """{"time_column_type":"INVALID"}""",
                    GcsDataLakeSpecification::class.java,
                )
            }
            .isInstanceOf(Exception::class.java)
    }

    @Test
    fun `generated REST spec exposes optional authentication and secret fields`() {
        val schema =
            ValidatedJsonUtils.generateAirbyteJsonSchema(GcsDataLakeSpecification::class.java)
        val time = schema["properties"]["time_column_type"]
        assertThat(time["default"].asText()).isEqualTo("TIME")
        assertThat(time["enum"].map { it.asText() }).containsExactly("TIME", "STRING")
        assertThat(schema["required"].map { it.asText() }).doesNotContain("time_column_type")
        val rest =
            schema["properties"]["catalog_type"]["oneOf"].first {
                it["properties"]["catalog_type"]["enum"].any { type -> type.asText() == "REST" }
            }
        for (name in
            listOf(
                "warehouse",
                "token",
                "client_id",
                "client_secret",
                "oauth2_server_uri",
                "scope",
            )) {
            assertThat(rest["properties"].has(name)).isTrue()
            assertThat(rest["required"].map { it.asText() }).doesNotContain(name)
        }
        assertThat(rest["properties"]["token"]["airbyte_secret"].asBoolean()).isTrue()
        assertThat(rest["properties"]["client_secret"]["airbyte_secret"].asBoolean()).isTrue()
        for (environment in listOf("oss", "cloud")) {
            val expected =
                Jsons.readTree(
                        File("src/test-integration/resources/expected-spec-$environment.json"),
                    )["connectionSpecification"]
            assertThat(time).isEqualTo(expected["properties"]["time_column_type"])
            val expectedRest =
                expected["properties"]["catalog_type"]["oneOf"].first {
                    it["properties"]["catalog_type"]["enum"].any { type -> type.asText() == "REST" }
                }
            assertThat(rest).isEqualTo(expectedRest)
        }
    }
}
