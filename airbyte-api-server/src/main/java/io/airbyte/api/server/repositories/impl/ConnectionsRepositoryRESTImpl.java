package io.airbyte.api.server.repositories.impl;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.airbyte.api.server.repositories.ConnectionsRepository;
import io.micronaut.data.annotation.Repository;
import io.micronaut.http.MediaType;
import io.micronaut.http.annotation.Body;
import io.micronaut.http.annotation.Get;
import io.micronaut.http.annotation.Post;
import io.micronaut.http.client.annotation.Client;
import io.micronaut.validation.Validated;
import java.util.UUID;
import javax.validation.constraints.NotBlank;
import lombok.extern.slf4j.Slf4j;

class SyncDto {
    String connectionId;

    @JsonProperty("connectionId")
    public String getConnectionId() {
        return connectionId;
    }
}

@Client("config-api")
@Validated
interface SomeServiceClient {

    @Post(value = "/api/v1/connections/sync", consumes = MediaType.APPLICATION_JSON, produces = MediaType.APPLICATION_JSON)
//    @Post(value = "/workspaces/list", processes = "application/json")
    String sync(@Body SyncDto connectionId);

    @Get("/health")
    String healthCheck();
}


@Repository
@Slf4j
public class ConnectionsRepositoryRESTImpl implements ConnectionsRepository {
    final String configServerUrl = "localhost:8080"; // TODO: Use the property

    private final SomeServiceClient client;

    public ConnectionsRepositoryRESTImpl(final SomeServiceClient client) {
        this.client = client;
    }

    @Override
    public void sync(@NotBlank final UUID connection) {

        // POST to Config API
        log.info("test: ConnectionsRepositoryRESTImpl with connection " + connection);
        final var syncDto = new SyncDto();
        syncDto.connectionId = connection.toString();
//        final String object = client.healthCheck();

//       final HttpRequest request = HttpRequest.POST("http://localhost:8000/api/v1/workspaces/list", body);
//        httpClient.toBlocking().retrieve(request, outputType)

        final String res = client.sync(syncDto);
        log.info("response: " + res);
    }

    @Override
    public void reset(final UUID connection) {
        // POST to Config API
    }

}
