/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.singlestore;

import io.airbyte.cdk.testutils.ContainerFactory;
import java.io.IOException;
import java.io.UncheckedIOException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.Network;
import org.testcontainers.utility.DockerImageName;

public class SingleStoreContainerFactory extends ContainerFactory<AirbyteSingleStoreTestContainer> {

  private static final Logger LOGGER = LoggerFactory.getLogger(SingleStoreContainerFactory.class);

  @Override
  protected AirbyteSingleStoreTestContainer createNewContainer(DockerImageName imageName) {
    return new AirbyteSingleStoreTestContainer(imageName.asCompatibleSubstituteFor("ghcr.io/singlestore-labs/singlestoredb-dev"));
  }

  /**
   * Create a new network and bind it to the container.
   */
  public void withNetwork(AirbyteSingleStoreTestContainer container) {
    container.withNetwork(Network.newNetwork());
  }

  private static void execInContainer(AirbyteSingleStoreTestContainer container, String... commands) {
    container.start();
    try {
      for (String command : commands) {
        var output = container.execInContainerWithUser("root", "/bin/bash", "-c", command);
        LOGGER.info("Execute command: {}", output);
      }
    } catch (IOException e) {
      throw new UncheckedIOException(e);
    } catch (InterruptedException e) {
      throw new RuntimeException(e);
    }
  }

  /**
   * Generate SSL certificates and enable SSL connections.
   */
  public static void withCert(AirbyteSingleStoreTestContainer container) {
    String[] commands = {"mkdir certs", "/bin/openssl genrsa 2048 > /certs/ca-key.pem",
      "/bin/openssl req -new -x509 -nodes -days 3600 -key /certs/ca-key.pem -out /certs/ca-cert.pem -subj '/C=US/ST=CA/L=San Francisco/O=MemSQL/CN=memsql.ssl.test.ca'",
      "/bin/openssl req -newkey rsa:2048 -nodes -keyout /certs/server-key.pem -out /certs/server-req.pem -subj '/C=US/ST=CA/L=San Francisco/O=MemSQL/CN=memsql.ssl.test.server'",
      "/bin/openssl rsa -in /certs/server-key.pem -out /certs/server-key.pem",
      "/bin/openssl x509 -req -in /certs/server-req.pem -days 3600 -CA /certs/ca-cert.pem -CAkey /certs/ca-key.pem -set_serial 01 -out /certs/server-cert.pem",
      "/bin/openssl verify -CAfile /certs/ca-cert.pem /certs/server-cert.pem",
      "echo -e 'ssl_cert = /certs/server-cert.pem \\nssl_key = /certs/server-key.pem \\nssl_ca = /certs/ca-cert.pem' >> /data/master/memsql.cnf",
      "echo -e 'ssl_cert = /certs/server-cert.pem \\nssl_key = /certs/server-key.pem \\nssl_ca = /certs/ca-cert.pem' >> /data/leaf/memsql.cnf",
      "chown -R memsql /certs", "chmod -R 777 /certs"};
    execInContainer(container, commands);
    container.restart();
  }

}
