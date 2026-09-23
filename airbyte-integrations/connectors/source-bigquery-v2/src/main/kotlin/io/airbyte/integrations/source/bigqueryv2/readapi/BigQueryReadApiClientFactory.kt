/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2.readapi

import com.google.api.gax.core.FixedCredentialsProvider
import com.google.api.gax.rpc.FixedHeaderProvider
import com.google.auth.oauth2.ServiceAccountCredentials
import com.google.cloud.bigquery.storage.v1.BigQueryReadClient
import com.google.cloud.bigquery.storage.v1.BigQueryReadSettings
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.integrations.source.bigqueryv2.BigQueryClientFactory
import io.airbyte.integrations.source.bigqueryv2.BigQuerySourceConfiguration
import java.io.IOException

/**
 * Builds the Storage Read API client from the same service account key as the JDBC connection and
 * the native client. There is no emulator variant: the read path is not used against the emulator
 * (see [BigQuerySourceConfiguration.useStorageReadApi]).
 */
object BigQueryReadApiClientFactory {

    fun create(config: BigQuerySourceConfiguration): BigQueryReadClient {
        val credentials: ServiceAccountCredentials =
            try {
                ServiceAccountCredentials.fromStream(config.credentialsJson.byteInputStream())
            } catch (e: IOException) {
                throw ConfigErrorException(
                    "Unable to parse 'credentials_json' as a service account key: ${e.message}",
                    e,
                )
            }
        val settings: BigQueryReadSettings =
            BigQueryReadSettings.newBuilder()
                .setHeaderProvider(
                    FixedHeaderProvider.create("user-agent", BigQueryClientFactory.USER_AGENT)
                )
                .setCredentialsProvider(FixedCredentialsProvider.create(credentials))
                .build()
        return BigQueryReadClient.create(settings)
    }
}
