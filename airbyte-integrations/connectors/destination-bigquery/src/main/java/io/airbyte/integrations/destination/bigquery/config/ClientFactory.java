package io.airbyte.integrations.destination.bigquery.config;

import com.google.auth.oauth2.GoogleCredentials;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryOptions;
import io.airbyte.integrations.destination.bigquery.BigQueryUtils;
import io.airbyte.integrations.destination.bigquery.config.properties.BigQueryConnectorConfiguration;
import io.micronaut.context.annotation.Factory;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.env.Environment;
import jakarta.inject.Singleton;

import java.io.IOException;

@Factory
public class ClientFactory {

    @Singleton
    @Requires(notEnv = Environment.TEST)
    public BigQuery bigQuery(final BigQueryConnectorConfiguration configuration, final BigQueryUtils bigQueryUtils) throws IOException {
        final String projectId = configuration.getProjectId();

        final BigQueryOptions.Builder bigQueryBuilder = BigQueryOptions.newBuilder();
        final GoogleCredentials credentials = bigQueryUtils.getServiceAccountCredentials(configuration);
        return bigQueryBuilder
                .setProjectId(projectId)
                .setCredentials(credentials)
                .setHeaderProvider(bigQueryUtils.getHeaderProvider())
                .build()
                .getService();
    }
}
