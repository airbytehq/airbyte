/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb;

import io.airbyte.db.mongodb.MongoDatabase;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.standardtest.destination.PerStreamStateMessageTest;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.Map;
import java.util.function.Consumer;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
public class MongodbRecordConsumerTest extends PerStreamStateMessageTest {

  @Mock
  private Map<AirbyteStreamNameNamespacePair, MongodbWriteConfig> writeConfigs;

  @Mock
  private MongoDatabase mongoDatabase;

  @Mock
  private ConfiguredAirbyteCatalog catalog;

  @Mock
  private Consumer<AirbyteMessage> outputRecordCollector;

  @InjectMocks
  private MongodbRecordConsumer mongodbRecordConsumer;

  @Override
  protected Consumer<AirbyteMessage> getMockedConsumer() {
    return outputRecordCollector;
  }

  @Override
  protected FailureTrackingAirbyteMessageConsumer getMessageConsumer() {
    return mongodbRecordConsumer;
  }

}
