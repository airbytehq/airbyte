package io.airbyte.integrations.destination.kafka;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import java.util.Set;

public class KafkaStrictEncryptDestination extends KafkaDestination {

  private static final Set<String> SECURE_PROTOCOLS = Set.of(KafkaProtocol.SASL_SSL.name());

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    // TODO after implementing https://github.com/airbytehq/airbyte/issues/17356, check that either SSH tunnel is enabled OR SASL SSL is enabled
    if (!SECURE_PROTOCOLS.contains(config.get("protocol").get("security_protocol").asText())) {
      // Fail immediately if connection is unsecured. We don't run the super.check() because we don't want to send any traffic at all in this case.
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage("Unsecured connection not allowed.");
    }
    return super.check(config);
  }
}
