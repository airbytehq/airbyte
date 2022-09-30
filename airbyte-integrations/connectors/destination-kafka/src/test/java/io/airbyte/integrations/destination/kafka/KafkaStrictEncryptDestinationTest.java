package io.airbyte.integrations.destination.kafka;

import static org.junit.jupiter.api.Assertions.*;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.ConnectorSpecification;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KafkaStrictEncryptDestinationTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(KafkaStrictEncryptDestinationTest.class);

  @Test
  void testGetSpec() throws Exception {
    LOGGER.info("spec was {}", new KafkaStrictEncryptDestination().spec().getConnectionSpecification());
    assertEquals(Jsons.deserialize(MoreResources.readResource("expected_strict_encrypt_spec.json"), ConnectorSpecification.class),
        new KafkaStrictEncryptDestination().spec());
  }

  @Test
  void check_should_failOnInsecureConfig() throws Exception {
    ObjectMapper mapper = new ObjectMapper();
    AirbyteConnectionStatus checkResult = new KafkaStrictEncryptDestination().check(mapper.readTree(
        """
            {
              "bootstrap_servers": "PLAINTEXT://localhost:56789,SSL://localhost:67890"
            }
            """
    ));
    LOGGER.info("Check result was {}", checkResult);
    assertEquals(Status.FAILED, checkResult.getStatus());
    assertEquals("Unsecured connection to bootstrap servers is not allowed. These servers specify an insecure connection protocol: [PLAINTEXT://localhost:56789]", checkResult.getMessage());
  }

  @Test
  void check_should_attemptConnectionWithSslConfig() throws Exception {
    ObjectMapper mapper = new ObjectMapper();
    // Run check on an incomplete config with SSL enabled.
    // The check method currently only does anything if there's a test_topic property, so this is expected to succeed.
    AirbyteConnectionStatus checkResult = new KafkaStrictEncryptDestination().check(mapper.readTree(
        """
            {
              "bootstrap_servers": "SSL://localhost:67890,localhost:78901"
            }
            """
    ));
    LOGGER.info("Check result was {}", checkResult);
    assertEquals(Status.SUCCEEDED, checkResult.getStatus());
  }
}
