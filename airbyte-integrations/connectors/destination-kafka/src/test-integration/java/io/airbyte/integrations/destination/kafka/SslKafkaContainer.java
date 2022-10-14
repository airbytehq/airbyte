package io.airbyte.integrations.destination.kafka;

import org.testcontainers.containers.KafkaContainer;
import org.testcontainers.utility.DockerImageName;

/**
 * A KafkaContainer which accepts SSL connections
 */
public class SslKafkaContainer extends KafkaContainer {

  public SslKafkaContainer(DockerImageName image) {
    super(image);
  }

  /**
   * KafkaContainer hardcodes this to PLAINTEXT://host:port. Override it to use SSL.
   */
  @Override
  public String getBootstrapServers() {
    // Our superclass uses if (port == PORT_NOT_ASSIGNED) for this check.
    // We don't have access to the `port` field, so do a workaround.
    // Probably this check is unnecessary, but keeping it just to be safe.
    if (!this.isRunning()) {
      throw new IllegalStateException("You should start Kafka container first");
    }
    // Again, we don't have direct access to the port field.
    // Fortunately, getMappedPort doesn't mutate state, so we'll just call it directly.
    int port = getMappedPort(KAFKA_PORT);
    return String.format("SSL://%s:%s", getHost(), port);
  }
}
