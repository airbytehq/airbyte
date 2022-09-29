package io.airbyte.integrations.destination.kafka;

import static org.junit.jupiter.api.Assertions.*;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KafkaStrictEncryptDestinationTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(KafkaStrictEncryptDestinationTest.class);

  @Test
  void check_should_failOnInsecureConfig() throws Exception {
    ObjectMapper mapper = new ObjectMapper();
    AirbyteConnectionStatus checkResult = new KafkaStrictEncryptDestination().check(mapper.readTree(
        """
            {
              "protocol": {
                "security_protocol": "SASL_PLAINTEXT"
              }
            }
            """
    ));
    LOGGER.info("Check result was {}", checkResult);
    assertEquals(Status.FAILED, checkResult.getStatus());
    assertEquals("Unsecured connection not allowed.", checkResult.getMessage());
  }

  @Test
  void check_should_attemptConnectionWithSslConfig() throws Exception {
    ObjectMapper mapper = new ObjectMapper();
    // Run check on an incomplete config with SSL enabled.
    // The check method currently only does anything if there's a test_topic property, so this is expected to succeed.
    AirbyteConnectionStatus checkResult = new KafkaStrictEncryptDestination().check(mapper.readTree(
        """
            {
              "protocol": {
                "security_protocol": "SASL_SSL"
              }
            }
            """
    ));
    LOGGER.info("Check result was {}", checkResult);
    assertEquals(Status.SUCCEEDED, checkResult.getStatus());
  }
}
