/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kafka;

import com.github.dockerjava.api.command.InspectContainerResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import org.apache.commons.io.IOUtils;
import org.testcontainers.containers.BindMode;
import org.testcontainers.containers.KafkaContainer;
import org.testcontainers.images.builder.Transferable;
import org.testcontainers.utility.DockerImageName;

/**
 * A KafkaContainer which accepts SSL connections.
 */
public class SslKafkaContainer extends KafkaContainer {

  // This constant is copied from the superclass, since it's not exposed as public/protected :(
  private static final String STARTER_SCRIPT = "/testcontainers_start.sh";

  public SslKafkaContainer(DockerImageName image) {
    super(image);
    // We need create_certs.sh to generate the broker certs + producer truststore
    withClasspathResourceMapping("kafka_ssl", "/etc/airbyte_setup", BindMode.READ_ONLY);
    // Increase timeout because the cert generation takes about a minute
    withStartupTimeout(Duration.ofMinutes(5));
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

  @Override
  protected void containerIsStarting(InspectContainerResponse containerInfo, boolean reused) {
    // This will create a file at the STARTER_SCRIPT path, which we'll attempt to modify.
    super.containerIsStarting(containerInfo, reused);
    if (reused) {
      return;
    }

    String scriptContents = copyFileFromContainer(STARTER_SCRIPT, is -> IOUtils.toString(is, StandardCharsets.UTF_8));
    scriptContents = """
                     #!/bin/bash
                     mkdir -p /etc/kafka/secrets
                     cd /etc/kafka/secrets
                     cp /etc/airbyte_setup/create_certs.sh .
                     ./create_certs.sh
                     cd -

                     """ + scriptContents;

    copyFileToContainer(
        Transferable.of(scriptContents.getBytes(StandardCharsets.UTF_8), 0777),
        STARTER_SCRIPT);
  }

}
