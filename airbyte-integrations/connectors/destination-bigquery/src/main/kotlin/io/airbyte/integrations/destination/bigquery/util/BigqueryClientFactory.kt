/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.util

import com.google.auth.oauth2.GoogleCredentials
import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryOptions
import io.airbyte.integrations.destination.bigquery.BigQueryUtils
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import java.io.ByteArrayInputStream
import java.nio.charset.StandardCharsets

private val logger = KotlinLogging.logger {}

@Factory
class BigqueryClientFactory(private val config: BigqueryConfiguration) {
    @Singleton
    fun make(): BigQuery {
        // Follows this order of resolution:
        // https://cloud.google.com/java/docs/reference/google-auth-library/latest/com.google.auth.oauth2.GoogleCredentials#com_google_auth_oauth2_GoogleCredentials_getApplicationDefault
        val credentials =
            if (config.credentialsJson == null) {
                logger.info {
                    "No service account key json is provided. It is required if you are using Airbyte cloud."
                }
                logger.info { "Using the default service account credential from environment." }
                GoogleCredentials.getApplicationDefault()
            } else {
                // The JSON credential can either be a raw JSON object, or a serialized JSON object.
                GoogleCredentials.fromStream(
                    ByteArrayInputStream(
                        config.credentialsJson.toByteArray(StandardCharsets.UTF_8)
                    ),
                )
            }
        return BigQueryOptions.newBuilder()
            .setProjectId(config.projectId)
            .setCredentials(credentials)
            .setHeaderProvider(BigQueryUtils.headerProvider)
            .build()
            .service
    }
}
