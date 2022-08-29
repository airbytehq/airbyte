/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage;

import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.destination.azure_blob_storage.writer.AzureBlobStorageWriterFactory;
import io.airbyte.integrations.standardtest.destination.PerStreamStateMessageTest;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@DisplayName("AzureBlobRecordConsumer")
@ExtendWith(MockitoExtension.class)
public class AzureBlobRecordConsumerTest extends PerStreamStateMessageTest {

  @Mock
  private Consumer<AirbyteMessage> outputRecordCollector;

  private AzureBlobStorageConsumer consumer;

  @Mock
  private AzureBlobStorageDestinationConfig azureBlobStorageDestinationConfig;

  @Mock
  private ConfiguredAirbyteCatalog configuredCatalog;

  @Mock
  private AzureBlobStorageWriterFactory writerFactory;

  @BeforeEach
  public void init() {
    consumer = new AzureBlobStorageConsumer(azureBlobStorageDestinationConfig, configuredCatalog, writerFactory, outputRecordCollector);
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
