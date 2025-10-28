/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake

import com.google.auth.oauth2.GoogleCredentials
import com.google.auth.oauth2.ServiceAccountCredentials
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.command.iceberg.parquet.IcebergCatalogConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.IcebergCatalogConfigurationProvider
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import java.io.ByteArrayInputStream

const val DEFAULT_CATALOG_NAME = "airbyte"
const val DEFAULT_STAGING_BRANCH = "airbyte_staging"
const val TEST_TABLE = "airbyte_test_table"

data class GcsDataLakeConfiguration(
    val gcsBucketName: String,
    val serviceAccountJson: String,
    val gcsEndpoint: String?,
    override val icebergCatalogConfiguration: IcebergCatalogConfiguration,
    // Partitioning is enabled, so we can run more than one worker for parallel processing
    override val numProcessRecordsWorkers: Int = 2
) :
    DestinationConfiguration(),
    IcebergCatalogConfigurationProvider {

    // Lazy-loaded credentials from service account JSON
    val googleCredentials: GoogleCredentials by lazy {
        val credentialsStream = ByteArrayInputStream(serviceAccountJson.toByteArray())
        GoogleCredentials.fromStream(credentialsStream)
    }

    // Extract project ID from service account credentials
    val projectId: String? by lazy {
        val credentials = googleCredentials
        if (credentials is ServiceAccountCredentials) {
            credentials.projectId
        } else {
            null
        }
    }
}

@Singleton
class GcsDataLakeConfigurationFactory :
    DestinationConfigurationFactory<GcsDataLakeSpecification, GcsDataLakeConfiguration> {

    override fun makeWithoutExceptionHandling(
        pojo: GcsDataLakeSpecification
    ): GcsDataLakeConfiguration {
        return GcsDataLakeConfiguration(
            gcsBucketName = pojo.gcsBucketName,
            serviceAccountJson = pojo.serviceAccountJson,
            gcsEndpoint = pojo.gcsEndpoint,
            icebergCatalogConfiguration = pojo.toIcebergCatalogConfiguration(),
        )
    }
}

@Factory
class GcsDataLakeConfigurationProvider(private val config: DestinationConfiguration) {
    @Singleton
    fun get(): GcsDataLakeConfiguration {
        return config as GcsDataLakeConfiguration
    }
}
