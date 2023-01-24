package io.airbyte.server.apis;

import io.airbyte.commons.server.handlers.*;
import io.micronaut.http.HttpRequest;
import io.micronaut.http.HttpStatus;
import io.micronaut.http.client.HttpClient;
import io.micronaut.http.client.annotation.Client;
import io.micronaut.runtime.server.EmbeddedServer;
import io.micronaut.test.annotation.MockBean;
import jakarta.inject.Inject;
import org.mockito.Mock;

import static org.junit.jupiter.api.Assertions.assertEquals;

public abstract class BaseControllerTest {


    @Mock
    private AttemptHandler attemptHandler;

    @MockBean(AttemptHandler.class)
    AttemptHandler mAttemptHandler() {
        return attemptHandler;
    }

    @Mock
    private ConnectionsHandler connectionsHandler;

    @MockBean(ConnectionsHandler.class)
    ConnectionsHandler mConnectionsHandler() {
        return connectionsHandler;
    }

    @Mock
    private DestinationHandler destinationHandler;

    @MockBean(DestinationHandler.class)
    DestinationHandler mDestinationHandler() {
        return destinationHandler;
    }

    @Mock
    private DestinationDefinitionsHandler destinationDefinitionsHandler;

    @MockBean(DestinationDefinitionsHandler.class)
    DestinationDefinitionsHandler mDestinationDefinitionsHandler() {
        return destinationDefinitionsHandler;
    }

    @Mock
    private HealthCheckHandler healthCheckHandler;

    @Mock
    private JobHistoryHandler jobHistoryHandler;

    @Mock
    private LogsHandler logsHandler;

    @Mock
    private OAuthHandler oAuthHandler;

    @Mock
    private OpenApiConfigHandler openApiConfigHandler;

    @Mock
    private OperationsHandler operationsHandler;

    @Mock
    private SchedulerHandler schedulerHandler;

    @Mock
    private SourceDefinitionsHandler sourceDefinitionsHandler;

    @Mock
    private SourceHandler sourceHandler;

    @Mock
    private StateHandler stateHandler;

    @Mock
    private WebBackendConnectionsHandler webBackendConnectionsHandler;

    @Mock
    private WebBackendGeographiesHandler webBackendGeographiesHandler;

    @Mock
    private WebBackendCheckUpdatesHandler webBackendCheckUpdatesHandler;

    @Mock
    private WorkspacesHandler workspacesHandler;

    @Inject
    EmbeddedServer embeddedServer;

    @Inject
    @Client("/")
    HttpClient client;

    void testEndpointStatus(HttpRequest request, HttpStatus expectedStatus) {
        assertEquals(expectedStatus, client.toBlocking().exchange(request).getStatus());
    }
}
