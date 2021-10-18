package io.airbyte.integrations.destination.elasticsearch;

import org.apache.http.HttpHost;
import org.apache.http.auth.AuthScope;
import org.apache.http.auth.BasicUserPrincipal;
import org.apache.http.auth.Credentials;
import org.apache.http.client.config.RequestConfig;
import org.apache.http.client.params.HttpClientParamConfig;
import org.apache.http.impl.client.BasicCredentialsProvider;
import org.apache.http.impl.nio.client.HttpAsyncClientBuilder;
import org.elasticsearch.client.RestClientBuilder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.security.Principal;

public class ElasticsearchHttpClientConfigCallback implements RestClientBuilder.HttpClientConfigCallback {

    private static final Logger log = LoggerFactory.getLogger(ElasticsearchHttpClientConfigCallback.class);

    ConnectorConfiguration config;

    ElasticsearchHttpClientConfigCallback(ConnectorConfiguration config) {
        this.config = config;
    }

    @Override
    public HttpAsyncClientBuilder customizeHttpClient(HttpAsyncClientBuilder httpClientBuilder) {

        if (config.isUsingBasicAuth()) {
            // Configure basic auth
            var httpHost = HttpHost.create(config.getEndpoint());
            var authScope = new AuthScope(httpHost.getHostName(), httpHost.getPort());
            var credProvider = new BasicCredentialsProvider();
            Credentials creds = new Credentials() {
                @Override
                public Principal getUserPrincipal() {
                    return new BasicUserPrincipal(config.getUsername());
                }

                @Override
                public String getPassword() {
                    return config.getPassword();
                }
            };
            credProvider.setCredentials(authScope, creds);
            httpClientBuilder.setDefaultCredentialsProvider(credProvider);
        }

        return httpClientBuilder;
    }

}
