/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.load.command.aws.AwsAssumeRoleCredentials
import io.airbyte.cdk.load.command.aws.AwsEnvVarConstants
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.integrations.destination.s3_data_lake.io.S3DataLakeUtil
import java.nio.file.Files
import java.nio.file.Path

object S3DataLakeTestUtil {
    val GLUE_CONFIG_PATH: Path = Path.of("secrets/glue.json")
    val GLUE_ASSUME_ROLE_CONFIG_PATH: Path = Path.of("secrets/glue_assume_role.json")
    private val AWS_SECRET_CONFIG_PATH: Path =
        Path.of("secrets/glue_aws_assume_role.json")
    val DREMIO_CONFIG_PATH: Path = Path.of("secrets/dremio_nessie_config.json")

    fun parseConfig(path: Path) =
        getConfig(
            ValidatedJsonUtils.parseOne(S3DataLakeSpecification::class.java, Files.readString(path))
        )

    fun getAwsAssumeRoleCredentials(): AwsAssumeRoleCredentials {
        val creds = getAwsAssumeRoleCredentialsAsMap()
        return AwsAssumeRoleCredentials(
            creds[AwsEnvVarConstants.ASSUME_ROLE_ACCESS_KEY.environmentVariable]!!,
            creds[AwsEnvVarConstants.ASSUME_ROLE_SECRET_KEY.environmentVariable]!!,
            creds[AwsEnvVarConstants.ASSUME_ROLE_EXTERNAL_ID.environmentVariable]!!,
        )
    }

    fun getAwsAssumeRoleCredentialsAsMap(): Map<String, String> {
        val parsedAssumeRoleCreds =
            Jsons.readTree(Files.readString(AWS_SECRET_CONFIG_PATH)) as ObjectNode
        return parsedAssumeRoleCreds.properties().associate { it.key to it.value.textValue() }
    }

    fun getConfig(spec: ConfigurationSpecification) =
        S3DataLakeConfigurationFactory()
            .makeWithoutExceptionHandling(spec as S3DataLakeSpecification)

    fun getCatalog(
        config: S3DataLakeConfiguration,
        awsAssumeRoleCredentials: AwsAssumeRoleCredentials
    ) =
        S3DataLakeUtil(SimpleTableIdGenerator(), awsAssumeRoleCredentials).let { icebergUtil ->
            val props = icebergUtil.toCatalogProperties(config)
            icebergUtil.createCatalog(DEFAULT_CATALOG_NAME, props)
        }
}
