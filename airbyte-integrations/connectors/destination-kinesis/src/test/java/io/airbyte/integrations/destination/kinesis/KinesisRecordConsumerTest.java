/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kinesis;

import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.standardtest.destination.PerStreamStateMessageTest;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@DisplayName("KinesisRecordConsumer")
@ExtendWith(MockitoExtension.class)
public class KinesisRecordConsumerTest extends PerStreamStateMessageTest {

  @Mock
  private Consumer<AirbyteMessage> outputRecordCollector;

  @Mock
  private ConfiguredAirbyteCatalog catalog;
  @Mock
  private KinesisStream kinesisStream;

  private KinesisMessageConsumer consumer;

  @BeforeEach
  public void init() {
    consumer = new KinesisMessageConsumer(catalog, kinesisStream, outputRecordCollector);
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
