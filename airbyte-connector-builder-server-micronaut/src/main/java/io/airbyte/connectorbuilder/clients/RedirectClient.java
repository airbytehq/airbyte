package io.airbyte.connectorbuilder.clients;

import io.airbyte.connectorbuilder.controllers.StreamListRequestBody;
import io.airbyte.connectorbuilder.controllers.StreamReadRequestBody;
import io.micronaut.http.HttpMethod;
import io.micronaut.http.client.HttpClient;
import io.micronaut.http.client.netty.DefaultHttpClient;
import io.micronaut.http.simple.SimpleHttpRequest;

public class RedirectClient {

    final String host = "http://airbyte-connector-builder-server:80";
    private final HttpClient httpClient;

    public RedirectClient() {
        this.httpClient = new DefaultHttpClient();
    }

    public String read(final StreamReadRequestBody body) {
        return httpClient.toBlocking().retrieve(new SimpleHttpRequest<>(HttpMethod.POST, host + "/v1/stream/read", body));
    }

    public String list(final StreamListRequestBody body) {
        return httpClient.toBlocking().retrieve(new SimpleHttpRequest<>(HttpMethod.POST, host + "/v1/streams/list", body));
    }

    public String manifest() {
        return httpClient.toBlocking().retrieve(new SimpleHttpRequest<>(HttpMethod.GET, host + "/v1/manifest_template", null));
    }
}
