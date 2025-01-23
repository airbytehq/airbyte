/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import com.fasterxml.jackson.core.type.TypeReference
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.integrations.destination.s3_data_lake.io.AWSSystemCredentials
import io.airbyte.integrations.destination.s3_data_lake.io.S3DataLakeUtil
import java.nio.file.Files
import java.nio.file.Path

object S3DataLakeTestUtil {
    val GLUE_CONFIG_PATH: Path = Path.of("secrets/glue.json")
    val GLUE_ASSUME_ROLE_CONFIG_PATH: Path = Path.of("secrets/glue_assume_role.json")
    private val GLUE_AWS_ASSUME_ROLE_CONFIG_PATH: Path =
        Path.of("secrets/glue_aws_assume_role.json")

    fun parseConfig(path: Path) =
        getConfig(
            ValidatedJsonUtils.parseOne(S3DataLakeSpecification::class.java, Files.readString(path))
        )

    fun getAWSSystemCredentials(): AWSSystemCredentials {
        val configFile = GLUE_AWS_ASSUME_ROLE_CONFIG_PATH.toFile()
        return Jsons.readValue(configFile, AWSSystemCredentials::class.java)
    }

    fun getAWSSystemCredentialsAsMap(): Map<String, String> {
        val credentials = getAWSSystemCredentials()
        return Jsons.convertValue(credentials, object : TypeReference<Map<String, String>>() {})
    }

    fun getConfig(spec: ConfigurationSpecification) =
        S3DataLakeConfigurationFactory()
            .makeWithoutExceptionHandling(spec as S3DataLakeSpecification)

    fun getCatalog(config: S3DataLakeConfiguration, awsSystemCredentials: AWSSystemCredentials) =
        S3DataLakeUtil(SimpleTableIdGenerator(), awsSystemCredentials).let { icebergUtil ->
            val props = icebergUtil.toCatalogProperties(config)
            icebergUtil.createCatalog(DEFAULT_CATALOG_NAME, props)
        }
}
