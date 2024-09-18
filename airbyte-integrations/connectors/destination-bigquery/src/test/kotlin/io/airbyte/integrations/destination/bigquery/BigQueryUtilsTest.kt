/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery

import com.google.common.collect.ImmutableMap
import io.airbyte.commons.json.Jsons.jsonNode
import io.airbyte.integrations.destination.bigquery.BigQueryUtils.getDatasetId
import java.util.stream.Stream
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource
import org.mockito.Mockito.mock

class BigQueryUtilsTest {
    private var configMapBuilder: ImmutableMap.Builder<Any, Any> = mock()

    @BeforeEach
    fun init() {
        configMapBuilder =
            ImmutableMap.builder<Any, Any>()
                .put(BigQueryConsts.CONFIG_CREDS, "test_secret")
                .put(BigQueryConsts.CONFIG_DATASET_LOCATION, "US")
    }

    @ParameterizedTest
    @MethodSource("validBigQueryIdProvider")
    fun testGetDatasetIdSuccess(projectId: String, datasetId: String, expected: String?) {
        val config =
            jsonNode(
                configMapBuilder
                    .put(BigQueryConsts.CONFIG_PROJECT_ID, projectId)
                    .put(BigQueryConsts.CONFIG_DATASET_ID, datasetId)
                    .build()
            )

        val actual = getDatasetId(config)

        Assertions.assertEquals(expected, actual)
    }

    @ParameterizedTest
    @MethodSource("invalidBigQueryIdProvider")
    fun testGetDatasetIdFail(projectId: String, datasetId: String, expected: String?) {
        val config =
            jsonNode(
                configMapBuilder
                    .put(BigQueryConsts.CONFIG_PROJECT_ID, projectId)
                    .put(BigQueryConsts.CONFIG_DATASET_ID, datasetId)
                    .build()
            )

        val exception: Exception =
            Assertions.assertThrows(IllegalArgumentException::class.java) { getDatasetId(config) }

        Assertions.assertEquals(expected, exception.message)
    }

    companion object {
        @JvmStatic
        private fun validBigQueryIdProvider(): Stream<Arguments> {
            return Stream.of(
                Arguments.arguments("my-project", "my_dataset", "my_dataset"),
                Arguments.arguments("my-project", "my-project:my_dataset", "my_dataset")
            )
        }

        @JvmStatic
        private fun invalidBigQueryIdProvider(): Stream<Arguments> {
            return Stream.of(
                Arguments.arguments(
                    "my-project",
                    ":my_dataset",
                    "Project ID included in Dataset ID must match Project ID field's value: Project ID is `my-project`, but you specified `` in Dataset ID"
                ),
                Arguments.arguments(
                    "my-project",
                    "your-project:my_dataset",
                    "Project ID included in Dataset ID must match Project ID field's value: Project ID is `my-project`, but you specified `your-project` in Dataset ID"
                )
            )
        }
    }
}
