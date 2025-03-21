/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.load.command.aws.AwsAssumeRoleCredentials
import io.airbyte.cdk.load.command.aws.AwsEnvVarConstants
import io.airbyte.cdk.load.toolkits.iceberg.parquet.SimpleTableIdGenerator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.integrations.destination.s3_data_lake.io.S3DataLakeUtil
import java.nio.file.Files
import java.nio.file.Path
import org.apache.iceberg.catalog.Catalog

object S3DataLakeTestUtil {
    val GLUE_CONFIG_PATH: Path = Path.of("secrets/glue.json")
    val GLUE_ASSUME_ROLE_CONFIG_PATH: Path = Path.of("secrets/glue_assume_role.json")
    private val GLUE_AWS_ASSUME_ROLE_CONFIG_PATH: Path =
        Path.of("secrets/glue_aws_assume_role.json")

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
            Jsons.readTree(Files.readString(GLUE_AWS_ASSUME_ROLE_CONFIG_PATH)) as ObjectNode
        return parsedAssumeRoleCreds.properties().associate { it.key to it.value.textValue() }
    }

    fun getConfig(spec: ConfigurationSpecification) =
        S3DataLakeConfigurationFactory()
            .makeWithoutExceptionHandling(spec as S3DataLakeSpecification)

    fun getCatalog(
        config: S3DataLakeConfiguration,
        awsAssumeRoleCredentials: AwsAssumeRoleCredentials
    ): Catalog {
        val icebergUtil = IcebergUtil(SimpleTableIdGenerator())
        val s3DataLakeUtil = S3DataLakeUtil(icebergUtil, awsAssumeRoleCredentials)
        val props = s3DataLakeUtil.toCatalogProperties(config)
        return icebergUtil.createCatalog(DEFAULT_CATALOG_NAME, props)
    }
}
