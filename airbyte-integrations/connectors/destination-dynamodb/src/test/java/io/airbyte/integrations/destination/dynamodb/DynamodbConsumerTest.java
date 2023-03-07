/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dynamodb;

import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.standardtest.destination.PerStreamStateMessageTest;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class DynamodbConsumerTest extends PerStreamStateMessageTest {

  @Mock
  private Consumer<AirbyteMessage> outputRecordCollector;

  @InjectMocks
  private DynamodbConsumer consumer;

  @Mock
  private DynamodbDestinationConfig destinationConfig;

  @Mock
  private ConfiguredAirbyteCatalog catalog;

  @BeforeEach
  private void init() {
    consumer = new DynamodbConsumer(destinationConfig, catalog, outputRecordCollector);
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
