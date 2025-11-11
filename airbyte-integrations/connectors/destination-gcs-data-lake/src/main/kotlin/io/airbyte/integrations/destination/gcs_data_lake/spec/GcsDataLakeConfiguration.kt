/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.spec

import com.google.auth.oauth2.GoogleCredentials
import com.google.auth.oauth2.ServiceAccountCredentials
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import java.io.ByteArrayInputStream

const val DEFAULT_CATALOG_NAME = "airbyte"
const val DEFAULT_STAGING_BRANCH = "airbyte_staging"
const val TEST_TABLE = "airbyte_test_table"

data class GcsDataLakeConfiguration(
    val gcsBucketName: String,
    val serviceAccountJson: String,
    val gcpProjectId: String?,
    val gcpLocation: String,
    val gcsEndpoint: String?,
    val namespace: String,
    val gcsCatalogConfiguration: GcsCatalogConfiguration,
    // Partitioning is enabled, so we can run more than one worker for parallel processing
    override val numProcessRecordsWorkers: Int = 2
) : DestinationConfiguration() {

    // Lazy-loaded credentials from service account JSON with proper OAuth scopes
    val googleCredentials: GoogleCredentials by lazy {
        val credentialsStream = ByteArrayInputStream(serviceAccountJson.toByteArray())
        val baseCredentials = GoogleCredentials.fromStream(credentialsStream)

        // Create scoped credentials for GCS and BigQuery access
        baseCredentials.createScoped(
            listOf(
                "https://www.googleapis.com/auth/cloud-platform", // Full GCP access
                "https://www.googleapis.com/auth/devstorage.read_write", // GCS read/write
                "https://www.googleapis.com/auth/bigquery" // BigQuery/BigLake access
            )
        )
    }

    // Extract project ID - use configured value or extract from service account
    val projectId: String by lazy {
        gcpProjectId
            ?: run {
                val credentials = googleCredentials
                if (credentials is ServiceAccountCredentials) {
                    credentials.projectId
                } else {
                    throw IllegalStateException(
                        "Could not determine GCP project ID from credentials. Please provide gcp_project_id explicitly."
                    )
                }
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
            gcpProjectId = pojo.gcpProjectId,
            gcpLocation = pojo.gcpLocation,
            gcsEndpoint = pojo.gcsEndpoint,
            namespace = pojo.namespace,
            gcsCatalogConfiguration = pojo.toGcsCatalogConfiguration(),
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
