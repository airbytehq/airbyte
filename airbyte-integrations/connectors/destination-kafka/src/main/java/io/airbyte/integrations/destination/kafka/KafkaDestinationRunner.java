package io.airbyte.integrations.destination.kafka;

import io.airbyte.integrations.base.adaptive.AdaptiveDestinationRunner;

public class KafkaDestinationRunner {

  public static void main(String[] args) throws Exception {
    AdaptiveDestinationRunner.baseOnEnv()
        .withOssDestination(KafkaDestination::new)
        .withCloudDestination(KafkaStrictEncryptDestination::new)
        .run(args);
  }
}
