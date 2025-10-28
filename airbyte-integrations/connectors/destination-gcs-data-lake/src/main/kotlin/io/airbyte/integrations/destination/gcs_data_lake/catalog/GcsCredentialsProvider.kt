/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.catalog

import com.google.auth.Credentials
import com.google.auth.oauth2.GoogleCredentials
import com.google.auth.oauth2.ServiceAccountCredentials
import java.io.ByteArrayInputStream

const val GCS_CREDENTIALS_JSON = "gcs-credentials-json"

/**
 * Custom credentials provider for Google Cloud that can be instantiated by Iceberg's
 * GoogleAuthManager via reflection.
 *
 * This class allows us to pass service account credentials programmatically to Iceberg
 * without relying on environment variables or file system paths.
 *
 * Similar to GlueCredentialsProvider in S3DataLake destination.
 */
class GcsCredentialsProvider private constructor(private val delegate: GoogleCredentials) :
    Credentials() {

    override fun getAuthenticationType(): String = delegate.authenticationType

    override fun getRequestMetadata(): MutableMap<String, MutableList<String>> =
        delegate.requestMetadata

    override fun getRequestMetadata(uri: java.net.URI?): MutableMap<String, MutableList<String>> =
        delegate.getRequestMetadata(uri)

    override fun hasRequestMetadata(): Boolean = delegate.hasRequestMetadata()

    override fun hasRequestMetadataOnly(): Boolean = delegate.hasRequestMetadataOnly()

    override fun refresh() {
        delegate.refresh()
    }

    companion object {
        /**
         * Factory method called by Iceberg's GoogleAuthManager via reflection.
         * Properties are passed from catalog configuration.
         */
        @JvmStatic
        fun create(properties: Map<String, String>): Credentials {
            val credentialsJson = properties[GCS_CREDENTIALS_JSON]
                ?: throw IllegalArgumentException("Missing required property: $GCS_CREDENTIALS_JSON")

            val credentialsStream = ByteArrayInputStream(credentialsJson.toByteArray())
            val baseCredentials = GoogleCredentials.fromStream(credentialsStream)

            // Create scoped credentials for GCS and BigQuery access
            val scopedCredentials = baseCredentials.createScoped(
                listOf(
                    "https://www.googleapis.com/auth/cloud-platform",  // Full GCP access
                    "https://www.googleapis.com/auth/devstorage.read_write",  // GCS read/write
                    "https://www.googleapis.com/auth/bigquery"  // BigQuery/BigLake access
                )
            )

            return GcsCredentialsProvider(scopedCredentials)
        }
    }
}
