/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redis;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.ssh.SshWrappedDestination;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.List;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class RedisDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedisDestination.class);

  public static void main(String[] args) throws Exception {
    LOGGER.info("starting destination: {}", RedisDestination.class);
    final Destination destination = RedisDestination.sshWrappedDestination();
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", RedisDestination.class);
  }

  public static Destination sshWrappedDestination() {
    return new SshWrappedDestination(new RedisDestination(), List.of("host"), List.of("port"));
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    try (RedisCache redisCache = RedisCacheFactory.newInstance(config)) {
      // check connection and write permissions
      redisCache.ping("Connection check");
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
    } catch (Exception e) {
      final String errorMessage = "Could not connect with provided configuration. Error: " + e.getMessage();
      AirbyteTraceMessageUtility.emitConfigErrorTrace(e, errorMessage);
      return new AirbyteConnectionStatus()
          .withMessage(errorMessage)
          .withStatus(AirbyteConnectionStatus.Status.FAILED);
    }

  }

  @Override
  public AirbyteMessageConsumer getConsumer(JsonNode config,
                                            ConfiguredAirbyteCatalog configuredCatalog,
                                            Consumer<AirbyteMessage> outputRecordCollector) {
    return new RedisMessageConsumer(config, configuredCatalog, outputRecordCollector);
  }

}
