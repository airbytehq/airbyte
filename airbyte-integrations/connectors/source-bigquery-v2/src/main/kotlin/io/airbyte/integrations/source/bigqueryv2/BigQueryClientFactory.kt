/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2

import com.google.api.gax.rpc.FixedHeaderProvider
import com.google.auth.oauth2.ServiceAccountCredentials
import com.google.cloud.NoCredentials
import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryOptions
import io.airbyte.cdk.ConfigErrorException
import java.io.IOException

/**
 * Builds the native [BigQuery] client used for schema discovery, from the same credentials as the
 * JDBC connection. The JDBC driver's `DatabaseMetaData` flattens STRUCT and ARRAY columns to a
 * single `STRUCT`/`ARRAY` type name; the native `tables.get` response carries the nested fields and
 * the primary key constraints.
 */
object BigQueryClientFactory {
    const val USER_AGENT = "airbyte/source-bigquery-v2 (GPN: Airbyte)"

    fun create(config: BigQuerySourceConfiguration): BigQuery {
        val builder: BigQueryOptions.Builder =
            BigQueryOptions.newBuilder()
                .setProjectId(config.projectId)
                .setHeaderProvider(FixedHeaderProvider.create("user-agent", USER_AGENT))
        if (config.emulatorHost != null) {
            builder.setHost(config.emulatorHost).setCredentials(NoCredentials.getInstance())
        } else {
            val credentials: ServiceAccountCredentials =
                try {
                    ServiceAccountCredentials.fromStream(config.credentialsJson.byteInputStream())
                } catch (e: IOException) {
                    throw ConfigErrorException(
                        "Unable to parse 'credentials_json' as a service account key: ${e.message}",
                        e,
                    )
                }
            builder.setCredentials(credentials)
        }
        return builder.build().service
    }
}
