/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.helper;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.generated.ConnectionApi;
import io.airbyte.api.client.generated.DestinationApi;
import io.airbyte.api.client.generated.JobsApi;
import io.airbyte.api.client.generated.SourceApi;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.api.client.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.client.model.generated.ConnectionRead;
import io.airbyte.api.client.model.generated.DestinationIdRequestBody;
import io.airbyte.api.client.model.generated.DestinationRead;
import io.airbyte.api.client.model.generated.DestinationUpdate;
import io.airbyte.api.client.model.generated.JobIdRequestBody;
import io.airbyte.api.client.model.generated.JobInfoLightRead;
import io.airbyte.api.client.model.generated.JobRead;
import io.airbyte.api.client.model.generated.SourceIdRequestBody;
import io.airbyte.api.client.model.generated.SourceRead;
import io.airbyte.api.client.model.generated.SourceUpdate;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.Config;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

public class PersistConfigHelperTest {

  private static final Long JOB_ID = 123L;
  private static final UUID CONNECTION_ID = UUID.randomUUID();
  private static final UUID SOURCE_ID = UUID.randomUUID();
  private static final String SOURCE_NAME = "source-stripe";
  private static final UUID DESTINATION_ID = UUID.randomUUID();
  private static final String DESTINATION_NAME = "destination-google-sheets";

  private final AirbyteApiClient airbyteApiClient = mock(AirbyteApiClient.class);
  private final JobsApi mJobsApi = mock(JobsApi.class);
  private final ConnectionApi mConnectionApi = mock(ConnectionApi.class);
  private final SourceApi mSourceApi = mock(SourceApi.class);
  private final DestinationApi mDestinationApi = mock(DestinationApi.class);

  private PersistConfigHelper persistConfigHelper;

  @BeforeEach
  void setUp() throws ApiException {
    when(airbyteApiClient.getJobsApi()).thenReturn(mJobsApi);
    when(airbyteApiClient.getSourceApi()).thenReturn(mSourceApi);
    when(airbyteApiClient.getDestinationApi()).thenReturn(mDestinationApi);
    when(airbyteApiClient.getConnectionApi()).thenReturn(mConnectionApi);

    when(mJobsApi.getJobInfoLight(new JobIdRequestBody()
        .id(JOB_ID))).thenReturn(new JobInfoLightRead()
            .job(new JobRead()
                .configId(CONNECTION_ID.toString())));

    when(mConnectionApi.getConnection(new ConnectionIdRequestBody()
        .connectionId(CONNECTION_ID))).thenReturn(new ConnectionRead()
            .sourceId(SOURCE_ID)
            .destinationId(DESTINATION_ID));

    when(mSourceApi.getSource(new SourceIdRequestBody()
        .sourceId(SOURCE_ID))).thenReturn(new SourceRead()
            .sourceId(SOURCE_ID)
            .name(SOURCE_NAME));

    when(mDestinationApi.getDestination(new DestinationIdRequestBody()
        .destinationId(DESTINATION_ID))).thenReturn(new DestinationRead()
            .destinationId(DESTINATION_ID)
            .name(DESTINATION_NAME));

    persistConfigHelper = new PersistConfigHelper(airbyteApiClient);
  }

  @Test
  void testPersistSourceConfig() throws ApiException {
    final Config newConfiguration = new Config().withAdditionalProperty("key", "new_value");
    final JsonNode configJson = Jsons.jsonNode(newConfiguration.getAdditionalProperties());

    final SourceUpdate expectedSourceUpdate = new SourceUpdate()
        .sourceId(SOURCE_ID)
        .name(SOURCE_NAME)
        .connectionConfiguration(configJson);

    when(mSourceApi.updateSource(Mockito.any())).thenReturn(new SourceRead().connectionConfiguration(configJson));

    persistConfigHelper.persistSourceConfig(JOB_ID, newConfiguration);
    verify(mSourceApi).updateSource(expectedSourceUpdate);
  }

  @Test
  void testPersistDestinationConfig() throws ApiException {
    final Config newConfiguration = new Config().withAdditionalProperty("key", "new_value");
    final JsonNode configJson = Jsons.jsonNode(newConfiguration.getAdditionalProperties());

    final DestinationUpdate expectedDestinationUpdate = new DestinationUpdate()
        .destinationId(DESTINATION_ID)
        .name(DESTINATION_NAME)
        .connectionConfiguration(configJson);

    when(mDestinationApi.updateDestination(Mockito.any())).thenReturn(new DestinationRead().connectionConfiguration(configJson));

    persistConfigHelper.persistDestinationConfig(JOB_ID, newConfiguration);
    verify(mDestinationApi).updateDestination(expectedDestinationUpdate);
  }

}
