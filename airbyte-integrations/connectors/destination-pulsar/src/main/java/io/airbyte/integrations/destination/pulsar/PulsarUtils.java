/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.pulsar;

import java.util.Map;
import org.apache.pulsar.client.api.Producer;
import org.apache.pulsar.client.api.PulsarClient;
import org.apache.pulsar.client.api.PulsarClientException;
import org.apache.pulsar.client.api.Schema;
import org.apache.pulsar.client.api.schema.GenericRecord;

class PulsarUtils {

  static PulsarClient buildClient(final String serviceUrl) {
    try {
      return PulsarClient.builder()
          .serviceUrl(serviceUrl)
          .build();
    } catch (PulsarClientException e) {
      throw new RuntimeException("Error creating the Pulsar client", e);
    }
  }

  static Producer<GenericRecord> buildProducer(final PulsarClient client,
                                               final Schema<GenericRecord> schema,
                                               final Map<String, Object> config,
                                               final String topic) {
    try {
      return client.newProducer(schema)
          .loadConf(config)
          .topic(topic)
          .create();
    } catch (PulsarClientException e) {
      throw new RuntimeException("Error creating the Pulsar producer", e);
    }
  }

}
