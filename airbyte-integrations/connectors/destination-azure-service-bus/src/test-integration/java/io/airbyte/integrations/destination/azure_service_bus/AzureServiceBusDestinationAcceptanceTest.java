/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_service_bus;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import java.io.IOException;
import java.net.URLDecoder;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.stream.IntStream;
import okhttp3.mockwebserver.MockResponse;
import okhttp3.mockwebserver.MockWebServer;
import okhttp3.mockwebserver.RecordedRequest;
import org.apache.commons.lang3.StringUtils;
import org.jetbrains.annotations.NotNull;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AzureServiceBusDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(AzureServiceBusDestinationAcceptanceTest.class);

  private String endpointUrl;
  private MockWebServer webServer;

  private List<JsonNode> recordsSaved;


  @Override
  protected String getImageName() {
    return "airbyte/destination-azure-service-bus:dev";
  }

  @Override
  protected JsonNode getConfig() {
    // generate the configuration JSON file to be used for running the destination during the test
    LOGGER.debug("endpointUrl={}", endpointUrl);
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("service_bus_connection_string", "Endpoint=sb://any.host/;"
            + "SharedAccessKeyName=someKeyName;SharedAccessKey=someKeyValue")
        .put(AzureServiceBusConfig.CONFIG_QUEUE_NAME, "any_queue")
        .put(AzureServiceBusConfig.CONFIG_ENDPOINT_URL_OVERRIDE, endpointUrl)
        .build());
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    // will result in a failed connection check as sign key is missing/invalid
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("service_bus_connection_string", "Endpoint=sb://foo.servicebus.windows.net/;UnknownKey=foo")
        .build());
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv,
      String streamNameIn,
      String namespaceIn,
      JsonNode streamSchema) throws IOException {

    while (recordsSaved.size() < webServer.getRequestCount()) {
      try {

        RecordedRequest recordedRequest = webServer.takeRequest(200, TimeUnit.MILLISECONDS);
        String bodyStr = recordedRequest.getBody().readString(StandardCharsets.UTF_8);
        ObjectNode rootNode = (ObjectNode) Jsons.deserialize(bodyStr);
        rootNode.put(AzureServiceBusDestination.STREAM, recordedRequest.getHeader(AzureServiceBusDestination.STREAM))
            .put(AzureServiceBusDestination.NAMESPACE, recordedRequest.getHeader(AzureServiceBusDestination.NAMESPACE));
        recordsSaved.add(rootNode);
      } catch (InterruptedException e) {
        throw new IOException(e);
      }
    }

    String streamName = StringUtils.trimToEmpty(streamNameIn);
    String namespace = StringUtils.trimToEmpty(namespaceIn);
    List<JsonNode> testResultList = recordsSaved.stream()
        .filter(rootNode -> streamName.equals(URLDecoder.decode(rootNode.path(AzureServiceBusDestination.STREAM).asText(""), StandardCharsets.UTF_8)))
        .filter(rootNode -> namespace.equals(rootNode.path(AzureServiceBusDestination.NAMESPACE).asText("")))
        .map(rootNode -> rootNode.get(JavaBaseConstants.COLUMN_NAME_DATA))
        .toList();
    return testResultList;
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    try {
      webServer.shutdown();
    } catch (IOException e) {
      LOGGER.warn("failed to shutdown mock http server " + e.getMessage());
    }
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv, final HashSet<String> TEST_SCHEMAS) throws Exception {
    webServer = new MockWebServer();
    webServer.setDispatcher(new MockResponseDispatcher());
    recordsSaved = new ArrayList<>();
    endpointUrl = webServer.url("/").toString();
  }

  private static class MockResponseDispatcher extends okhttp3.mockwebserver.Dispatcher {
    private final MockResponse response = new MockResponse()
        .setResponseCode(201)
        .setBody("");

    @NotNull
    @Override
    public MockResponse dispatch(@NotNull RecordedRequest recordedRequest) {
      return response;
    }
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new AdvancedTestDataComparator();
  }

}
