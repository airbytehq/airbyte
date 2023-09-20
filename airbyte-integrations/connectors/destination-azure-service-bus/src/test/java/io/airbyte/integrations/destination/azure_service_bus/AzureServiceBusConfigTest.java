package io.airbyte.integrations.destination.azure_service_bus;

import static io.airbyte.integrations.destination.azure_service_bus.AzureServiceBusConfig.CONFIG_ENDPOINT_URL_OVERRIDE;
import static io.airbyte.integrations.destination.azure_service_bus.auth.AzureConnectionStringTest.getVanillaConnect;
import static org.assertj.core.api.Assertions.assertThat;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.util.Map;
import okhttp3.HttpUrl;
import org.junit.jupiter.api.Test;

class AzureServiceBusConfigTest {

  @Test
  void parseHeaderMapConfig() {
    Map<String, String> result = AzureServiceBusConfig.parseHeaderMapConfig("foo=bar;meaning=42");
    assertThat(result)
        .as("splits string into key value pairs")
        .containsExactlyInAnyOrderEntriesOf(Map.of("foo", "bar", "meaning", "42"));
  }


  @Test
  void determineQueueName() {
    assertThat(AzureServiceBusConfig.determineQueueName(getVanillaConnect(), ""))
        .as("no queue name check connect string")
        .contains("bar-queue-name");

    assertThat(AzureServiceBusConfig.determineQueueName(getVanillaConnect(), "my-queue-name"))
        .as("queue name set to my-queue-name, use this over connect string")
        .contains("my-queue-name");

  }

  @Test
  void createEndpointUrl() {
    ObjectNode rootNode = new ObjectMapper().createObjectNode();
    String urlStr = "https://allow_overide.com:32879/";
    rootNode.put(CONFIG_ENDPOINT_URL_OVERRIDE, urlStr);
    HttpUrl endpointUrl = AzureServiceBusConfig.createEndpointUrl(rootNode, () -> "invalid");
    assertThat(endpointUrl)
        .isEqualTo(HttpUrl.parse(urlStr));
  }
}