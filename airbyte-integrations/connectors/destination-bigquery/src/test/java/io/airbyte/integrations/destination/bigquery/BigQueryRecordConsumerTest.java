/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.destination.bigquery.uploader.AbstractBigQueryUploader;
import io.airbyte.integrations.standardtest.destination.PerStreamStateMessageTest;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import java.util.Map;
import java.util.function.Consumer;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
public class BigQueryRecordConsumerTest extends PerStreamStateMessageTest {

  @Mock
  private Map<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMap;
  @Mock
  private Consumer<AirbyteMessage> outputRecordCollector;

  @InjectMocks
  private BigQueryRecordConsumer bigQueryRecordConsumer;

  @Override
  protected Consumer<AirbyteMessage> getMockedConsumer() {
    return outputRecordCollector;
  }

  @Override
  protected FailureTrackingAirbyteMessageConsumer getMessageConsumer() {
    return bigQueryRecordConsumer;
  }

}
