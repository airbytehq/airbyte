/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake

import io.airbyte.cdk.integrations.base.DestinationConfig
import io.airbyte.commons.json.Jsons.emptyObject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class SnowflakeInternalStagingSqlOperationsTest {
    private var snowflakeStagingSqlOperations: SnowflakeInternalStagingSqlOperations? = null

    @BeforeEach
    fun setup() {
        DestinationConfig.initialize(emptyObject())
        snowflakeStagingSqlOperations =
            SnowflakeInternalStagingSqlOperations(SnowflakeSQLNameTransformer())
    }

    @Test
    fun createStageIfNotExists() {
        val actualCreateStageQuery = snowflakeStagingSqlOperations!!.getCreateStageQuery(STAGE_NAME)
        val expectedCreateStageQuery =
            "CREATE STAGE IF NOT EXISTS " +
                STAGE_NAME +
                " encryption = (type = 'SNOWFLAKE_SSE') copy_options = (on_error='skip_file');"
        Assertions.assertEquals(expectedCreateStageQuery, actualCreateStageQuery)
    }

    @Test
    fun putFileToStage() {
        val expectedQuery =
            "PUT file://" + FILE_PATH + " @" + STAGE_NAME + "/" + STAGE_PATH + " PARALLEL ="
        val actualPutQuery =
            snowflakeStagingSqlOperations!!.getPutQuery(STAGE_NAME, STAGE_PATH, FILE_PATH)
        Assertions.assertTrue(actualPutQuery.startsWith(expectedQuery))
    }

    @Test
    fun listStage() {
        val expectedQuery = "LIST @" + STAGE_NAME + "/" + STAGE_PATH + FILE_PATH + ";"
        val actualListQuery =
            snowflakeStagingSqlOperations!!.getListQuery(STAGE_NAME, STAGE_PATH, FILE_PATH)
        Assertions.assertEquals(expectedQuery, actualListQuery)
    }

    @Test
    fun copyIntoTmpTableFromStage() {
        val expectedQuery =
            """
        COPY INTO "schemaName"."tableName" FROM '@stageName/stagePath/2022/'
        file_format = (
          type = csv
          compression = auto
          field_delimiter = ','
          skip_header = 0
          FIELD_OPTIONALLY_ENCLOSED_BY = '"'
          NULL_IF=('')
          error_on_column_count_mismatch=false
        ) files = ('filename1','filename2');
        """.trimIndent()
        val actualCopyQuery =
            snowflakeStagingSqlOperations!!.getCopyQuery(
                STAGE_NAME,
                STAGE_PATH,
                listOf("filename1", "filename2"),
                "tableName",
                SCHEMA_NAME
            )
        Assertions.assertEquals(expectedQuery, actualCopyQuery)
    }

    @Test
    fun dropStageIfExists() {
        val expectedQuery = "DROP STAGE IF EXISTS " + STAGE_NAME + ";"
        val actualDropQuery = snowflakeStagingSqlOperations!!.getDropQuery(STAGE_NAME)
        Assertions.assertEquals(expectedQuery, actualDropQuery)
    }

    @Test
    fun removeStage() {
        val expectedQuery = "REMOVE @" + STAGE_NAME + ";"
        val actualRemoveQuery = snowflakeStagingSqlOperations!!.getRemoveQuery(STAGE_NAME)
        Assertions.assertEquals(expectedQuery, actualRemoveQuery)
    }

    companion object {
        private const val SCHEMA_NAME = "schemaName"
        private const val STAGE_NAME = "stageName"
        private const val STAGE_PATH = "stagePath/2022/"
        private const val FILE_PATH = "filepath/filename"
    }
}
