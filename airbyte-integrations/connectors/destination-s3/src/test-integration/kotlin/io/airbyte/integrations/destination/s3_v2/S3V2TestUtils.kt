/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.load.command.aws.AwsAssumeRoleCredentials
import io.airbyte.cdk.load.util.Jsons
import java.nio.file.Files
import java.nio.file.Path

object S3V2TestUtils {
    const val JSON_UNCOMPRESSED_CONFIG_PATH = "secrets/s3_dest_v2_minimal_required_config.json"
    const val JSON_ROOT_LEVEL_FLATTENING_CONFIG_PATH =
        "secrets/s3_dest_v2_jsonl_root_level_flattening_config.json"
    const val JSON_GZIP_CONFIG_PATH = "secrets/s3_dest_v2_jsonl_gzip_config.json"
    const val JSON_STAGING_CONFIG_PATH = "secrets/s3_dest_v2_jsonl_staging_config.json"
    const val CSV_UNCOMPRESSED_CONFIG_PATH = "secrets/s3_dest_v2_csv_config.json"
    const val CSV_ROOT_LEVEL_FLATTENING_CONFIG_PATH =
        "secrets/s3_dest_v2_csv_root_level_flattening_config.json"
    const val CSV_GZIP_CONFIG_PATH = "secrets/s3_dest_v2_csv_gzip_config.json"
    const val AVRO_UNCOMPRESSED_CONFIG_PATH = "secrets/s3_dest_v2_avro_config.json"
    const val AVRO_BZIP2_CONFIG_PATH = "secrets/s3_dest_v2_avro_bzip2_config.json"
    const val PARQUET_UNCOMPRESSED_CONFIG_PATH = "secrets/s3_dest_v2_parquet_config.json"
    const val PARQUET_SNAPPY_CONFIG_PATH = "secrets/s3_dest_v2_parquet_snappy_config.json"
    const val ENDPOINT_URL_CONFIG_PATH = "secrets/s3_dest_v2_endpoint_url_config.json"
    const val ENDPOINT_EMPTY_URL_CONFIG_PATH = "secrets/s3_dest_v2_endpoint_empty_url_config.json"
    const val AMBIGUOUS_FILEPATH_CONFIG_PATH = "secrets/s3_dest_v2_ambiguous_filepath_config.json"

    // Note that this config uses the airbyte-integration-test-destination-s3 bucket instead of
    // airbyte-johnny-test - this is because the assumed role doesn't have permission to access
    // airbyte-johnny-test.
    // We should eventually move all the configs to use airbyte-integration-test-destination-s3,
    // if only to avoid confusing some hapless new hire about why johnny's bucket is so important.
    const val CSV_ASSUME_ROLE_CONFIG_PATH = "secrets/s3_dest_v2_csv_assume_role_config.json"
    val assumeRoleCredentials: AwsAssumeRoleCredentials

    fun getConfig(configPath: String): String = Files.readString(Path.of(configPath))

    private const val ASSUME_ROLE_INTERNAL_CREDENTIALS_SECRET_PATH =
        "secrets/s3_dest_iam_role_credentials_for_assume_role_auth.json"
    init {
        val parsedAssumeRoleCreds =
            Jsons.readTree(Files.readString(Path.of(ASSUME_ROLE_INTERNAL_CREDENTIALS_SECRET_PATH)))
        val assumeRoleAccessKey = parsedAssumeRoleCreds["AWS_ACCESS_KEY_ID"].textValue()
        val assumeRoleSecretKey = parsedAssumeRoleCreds["AWS_SECRET_ACCESS_KEY"].textValue()
        val assumeRoleExternalId = parsedAssumeRoleCreds["AWS_ASSUME_ROLE_EXTERNAL_ID"].textValue()
        assumeRoleCredentials =
            AwsAssumeRoleCredentials(
                assumeRoleAccessKey,
                assumeRoleSecretKey,
                assumeRoleExternalId,
            )
    }
}
