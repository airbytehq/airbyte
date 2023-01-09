/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.cassandra;

import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.standardtest.destination.PerStreamStateMessageTest;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
public class CassandraRecordConsumerTest extends PerStreamStateMessageTest {

  @Mock
  private Consumer<AirbyteMessage> outputRecordCollector;

  @InjectMocks
  private CassandraMessageConsumer consumer;
  @Mock
  private CassandraConfig config;
  @Mock
  private ConfiguredAirbyteCatalog catalog;
  @Mock
  private CassandraCqlProvider provider;

  @BeforeEach
  public void init() {
    consumer = new CassandraMessageConsumer(config, catalog, provider, outputRecordCollector);
  }

  @Override
  protected Consumer<AirbyteMessage> getMockedConsumer() {
    return outputRecordCollector;
  }

  @Override
  protected FailureTrackingAirbyteMessageConsumer getMessageConsumer() {
    return consumer;
  }

}
